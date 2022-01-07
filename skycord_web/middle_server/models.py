from django.db import models

# Create your models here.
from django.db import models

# Create your models here.
class User(models.Model):
    id = models.BigAutoField(primary_key=True,)
    email = models.EmailField(max_length=200, unique=True)
    password = models.CharField(max_length=200)
    phone = models.CharField(max_length=11, unique=True)

class Farm(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

class Raspberry(models.Model):
    id = models.BigAutoField(primary_key=True)
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

class Original_image(models.Model):
    id = models.BigAutoField(primary_key=True)
    raspberry = models.ForeignKey(Raspberry, on_delete=models.CASCADE)
    original_image = models.BinaryField()
    date = models.DateTimeField(auto_now_add=True)
    split_count = models.IntegerField()

class Split_image(models.Model):
    id = models.BigAutoField(primary_key=True)
    original_image = models.ForeignKey(Original_image, on_delete= models.CASCADE)
    split_image = models.BinaryField()
    predict_value = models.CharField(max_length=20)

