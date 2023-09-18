'''
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import APIKey

@receiver(post_save, sender=APIKey)
def api_key_created(sender, instance, created, **kwargs):
    if created:  # ensures that this is a new instance
        send_mail(
            'Your API Key',
            f'Your API Key has been generated: {instance.key}',
            'from@example.com',
            [instance.email],
            fail_silently=False,
        )
'''