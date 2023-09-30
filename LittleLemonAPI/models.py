from django.db import models
from django.contrib.auth.models import User
import uuid
import datetime


# Create your models here.
class Category(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=255, db_index=True)

    def __str__(self)-> str:
        return str(self.title)

class MenuItem(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)
    featured = models.BooleanField(db_index=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)

    def __str__(self):
        return self.title
    




class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    cartitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='item')
    quantity = models.SmallIntegerField()
    
    
    def __str__(self):
        return  f'{self.quantity} X  {self.cartitem.title }'
    

    class Meta:
       unique_together = ( 'user','cartitem')

    

    

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    orderitem = models.ManyToManyField(MenuItem)
    status = models.BooleanField(db_index=True)
    ordered_on = models.DateTimeField(db_index=True, auto_created=True)

    def __str__(self):
        return f"Order {self.user} by {self.user.username}"  



