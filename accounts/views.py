import json
import facebook

from datetime import datetime
from django.http import JsonResponse
from django.db import transaction

from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User


from .models import UserSocialNetwork
from .utils import get_username


class LoginFacebookView(APIView):
    @transaction.atomic
    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        access_token = data.get('access_token')
        new_user = False

        # Get the user's data of the GraphAPI
        try:
            graph = facebook.GraphAPI(access_token=access_token)
            user_info = graph.get_object(
                id='me',
                fields='first_name, last_name, id, birthday, '
                       'email, picture.type(large)')

        except facebook.GraphAPIError as error:
            return JsonResponse({'error': u'{}'.format(error)}, safe=False)

        # Check the UserSocialNetwork
        try:
            user_facebook = UserSocialNetwork.objects.get(social_id=user_info.get('id'), social_network_id=1)
            user = User.objects.get(id=user_facebook.user_id)
        except UserSocialNetwork.DoesNotExist:

            # Create User
            password = User.objects.make_random_password()
            user = User(first_name=user_info.get('first_name'),
                        last_name=user_info.get('last_name'),
                        email=user_info.get('email') or '{0} without email'.format(user_info.get('last_name')),
                        date_joined=datetime.now(),
                        username=user_info.get('email') or get_username(user_info.get('first_name'),
                                                                        user_info.get('last_name')),
                        is_active=1)
            user.set_password(password)
            user.save()
            new_user = True

            # Create UserSocialNetwork
            UserSocialNetwork.objects.create(social_id=user_info.get('id'),
                                             profile_image=user_info.get('picture')['data']['url'],
                                             first_name=user_info.get('first_name'),
                                             last_name=user_info.get('last_name'),
                                             email=user_info.get('email') or '{0} without email'.format(
                                                 user_info.get('last_name')),
                                             social_network_id=1, user_id=user.id)

        try:
            token = Token.objects.get(user=user).key
            return JsonResponse({'auth_token': token, 'new_user': new_user},
                                safe=False)
        except Exception as error:
            return JsonResponse({'error': u"{}".format(error)}, safe=False)


class AddAccountFacebookView(APIView):
    @transaction.atomic
    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        access_token = data.get('access_token')
        user_id = data.get('user_id')
        add_account = False

        # Check the user
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not match'}, safe=False)
        except Exception as error:
            return JsonResponse({'error': u'{}'.format(error)}, safe=False)

        # Get the user's data of the GraphAPI
        try:
            graph = facebook.GraphAPI(access_token=access_token)
            user_info = graph.get_object(
                id='me',
                fields='first_name, last_name, id, birthday, '
                       'email, picture.type(large)')
        except facebook.GraphAPIError as error:
            return JsonResponse({'error': u'{}'.format(error)}, safe=False)

        try:
            if UserSocialNetwork.objects.filter(social_id=user_info.get('id')).exists():
                return JsonResponse({'error': 'Ya existe cuenta con facebook'})

            UserSocialNetwork.objects.get(social_id=user_info.get('id'),
                                          social_network_id=1,
                                          user_id=user_id)

        except UserSocialNetwork.DoesNotExist:
            add_account = True
            UserSocialNetwork.objects.create(social_id=user_info.get('id'),
                                             profile_image=user_info.get('picture')['data']['url'],
                                             social_network_id=1, user_id=user.id)

        # Return token
        try:
            token = Token.objects.get(user=user).key
            return JsonResponse({'auth_token': token, 'add_account': add_account},
                                safe=False)
        except Exception as error:
            return JsonResponse({'error': u"{}".format(error)}, safe=False)
