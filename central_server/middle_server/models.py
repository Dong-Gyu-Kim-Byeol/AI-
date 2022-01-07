from django.db import models

# pip install django_multitenant
from django_multitenant.fields import TenantForeignKey
from django_multitenant.models import TenantModel

# Create your models here.
class User(TenantModel):
    id = models.BigAutoField(primary_key=True)
    tenant_id = 'id'

    email = models.EmailField(max_length=200)
    password = models.CharField(max_length=200)
    phone = models.CharField(max_length=11)

class Farm(TenantModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tenant_id = 'user_id'

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=200)

    class Meta(object):
        unique_together = ["id", "user"]

class Raspberry(TenantModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tenant_id = 'user_id'

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=200)

    farm = TenantForeignKey(Farm, on_delete=models.CASCADE)

    class Meta(object):
        unique_together = ["id", "user"]

class Original_image(TenantModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tenant_id = 'user_id'

    id = models.BigAutoField(primary_key=True)
    original_image = models.BinaryField()
    date = models.DateTimeField(auto_now_add=True)
    split_count = models.IntegerField()

    raspberry = TenantForeignKey(Raspberry, on_delete=models.CASCADE)

    class Meta(object):
        unique_together = ["id", "user"]

class Split_image(TenantModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tenant_id = 'user_id'

    id = models.BigAutoField(primary_key=True)
    split_image = models.BinaryField()
    predict_value = models.CharField(max_length=20)

    original_image = TenantForeignKey(Original_image, on_delete=models.CASCADE)

    class Meta(object):
        unique_together = ["id", "user"]


