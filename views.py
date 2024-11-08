from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import MenuItem,Cart,Order
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from .permissions import *
from rest_framework import status, viewsets
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from decimal import Decimal
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle



@permission_classes([IsAuthenticated,IsManagerOrReadOnly])
class MenuItemView(viewsets.ModelViewSet):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    
@permission_classes([IsAuthenticated,IsManagerOrReadOnly])
class SingleMenuItemView(viewsets.ModelViewSet):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

class ManagerViewSet(viewsets.ViewSet):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    permission_classes = [IsAuthenticated,IsManager]
    
    
    def list(self, request):
        manager_group = Group.objects.get(name='Manager')
        manager_users = manager_group.user_set.all()
        serializer = UserSerializer(manager_users, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    def create(self, request):
        user = get_object_or_404(User, username=request.data['username'])
        managers = Group.objects.get(name="Manager")
        managers.user_set.add(user)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request):
        user = get_object_or_404(User, username=request.data['username'])
        managers = Group.objects.get(name="Manager")
        managers.user_set.remove(user)

        return Response({"message":"delete successful! "}, status=status.HTTP_204_NO_CONTENT)
        

class DeliveryCrewViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated,IsManager]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    
    
    def list(self, request):
        delivery_crew_group = Group.objects.get(name='Delivery Crew')
        delivery_crew_users = delivery_crew_group.user_set.all()
        serializer = UserSerializer(delivery_crew_users, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    def create(self, request):
        user = get_object_or_404(User, username=request.data['username'])
        delivery_crew = Group.objects.get(name="Delivery Crew")
        delivery_crew.user_set.add(user)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request):
        user = get_object_or_404(User, username=request.data['username'])
        delivery_crew = Group.objects.get(name="Delivery Crew")
        delivery_crew.user_set.remove(user)

        return Response({"message":"delete successful! "}, status=status.HTTP_204_NO_CONTENT)


class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    
    def list(self, request):
        carts = Cart.objects.filter(user=request.user) 
        serializer = CartSerializer(carts, many=True)  
        return Response(serializer.data, status=status.HTTP_200_OK)

    
    def create(self, request):
        menuitem = get_object_or_404(MenuItem, title=request.data["title"])
        quantity = request.data['quantity']
        unit_price = menuitem.price
        price = Decimal(quantity) *unit_price


        cart_item = Cart.objects.create(
                user=request.user,
                menuitem=menuitem,
                quantity=quantity,
                unit_price=unit_price,
                price=price
            )

        serializer = CartSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request):
        carts = Cart.objects.filter(user=request.user)
        if not carts.exists():
            raise PermissionDenied("Your cart is already empty.")

        carts.delete()
        return Response({"message":"Your cart has been emptied."}, status=status.HTTP_204_NO_CONTENT)
  
             
class OrderViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    
    def list(self, request):

        if request.user.groups.filter(name='Manager').exists():
            orders = Order.objects.all()
            serializer = OrderSerializer(orders,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
            
        elif request.user.groups.filter(name='Delivery Crew').exists():
            orders = Order.objects.filter(delivery_crew=request.user)
            serializer = OrderSerializer(orders,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK) 
        
        else:
            orders = Order.objects.filter(user=request.user)
            serializer = OrderSerializer(orders,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK) 


    def create(self, request):
        cart_items = Cart.objects.filter(user=request.user)
        order = Order.objects.create(user=request.user, status=False, date=datetime.date.today())
        total_price = 0
        for cart_item in cart_items:
            order_item = OrderItem.objects.create(
                order=order,
                menuitem=cart_item.menuitem,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                price=cart_item.price
            )
            total_price += cart_item.price
        
        order.total = total_price
        order.save()
        cart_items.delete()
        serializer = OrderSerializer(order)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        


            


class OrderManagementViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    
    def retrieve(self, request):
        order_id = request.data.get("orderId")  # Using get() to avoid KeyError
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"message": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        if order.user != request.user:
            return Response({"message": "This order does not belong to you."}, status=status.HTTP_403_FORBIDDEN)
        else:
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
    def update(self, request):
        order_id = request.data.get("orderId")
        order = get_object_or_404(Order, id=order_id)
        
        if request.user.groups.filter(name='Manager').exists():
            if order.status == 0:
                order.status = 1
    
                delivery_crew_id = request.data.get('delivery_crew', None)
                if delivery_crew_id:
                    try:
                        delivery_crew = User.objects.get(pk=delivery_crew_id)
                        order.delivery_crew = delivery_crew
                    except User.DoesNotExist:
                        return Response({"message": "Delivery crew not found"}, status=status.HTTP_400_BAD_REQUEST)
                order.save()
                return Response({"message": "This order is on its way."}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "This order is already out for delivery."}, status=status.HTTP_400_BAD_REQUEST)
            
        if request.user.groups.filter(name='Delivery Crew').exists():
            if order.delivery_crew != request.user:
                return Response({"message": "This order is not assigned to you."}, status=status.HTTP_403_FORBIDDEN)
            else:
                if order.status == 0:
                    order.status = 1
                    order.save()
                    return Response({"message": "Order delivery confirmed."}, status=status.HTTP_200_OK)
                else:
                    order.status = 0
                    order.save()
                    return Response({"message": "Order status updated to out for delivery."}, status=status.HTTP_200_OK)
    
    @permission_classes([IsManager])
    def destroy(self,request):
        order = Order.objects.get(id=request.data["orderId"])
        if not order.exists():
            raise PermissionDenied("order foes not exist.")

        carts.delete()
        return Response({"message":"Order Successfully deleted."}, status=status.HTTP_204_NO_CONTENT)
        
        
             
        
            


                
                
                
                

            
            
            
            

        
    
    
    