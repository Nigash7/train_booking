#urls.py in api
from django.urls import path
from . import views

urlpatterns = [

      path("demo/",views.demo,name="demo"),
      path("signup/",views.Signup_user,name="signup"),
      path("login/",views.Login_user,name="login"),
    # path("profile",views.User_profile,name="profile"),

]