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
    #url(r'^\?search\=(?P<deck_query>)$', views.deck_list, name='deck_list'),

    url(r'^accounts/create/$', views.create_user, name='create_user'),
    url(r'^accounts/(?P<pk>\d+)/$', views.user_profile, name='user_profile'),
    url(r'^accounts/messages/$', views.user_messages, name='user_messages'),
    url(r'^accounts/messages/create/$', views.user_write_message, name='user_write_message'),
    url(r'^accounts/messages/create/(?P<recipient_pk>\d+)/$', views.user_write_message, name='user_write_message'),
    url(r'^accounts/(?P<pk>\d+)/settings/$', views.user_settings, name='user_settings'),
    url(r'^accounts/(?P<pk>\d+)/stats/$', views.user_stats, name='user_stats'),
    url(r'^accounts/(?P<pk>\d+)/decks/$', views.user_decks, name='user_decks'),
    url(r'^accounts/(?P<pk>\d+)/decks/(?P<sort_method>(title|created_date|card_count))/$', 
        views.user_decks, name='user_decks'),
    url(r'^accounts/(?P<pk>\d+)/decks/(?P<sort_method>(title|created_date|card_count))/sort/(?P<sort_order>(ascending|descending))/$', 
        views.user_decks, name='user_decks'),
    url(r'^accounts/$', views.user_list, name='user_list'),
    url(r'^accounts/all/$', views.user_list, name='user_list'),
    url(r'^accounts/all/(?P<sort_method>(username|date_joined))/sort/(?P<sort_order>(ascending|descending))/$',
        views.user_list, name='user_list'),
    url(r'^accounts/all/(?P<sort_method>(username|date_joined))/$', views.user_list, name='user_list'),

    url(r'^deck/(?P<pk>\d+)/$', views.deck_view, name='deck_view'),
    url(r'^deck/(?P<pk>\d+)/add/$', views.add_card_to_deck, name='add_card_to_deck'),
    url(r'^deck/(?P<pk>\d+)/add-tag/$', views.add_tag_to_deck, name='add_tag_to_deck'),
    url(r'^deck/(?P<pk>\d+)/remove-tag/(?P<tag_word>.+)/$', views.remove_tag_from_deck, name='remove_tag_from_deck'),
    url(r'^deck/(?P<pk>\d+)/remove/$', views.remove_card_from_deck, name='remove_card_from_deck'),
    url(r'^deck/create/$', views.create_deck, name='create_deck'),
    url(r'^deck/(?P<pk>\d+)/delete/$', views.delete_deck, name='delete_deck'),
    url(r'^deck/(?P<pk>\d+)/edit/$', views.edit_deck, name='edit_deck'),
    url(r'^deck/card/(?P<pk>\d+)/delete$', views.remove_card_from_deck, name='delete_card'),
    url(r'^deck/(?P<deck_pk>\d+)/card/(?P<card_pk>\d+)/edit$', views.edit_card, name='edit_card'),
    url(r'^deck/(?P<pk>\d+)/review/card/(?P<card_index>\d+)/$', views.deck_review, name='deck_review'),
    url(r'^deck/(?P<deck_pk>\d+)/quiz/$', views.deck_quiz, name='deck_quiz'),
    url(r'^deck/(?P<deck_pk>\d+)/quiz/answer/(?P<answer_choice>\d+)', views.deck_quiz, name='deck_quiz'),

    url(r'^tag/(?P<tag_word>.+)/$', views.tag_deck_list, name='tag_deck_list'),

    #this... probably shouldn't be in a release 
    url(r'^flush/$', views.flush_session, name='flush_session'),

    #nor this... easy way to test 404s
    url(r'^404/$', views.test_404, name='404'),
]