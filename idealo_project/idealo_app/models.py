from django.db import models
import uuid


class APIKey(models.Model):
    email = models.EmailField(unique=True)
    subscription_type = models.CharField(max_length=8)
    is_active = models.BooleanField(default=True)
    key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    requests_left = models.IntegerField(default=1000) 
    expiry = models.BigIntegerField(default=None)
