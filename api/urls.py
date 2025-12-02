#urls.py in api
from django.urls import path
from . import views

urlpatterns = [

      path("demo/",views.demo,name="demo"),
      path("signup/",views.Signup_user,name="signup"),
      path("login/",views.Login_user,name="login"),
      path("logout/",views.logout,name="logout"),
      path("trains/",views.get_Train,name="train"),
      path("train_id/<int:T_id>/",views.get_Train_id, name="train_id"),
    
      path("profile/",views.profile_view,name="profile"),
      path("update_profile/",views.update_profile,name="update_profile"),
      path("book_ticket/",views.book_ticket,name="book_ticket"),
      path("user_bookings/",views.user_bookings,name="user_bookings"),
      path("download_ticket/<int:booking_id>/", views.download_ticket,name="download_ticket"),



]