from django.urls import path
from accounts.views import LoginFacebookView, AddAccountFacebookView


app_name = 'accounts'

urlpatterns = [
    path('login_facebook/', LoginFacebookView.as_view(), name='login_facebook'),
    path('add_login_facebook/', AddAccountFacebookView.as_view(), name='add_login_facebook'),
]
