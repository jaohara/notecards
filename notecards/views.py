from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
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
