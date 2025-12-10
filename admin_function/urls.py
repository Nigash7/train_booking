
from django.urls import path
from . import views

urlpatterns = [
    path("",views.admin_login,name="login"),
    path("adminhome/",views.admin_home,name="adminhome"),
    path("admin/train/edit/<int:id>/", views.edit_train, name="edit_train"),
    path("admin/train/delete/<int:id>/", views.delete_train, name="delete_train"),
    path("admin/train/add/", views.add_train, name="add_train"),
    path("admin/logout/", views.logout_admin, name="logout"),
    path("admin/train/<int:train_id>/stops/", views.train_stops, name="train_stops"),
    path("admin/train/<int:train_id>/stops/add/", views.add_stop, name="add_stop"),
    path("admin/stop/<int:stop_id>/delete/", views.delete_stop, name="delete_stop"),
    path("admin/train/<int:train_id>/toggle/", views.toggle_train_status, name="toggle_train_status"),
    path("admin/reports/", views.reports_home, name="reports_home"),
    path("admin/reports/date/", views.total_collection_by_date, name="total_collection_by_date"),
    path("admin/reports/train/", views.train_collection_by_date, name="train_collection_by_date"),




   
]