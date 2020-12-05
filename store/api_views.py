from rest_framework.exceptions import ValidationError
from rest_framework.generics import (ListAPIView, CreateAPIView,
                                     RetrieveUpdateDestroyAPIView, GenericAPIView)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from store.serializers import ProductSerializer, ProductStatSerializer
from store.models import Product

from django.utils import timezone
from django.core.cache import cache


class ProductPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100


class ProductList(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter,)
    filter_fields = ('id',)
    search_fields = ('name', 'description')
    pagination_class = ProductPagination

    def get_queryset(self):
        on_sale = self.request.query_params.get('on_sale', None)
        if on_sale is None:
            return super().get_queryset()
        queryset = self.queryset
        if on_sale.lower() == 'true':
            now = timezone.now()
            return queryset.filter(
                sale_start__lte=now,
                sale_end__gte=now
            )
        return queryset


class ProductCreate(CreateAPIView):
    serializer_class = ProductSerializer

    def create(self, request, *args, **kwargs):
        try:
            price = request.data.get('price')
            if price is not None and float(price) <= 0.0:
                raise ValidationError({'price': 'Must be above $0.00'})
        except ValueError:
            raise ValidationError({'price': 'A valid number is required'})
        return super().create(request, *args, **kwargs)


class ProductRetriveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    lookup_field = 'id'
    serializer_class = ProductSerializer

    def delete(self, request, *args, **kwargs):
        product_id = request.data.get('id')
        response = super().delete(request, *args, **kwargs)
        if response.status_code == 204:
            cache.delete(f'product_data{product_id}')
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        if response.status_code == 200:
            product = response.data
            cache.set(f'product_data{product}', {
                'name': product['name'],
                'description': product['description'],
                'price': product['price'],
            })

        return response


class ProductStats(GenericAPIView):
    lookup_field = 'id'
    serializer_class = ProductStatSerializer
    queryset = Product.objects.all()

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer({
            'stats': {
                '2019-01-01': [5, 10, 15],
                '2019-01-02': [20, 1, 6],
            }
        })
        
        return Response(serializer.data)