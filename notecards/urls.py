from django.conf.urls import url
from . import views

urlpatterns =[
    url(r'^$', views.deck_list, name='deck_list'),
    url(r'^deck/(?P<pk>\d+)/$', views.deck_view, name='deck_view'),
    url(r'^deck/(?P<pk>\d+)/add/$', views.add_card_to_deck, name='add_card_to_deck'),
    url(r'^deck/(?P<pk>\d+)/remove', views.remove_card_from_deck, name='remove_card_from_deck'),
]