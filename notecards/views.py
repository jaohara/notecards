from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Tag, Deck, Card
from .forms import CardForm

def deck_list(request):
    decks = Deck.objects.all()
    return render(request, 'notecards/deck_list.html', {'decks': decks})

def deck_view(request, pk):
    deck = get_object_or_404(Deck, pk=pk)
    cards = Card.objects.filter(deck__title=deck.title)
    form = CardForm()
    test_var = ""

    if request.method == "POST":
        # we should have submitted a form 

        # this shouldn't route back to itself; we should have a separate view for the 
        # addcard action
        test_var ="Success"

    # return to this later, not necessary for first draft
    # tags = Tag.objects.filter()
    return render(request, 'notecards/deck_view.html', {'deck': deck, 
                                                        'cards': cards, 
                                                        'form': form,
                                                        'test_var': test_var})

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

def remove_card_from_deck(request, pk):
    card = get_object_or_404(Card, pk=pk)
    deck = card.deck
    card.delete()
    deck.remove_card()
    return redirect('deck_view', pk=deck.pk)
