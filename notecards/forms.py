from django import forms

from .models import Tag, Deck, Card

class CardForm(forms.ModelForm):

    class Meta:
        model = Card
        fields = ('front', 'back')