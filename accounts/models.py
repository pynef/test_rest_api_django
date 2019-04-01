"""
Accounts Models
"""
# -*- coding: utf-8 -*-
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from django.core import validators
from django.utils import timezone
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    UserManager
)

from rest_framework.authtoken.models import Token
from .choices import (
    SEX_CHOICES,
    TYPE_DOCUMENT_CHOICES,
    SOCIAL_NETWORK_CHOICES
)


class UsernameId(models.Model):
    username_id = models.AutoField(primary_key=True)


class User(AbstractBaseUser, PermissionsMixin):
    date_joined = models.DateTimeField(('date joined'), default=timezone.now)
    first_name = models.CharField(('first name'), max_length=30)
    last_name = models.CharField(('last name'), max_length=50)
    email = models.EmailField(
        ('email address'),
        unique=True,
        error_messages={
            'unique': ("A user with that email already exists."),
        })

    username = models.CharField(
        ('username'),
        max_length=100,
        unique=True,
        help_text=('Required. 30 characters or fewer. Letters, digits and '
                   '@/./+/-/_ only.'),
        validators=[
            validators.RegexValidator(
                r'^[\w.@+-]+$',
                ('Enter a valid username. '
                 'This value may contain only letters, numbers '
                 'and @/./+/-/_ characters.'), 'invalid'),
        ],
        error_messages={
            'unique': ("A user with that username already exists."),
        })
    is_staff = models.BooleanField(
        ('staff status'),
        default=False,
        help_text=('Designates whether the user can log into this admin '
                   'site.'))
    is_active = models.BooleanField(
        ('active'),
        default=True,
        help_text=('Designates whether this user should be treated as '
                   'active. Unselect this instead of deleting accounts.'))

    salt_password = models.CharField(u'Password with salt password', max_length=255, null=True, blank=True)
    old_password = models.CharField(u'Password with old hash', max_length=128, null=True, blank=True)
    type_register = models.CharField(u'Type register', max_length=15, choices=SOCIAL_NETWORK_CHOICES,
                                     db_index=True, default='correo')
    cellphone = models.CharField(u'Cellphone', max_length=20, blank=True, null=True)
    sex = models.CharField(u'Sex', max_length=1, choices=SEX_CHOICES, db_index=True, null=True)
    country_iso = models.CharField(u'País ISO?', max_length=3, null=True, blank=True)
    picture = models.CharField(u'Picture', max_length=300, blank=True, null=True)
    email_valid = models.BooleanField(u'Email valid', default=False)
    user_banned = models.BooleanField(u'is banned?', default=False)

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        managed = True
        abstract = False
        db_table = 'auth_user'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    biografy = models.TextField(u'Biografry', max_length=300, blank=True, null=True)
    number_document = models.CharField(u'Number document', max_length=15, blank=True, null=True)
    type_document = models.CharField(u'Type document', max_length=1, choices=TYPE_DOCUMENT_CHOICES,
                                     db_index=True, null=True)
    address = models.CharField(u'Address', max_length=150, blank=True, null=True)
    birthday = models.DateField(u'Birthday', null=True, blank=True)


class SocialNetwork(models.Model):
    social_network_id = models.AutoField(primary_key=True)
    social_network = models.CharField(max_length=150)


class UserSocialNetwork(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    social_network = models.CharField(u'Type register', max_length=15, choices=SOCIAL_NETWORK_CHOICES,
                                      db_index=True, default='correo')
    social_id = models.CharField(max_length=200, unique=True, null=True)
    profile_image = models.CharField(max_length=300, blank=True)
    first_name = models.CharField(max_length=130, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(max_length=150, blank=True, null=True)
    birthday = models.DateField(null=True, blank=True)


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


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    Token.objects.get_or_create(user=instance)
