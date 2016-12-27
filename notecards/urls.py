from django.conf.urls import url
from . import views

urlpatterns =[
    url(r'^$', views.deck_list, name='deck_list'),
    url(r'^deck/(?P<pk>\d+)/$', views.deck_view, name='deck_view'),
    url(r'^deck/(?P<pk>\d+)/add/$', views.add_card_to_deck, name='add_card_to_deck'),
    url(r'^deck/(?P<pk>\d+)/remove/$', views.remove_card_from_deck, name='remove_card_from_deck'),
    url(r'^deck/create/$', views.create_deck, name='create_deck'),
    url(r'^deck/(?P<pk>\d+)/delete/$', views.delete_deck, name='delete_deck'),
    url(r'^deck/(?P<pk>\d+)/review/card/(?P<card_index>\d+)/$', views.deck_review, name='deck_review'),
    url(r'^deck/(?P<pk>\d+)/quiz/(?P<quiz_index>\d+)/$', views.deck_quiz, name='deck_quiz'),
    url(r'^deck/(?P<pk>\d+)/quiz/(?P<quiz_index>\d+)/answer_choice/(?P<answer_choice>\d+)', views.deck_quiz, name='deck_quiz'), 
    url(r'^flush/$', views.flush_session, name='flush_session'),
]