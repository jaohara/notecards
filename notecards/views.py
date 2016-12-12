from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Deck, Card

def deck_list(request):
    decks = Deck.objects.all()
    return render(request, 'notecards/deck_list.html', {'decks': decks})