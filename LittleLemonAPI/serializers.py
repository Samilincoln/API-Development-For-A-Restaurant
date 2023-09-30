from rest_framework import serializers
from .models import MenuItem, Category, CartItem, Order
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
import json


class UserSerializer(serializers.ModelSerializer):
    class Meta:
          model = get_user_model()
          fields = ('id', 'username', 'email', 'password')
          extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = get_user_model().objects.create_user(**validated_data)
        return user


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','slug','title']


class MenuItemSerializer(serializers.ModelSerializer):
    #category = CategorySerializer()
    #title = serializers.RelatedField(read_only=True)
    class Meta:
        model = MenuItem
        fields = ['id','title', 'price', 'featured', 'category']

class AddCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model= CartItem
        fields = ['id','user','cartitem','quantity']
        




class CartItemSerializer(serializers.ModelSerializer):
    calculated_price = serializers.SerializerMethodField(method_name='calc_price')
    user = serializers.StringRelatedField(read_only =True)
    cartitem = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all())
    #cartitem = MenuItemSerializer()
    #item_name =  serializers.SerializerMethodField(method_name='product_name')




    class Meta:
        model = CartItem
        fields = ['id','user','cartitem','quantity','calculated_price']
        read_only_fields = ["user"]

   

    def calc_price(self, cartitems=CartItem):
        return cartitems.quantity * cartitems.cartitem.price
    
    def create(self, validated_data):
        user =  self.context['request'].user
        cartitem = validated_data['cartitem']
        quantity = validated_data['quantity']
        cart, created = CartItem.objects.get_or_create(user=user, cartitem=cartitem, defaults={'quantity': quantity} )
        if not created:
            cart.quantity += quantity
            cart.save()

        return cart
    

    
class OrderSerializer(serializers.ModelSerializer):
    orderitem = serializers.PrimaryKeyRelatedField(many=True, queryset=CartItem.objects.all())
    
    class Meta:
        model = Order
        fields = ('id', 'user', 'orderitem', 'ordered_on', 'status')

    def create(self, validated_data):
        items_data = validated_data.pop('orderitem')
        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            order.orderitem.add(item_data)
        return order
    
class OrderItemSerializer(serializers.ModelSerializer):
       order = serializers.PrimaryKeyRelatedField(read_only = True)
       orderitem = serializers.PrimaryKeyRelatedField(read_only = True)
       
       class Meta:
            model = Order
            fields = ['order','orderitem']





