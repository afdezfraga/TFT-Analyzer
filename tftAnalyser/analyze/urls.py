
from django.conf.urls import url, include
from analyze import views

urlpatterns = [
    url(r'^top/$', views.top, name='top'),
    url(r'^top/(?P<count>\d+)$', views.ajax_top, name='ajax_top'),
    url(r'^$', views.tft),
    url(r'^(?P<stream_amount>\d+)/$', views.ajax_twitch, name='ajax_twitch'),
    url(r'^units/$', views.units, name='units'),
    url(r'^traits/$', views.traits, name='traits'),
    url(r'^traits/(?P<trait_name>[\w\ ]+)$', views.getGuides, name='traits'),
    url(r'^objects/$', views.objects, name='objects'),
    url(r'^user/(?P<user_name>[\w\ ]+)$', views.users, name='user'),
    url(r'^user/(?P<user_name>[\w\ ]+)/refresh$', views.refresh, name='refresh'),
    url(r'^user/(?P<user_name>[\w\ ]+)/asinc$', views.ajax_users, name='ajax_users'),
]
