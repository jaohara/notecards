from django.conf.urls import url
from . import views

urlpatterns =[
    url(r'^$', views.deck_list, name='deck_list'),
]