from django import forms

from .models import Tag, Deck, Card

class CardForm(forms.ModelForm):

    class Meta:
        model = Card
        fields = ('front', 'back')

class DeckForm(forms.ModelForm):

    class Meta:
        model = Deck
        fields = ('title',)

# should the form to add tags be part of the deck creation form or on the deck_view page?