from rest_framework import serializers

from store.models import Product, ShoppingCartItem


class CartItemSerilaizer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(min_value=0, max_value=100)

    class Meta:
        model = ShoppingCartItem
        fields = ('product', 'quantity')


class ProductSerializer(serializers.ModelSerializer):
    is_on_sale = serializers.BooleanField(read_only=True)
    current_price = serializers.FloatField(read_only=True)
    description = serializers.CharField(min_length=2, max_length=200)
    cart_items = serializers.SerializerMethodField()
    # price = serializers.FloatField(min_value=1.00, max_value=10000)
    price = serializers.DecimalField(
        min_value=1.00, max_value=10000,
        max_digits=None, decimal_places=2,
    )
    sale_start = serializers.DateTimeField(
        input_formats=['%I:%M %p %d %B %Y'], format=None, allow_null=True,
        help_text='Accepted format is "12:01 PM 16 April 2017"',
        style={'input_type': 'text', 'placeholder': '12:01 AM 28 July 2020'}
    )
    sale_end = serializers.DateTimeField(
        input_formats=['%I:%M %p %d %B %Y'], format=None, allow_null=True,
        help_text='Accepted format is "12:01 PM 16 April 2017"',
        style={'input_type': 'text', 'placeholder': '12:01 AM 28 July 2020'}
    )
    photo = serializers.ImageField(default=None)
    warranty = serializers.FileField(write_only=True, default=None)

    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'price', 'sale_start',
                  'sale_end', 'is_on_sale', 'photo', 'warranty',
                  'current_price', 'cart_items')

    def get_cart_items(self, instance):
        items = ShoppingCartItem.objects.filter(product=instance)
        return CartItemSerilaizer(items, many=True).data

    def update(self, instance, validate_data):
        if validate_data.get('warranty', None):
            instance.description += '\n\nWarranty Information:\n'
            instance.description += b'; '.join(
                validate_data['warranty'].readlines()
            ).decode()
        return instance

class ProductStatSerializer(serializers.Serializer):
    stats = serializers.DictField(
        child=serializers.ListSerializer(
            child=serializers.IntegerField(),
        )
    )
