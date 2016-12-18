import random

from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core import serializers
from .models import Tag, Deck, Card
from .forms import CardForm, DeckForm

def deck_list(request):
    decks = Deck.objects.all()
    form = DeckForm()
    return render(request, 'notecards/deck_list.html', {'decks': decks, 'form': form,})

def deck_view(request, pk):
    deck = get_object_or_404(Deck, pk=pk)
    cards = Card.objects.filter(deck__title=deck.title)
    form = CardForm()

    # return to this later, not necessary for first draft
    # tags = Tag.objects.filter()
    return render(request, 'notecards/deck_view.html', {'deck': deck, 
                                                        'cards': cards, 
                                                        'form': form,})

@login_required
def deck_review(request, pk, card_index=0):
    # get the cards from a session object or return none
    card_index = int(card_index)

    
    if 'cards' not in request.session:
        # get the QuerySet of all cards in the deck
        deck = get_object_or_404(Deck, pk=pk)
        card_set = Card.objects.filter(deck__title=deck.title)

        test_card = None
        cards = list()
        #scramble the cards with random.shuffle(x)
        for card in card_set:
            cards.append({'front': card.front, 'back': card.back})
            test_card = card

        random.shuffle(cards)
        request.session['cards'] = cards
    else:
        cards = request.session['cards']



    if card_index >= len(cards):
        # we've reached the end
        if 'cards' in request.session:
            del request.session['cards']
        return redirect('/deck/{}/'.format(pk))

    else:
        front = cards[card_index].get('front')
        back = cards[card_index].get('back')

        # now, we have a shuffled cards sequence and a proper index

        # we'll render our important info, which is the cards deck and card_index
        return render(request, 'notecards/deck_review.html', {'front': front,
                                                              'back': back,
                                                              'card_index': card_index,
                                                              'deck_length': len(cards),})


#@login_required
#def deck_quiz(request, pk):

@login_required
def flush_session(request):
    request.session.flush()
    return redirect('/')

@login_required
def create_deck(request):
    if request.method =="POST":
        form = DeckForm(request.POST)
        if form.is_valid():
            deck = form.save(commit=False)
            deck.author = request.user
            deck.save()
            return redirect('/')
    else:
        return redirect('/')

@login_required
def delete_deck(request, pk):
    deck = get_object_or_404(Deck, pk=pk)
    deck.delete()
    return redirect('/')

@login_required
def add_card_to_deck(request, pk):
    if request.method == "POST":
        deck = get_object_or_404(Deck, pk=pk)
        form = CardForm(request.POST)
        if form.is_valid():
            card = form.save(commit=False)
            card.deck = deck
            card.save()
            deck.add_card()
            return redirect('deck_view', pk=deck.pk)
    else:
        redirect('/')

@login_required
def remove_card_from_deck(request, pk):
    card = get_object_or_404(Card, pk=pk)
    deck = card.deck
    card.delete()
    deck.remove_card()
    return redirect('deck_view', pk=deck.pk)
