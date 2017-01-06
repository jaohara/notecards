from django.conf.urls import url
from . import views

# previous regex (too generic)
# url(r'^(?P<sort_method>(\w+))/sort/(?P<sort_order>\w+)/$', views.deck_list, name='deck_list'),

urlpatterns =[
    url(r'^$', views.deck_list, name='deck_list'),
    url(r'^(?P<sort_method>(author|title|created_date|card_count))/$', 
        views.deck_list, name='deck_list'),
    url(r'^(?P<sort_method>(author|title|created_date|card_count))/sort/(?P<sort_order>(ascending|descending))/$', 
        views.deck_list, name='deck_list'),

    url(r'^accounts/create/$', views.create_user, name='create_user'),
    url(r'^accounts/(?P<pk>\d+)/$', views.user_profile, name='user_profile'),
    url(r'^accounts/(?P<pk>\d+)/stats/$', views.user_stats, name='user_stats'),
    url(r'^accounts/(?P<pk>\d+)/decks/$', views.user_decks, name='user_decks'),
    url(r'^accounts/all/$', views.user_list, name='user_list'),

    url(r'^deck/(?P<pk>\d+)/$', views.deck_view, name='deck_view'),
    url(r'^deck/(?P<pk>\d+)/add/$', views.add_card_to_deck, name='add_card_to_deck'),
    url(r'^deck/(?P<pk>\d+)/remove/$', views.remove_card_from_deck, name='remove_card_from_deck'),
    url(r'^deck/create/$', views.create_deck, name='create_deck'),
    url(r'^deck/(?P<pk>\d+)/delete/$', views.delete_deck, name='delete_deck'),
    url(r'^deck/(?P<pk>\d+)/edit/$', views.edit_deck, name='edit_deck'),
    url(r'^deck/(?P<pk>\d+)/review/card/(?P<card_index>\d+)/$', views.deck_review, name='deck_review'),
    url(r'^deck/(?P<pk>\d+)/quiz/(?P<quiz_index>\d+)/$', views.deck_quiz, name='deck_quiz'),
    url(r'^deck/(?P<pk>\d+)/quiz/(?P<quiz_index>\d+)/answer_choice/(?P<answer_choice>\d+)', views.deck_quiz, name='deck_quiz'),

    #this... probably shouldn't be in a release 
    url(r'^flush/$', views.flush_session, name='flush_session'),

    #nor this... easy way to test 404s
    url(r'^404/$', views.test_404, name='404'),
]