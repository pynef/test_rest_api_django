import json
import facebook

from datetime import datetime
from django.http import JsonResponse
from django.db import transaction

from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from .models import UserSocialNetwork, Profile
from .utils import get_username
from .models import User


class LoginFacebookView(APIView):
    @transaction.atomic
    def post(self, request):
        information = json.loads(request.body.decode('utf-8'))
        access_token = information.get('access_token')
        new_user = False

        # Get the user's data of the GraphAPI
        try:
            graph = facebook.GraphAPI(access_token=access_token)
            data = graph.get_object(id='me', fields='first_name, last_name, id, birthday, email, picture.type(large)')

            facebook_id = data.get('id')
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            birthday = datetime.strptime(data.get('birthday'), "%m/%d/%Y")
            email = data.get('email') or None
            picture = data.get('picture')['data']['url']

        except facebook.GraphAPIError as error:
            return JsonResponse({'error': u'{}'.format(error)}, safe=False)

        # Check the UserSocialNetwork
        try:
            user_facebook = UserSocialNetwork.objects.get(social_id=facebook_id, social_network='facebook')
            user = User.objects.get(id=user_facebook.user_id)

        except UserSocialNetwork.DoesNotExist:

            # Is vaild email
            if not email:
                return JsonResponse({'error': 'Email needed'}, safe=False)

            # Create User
            password = User.objects.make_random_password()
            user = User(first_name=first_name, last_name=last_name, email=email, date_joined=datetime.now(),
                        picture=picture, username=email, is_active=True, email_valid=True, type_register='facebook')
            
            user.set_password(password)
            user.save()
            new_user = True

            # Create UserSocialNetwork
            UserSocialNetwork.objects.create(social_id=facebook_id, profile_image=picture, first_name=first_name,
                                             last_name=last_name, email=email, social_network='facebook',
                                             user_id=user.id, birthday=birthday)

            # Update information in the profile
            Profile.objects.filter(user_id=user.id).update(birthday=birthday)

        try:
            token = Token.objects.get(user=user).key
            return JsonResponse({'auth_token': token, 'new_user': new_user},
                                safe=False)
        except Exception as error:
            return JsonResponse({'error': u"{}".format(error)}, safe=False)


class AddAccountFacebookView(APIView):
    @transaction.atomic
    def post(self, request):
        information = json.loads(request.body.decode('utf-8'))
        access_token = information.get('access_token')
        user_id = information.get('user_id')
        add_account = False

        # Check the user
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not match', 'add_account': add_account}, safe=False)
        except Exception as error:
            return JsonResponse({'error': u'{}'.format(error), 'add_account': add_account}, safe=False)

        # Get the user's data of the GraphAPI
        try:
            graph = facebook.GraphAPI(access_token=access_token)
            data = graph.get_object(id='me', fields='first_name, last_name, id, birthday, email, picture.type(large)')

            facebook_id = data.get('id')
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            birthday = datetime.strptime(data.get('birthday'), "%m/%d/%Y")
            email = data.get('email') or None
            picture = data.get('picture')['data']['url']

        except facebook.GraphAPIError as error:
            return JsonResponse({'error': u'{}'.format(error), 'add_account': add_account}, safe=False)

        try:
            # Is vaild email
            if not email:
                return JsonResponse({'error': 'Email needed', 'add_account': add_account}, safe=False)

            # Verify is exist the social network
            if UserSocialNetwork.objects.filter(social_id=facebook_id).exists():
                return JsonResponse({'error': 'Ya existe cuenta con facebook', 'add_account': add_account})

            UserSocialNetwork.objects.get(social_id=facebook_id, social_network='facebook', user_id=user_id)

        except UserSocialNetwork.DoesNotExist:
            add_account = True
            UserSocialNetwork.objects.create(social_id=facebook_id, social_network='facebook', first_name=first_name,
                                             last_name=last_name, email=email, profile_image=picture, user_id=user.id,
                                             birthday=birthday)

        # Return token
        try:
            token = Token.objects.get(user=user).key
            return JsonResponse({'auth_token': token, 'add_account': add_account}, safe=False)
        except Exception as error:
            return JsonResponse({'error': u"{}".format(error), 'add_account': add_account}, safe=False)
