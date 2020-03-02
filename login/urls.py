from django.urls import path
from . import views

app_name='login'

urlpatterns=[
    path('',views.loginview,name='log_in'),
    path('logout/',views.logoutview,name='logout'),
    # path('register/',views.UserFormView.as_view(),name='register'),
    path('frgtPwd/',views.frgtPwd,name='frgtPwd'),
    # # path('register/',views.UserFormView.as_view(),name='register'),
    path('newPwd/',views.newPwd,name='newPwd'),
    path('chngPwd/',views.changePwd,name='chngPwd'),
    path('savenewpwd/',views.savenewpwd,name='savenewpwd'),
]