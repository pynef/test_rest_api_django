"""
Accounts Models
"""
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.db import models

from rest_framework.authtoken.models import Token


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    biografy = models.TextField(max_length=300, blank=True, null=True)
    birthdate = models.DateField(null=True, blank=True)


class SocialNetwork(models.Model):
    social_network_id = models.AutoField(primary_key=True)
    social_network = models.CharField(max_length=150)


class UserSocialNetwork(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    social_network = models.ForeignKey('SocialNetwork', related_name='social_networks', on_delete=models.CASCADE)
    social_id = models.CharField(max_length=200, unique=True, null=True)
    profile_image = models.CharField(max_length=300, blank=True)
    first_name = models.CharField(max_length=130, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(max_length=150, blank=True, null=True)
    birthdate = models.DateField(null=True, blank=True)


class TypeAddress(models.Model):
    type_address_id = models.AutoField(primary_key=True)
    type_address = models.CharField(max_length=150)


class UserTypeAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type_address = models.ForeignKey('TypeAddress', related_name='type_documents', on_delete=models.CASCADE)
    address = models.CharField(max_length=150, null=True, blank=True)
    number = models.IntegerField()
    reference = models.CharField(max_length=150, null=True, blank=True)
    latitud = models.CharField(max_length=150, null=True, blank=True)
    longitud = models.CharField(max_length=150, null=True, blank=True)



@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    Token.objects.get_or_create(user=instance)
