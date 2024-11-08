from rest_framework import serializers
from .models import MenuItem, Cart, Order
from django.contrib.auth.models import User


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email']
        
        
        
class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ["user" , "menuitem", "quantity", "price" , "unit_price"]
        
        
        
class OrderSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Order
        fields = ['user', 'delivery_crew', 'status', 'date']