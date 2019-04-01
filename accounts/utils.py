# -*- coding: utf-8 -*-
import datetime
from .models import UsernameId
from django.db import transaction


@transaction.atomic
def get_username(firstname, lastname):
    username_id = UsernameId.objects.create()
    if firstname and lastname:
        return u"{}{}{}".format(firstname[0], lastname, username_id.username_id)

    return u"{}{}{}".format(firstname, lastname, username_id.username_id)


def create_email(email, user_id):
    pass
