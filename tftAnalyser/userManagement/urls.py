
from django.conf.urls import url, include
from userManagement import views

urlpatterns = [
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^logout/$', views.logout_view, name='logout_view'),
    url(r'^favorites/$', views.favorites, name='favorites'),
    url(r'^favorites/add/(?P<user_name>[\w\ ]+)$', views.add_favorites, name='add_favorites'),
    url(r'^favorites/delete/(?P<user_name>[\w\ ]+)$', views.delete_favorites, name='delete_favorites'),
]
