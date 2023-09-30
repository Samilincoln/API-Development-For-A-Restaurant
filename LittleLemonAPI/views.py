
from django.shortcuts import get_object_or_404, render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import generics, permissions
from rest_framework.mixins import CreateModelMixin
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from .models import Category, MenuItem, CartItem,  Order
from .serializers import CategorySerializer, MenuItemSerializer, CartItemSerializer, OrderSerializer, OrderItemSerializer #AddCartItemSerializer, ShowCartItemSerializer, OrderItemSerializer, AddOrderItemSerializer'''
from django.contrib.auth.models import User, Group
from django.contrib.auth import get_user_model
import json


def home(request):
    return render(request, 'home.html')


    


class CategoryView(generics.ListCreateAPIView, generics.RetrieveDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    

    

class MenuItemView(generics.ListCreateAPIView, generics.DestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    search_fields = ['title']

    @api_view(['GET','POST'])
    @permission_classes([IsAuthenticated])
    def menu_items(request):
        if request.method =='GET':
            items = MenuItem.objects.select_related('category').all()
            category_name = request.query_params.get('category')
            to_price = request.query_params.get('to_price')
            search = request.query_params.get('to_price')

            if category_name:
                items = items.filter(category__title = category_name)
            if to_price:
                items = items.filter(price__lte= to_price)
            serialized_item = MenuItemSerializer(items, many=True)
            if search :
                items = items.filter(title__istartswith= search)
            return Response(serialized_item.data)
            #return Response({"messsage":"Some secret message for only logged in users"})
        elif request.method == 'POST':
            if request.user.groups.filter(name='Manager').exists():
                serialized_item = MenuItemSerializer(data=request.data)
                serialized_item.is_valid(raise_exception=True)
                serialized_item.save()
                return Response(serialized_item.validated_data,status.HTTP_201_CREATED)
                #return Response({"messsage":"Some secret message for Managers"})
            else:
                return Response({'message': 'You are not authorized'}, 403)


    @api_view(['GET','PUT','DELETE'])
    @permission_classes([IsAuthenticated])
    def single_item(request, pk):
        if request.method == 'GET' :
            item = get_object_or_404(MenuItem,pk=pk)
            serialized_item = MenuItemSerializer(item, many=True)
            return Response(serialized_item.data)
        elif request.method == 'PUT' :
            if request.user.groups.filter(name='Manager').exists():
                item = get_object_or_404(MenuItem,pk=pk)
                serialized_item = MenuItemSerializer(instance=item, data=request.data)
                serialized_item.is_valid(raise_exception=True)
                serialized_item.save()
                return Response(serialized_item.validated_data,status.HTTP_200_OK)
            else:
                return Response({'message': 'You are not authorized'}, 403)
        elif request.method == 'DELETE':
            if request.user.groups.filter(name='Manager').exists():
                item = get_object_or_404(MenuItem,pk=pk)
                #serialized_item = MenuItemSerializer(item)
                #serialized_item.is_valid(raise_exception=True)
                item.delete()
                return Response({'message': 'Deleted Successfully'}, status.HTTP_200_OK)
            else:
                return Response({'message': 'You are not authorized'}, 403)
        elif request.method == 'POST':
            return Response({'message': 'You are not authorized'}, 403)


    

@api_view(['POST','DELETE','GET'])
@permission_classes([IsAdminUser])
def managers(request):
    if request.method == 'GET':
        managers = Group.name = 'Manager'
        
        return Response(managers.username)

    username = request.data['username']
    if username:
        user = get_object_or_404(User,username=username)
        managers = Group.objects.get(name = 'Manager')
        if request.method == 'POST':
            managers.user_set.add(user)
        if request.method == 'DELETE':
            managers.user_set.remove(user)
        return Response({'message':'ok'})
    return Response({'mesage': 'error'}, status.HTTP_400_BAD_REQUEST)






class CartAddAPIView(generics.ListCreateAPIView, generics.DestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        if permission_classes:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            cart = serializer.save()
            return Response(CartItemSerializer(cart).data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)
    

class UserOrderListAPIView(generics.ListCreateAPIView, generics.RetrieveDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def ordersview(request):
        if request.method == 'GET': 
            if request.user.groups.filter(name='Delivery').exists():
                return Response(Order.objects.filter(delivery_crew=request.user),  status.HTTP_200_OK)
            elif request.user.groups.filter(name='Customer').exists():
                return Response(Order.objects.filter(delivery_crew=request.user),  status.HTTP_200_OK)
            elif request.user.groups.filter(name='Manager').exists():
                return Response(Order.objects.all(), status.HTTP_200_OK)
            else:
                return Response({'mesage': 'error'}, status.HTTP_400_BAD_REQUEST)


    def perform_create(self, serializer):
        user_cart = CartItem.objects.filter(user=self.request.user)
        items = [cart.cartitem for cart in user_cart]
        serializer.save(user=self.request.user, orderitem=items)
        user_cart.delete()
        return serializer.data

    
    
    @api_view(['GET', 'DELETE', 'PATCH'])
    def orderitem_view(request,pk):
        try:
            item = get_object_or_404(Order,id=pk)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        if request.method =='GET':
            serialized_item = OrderSerializer(item)
            return Response(serialized_item.data)
        elif request.method =='DELETE':
            item.delete()
            return Response({'message': 'Deleted Successfully'},status.HTTP_200_OK)
        elif request.method =='PATCH':
            serializer = OrderSerializer(instance=item, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
            return Response(serializer.data)


    
   
        


    

api_view(['GET','PUT','PATCH','DELETE'])
@permission_classes([IsAuthenticated])
class CartView(generics.ListCreateAPIView, generics.RetrieveDestroyAPIView):
    queryset = CartItem.objects.all().order_by('user')
    serializer_class = CartItemSerializer

    def cartlist(self):
        return CartItem.objects.filter(user=self.request.user)
        

    @api_view(['GET', 'DELETE'])
    @permission_classes([IsAuthenticated])
    def cartitemview(request,pk):
        
        if request.method =='GET':
            item = get_object_or_404(CartItem,id=pk)
            serialized_item = CartItemSerializer(item)
            return Response(serialized_item.data)
        elif request.method =='DELETE':
            item = get_object_or_404(CartItem,pk=pk)
            item.delete()
            return Response({'message': 'Deleted Successfully'},status.HTTP_200_OK)
                
            
           


