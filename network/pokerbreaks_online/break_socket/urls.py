from django.urls import path

from . import views

urlpatterns = {
    path("", views.index, name="index"),

    # Api section
    # App
    path("breaks", views.update_breaks, name="update_breaks"),
    path("getupdate", views.getupdate, name="getupdate"),
    # Welfare officers
    path("add_break", views.add_break, name="add_break"),
}