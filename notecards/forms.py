from django import forms
from django.contrib.auth.models import User

from .models import Tag, Deck, Card, Message

class CardForm(forms.ModelForm):

    class Meta:
        model = Card
        fields = ('front', 'back',)

class DeckForm(forms.ModelForm):

    class Meta:
        model = Deck
        fields = ('title',)

class DeckEditForm(forms.ModelForm):

    """
        We're going to have a few more things in the future here - ideally, we'd want 
        the ability to choose tags for the deck as well as set permissions for which
        users can edit the deck. Both of these are working on the model-end, we just 
        need to implement their functionality.

        More importantly, isn't this really redundant? Wouldn't it make more sense 
        to roll this into the DeckForm form, and then choose to only display the
        title field when creating a deck from the deck_list view? 

        This is probably the right solution... but we'll be lazy for now.
    """

    class Meta:
        model = Deck
        fields = ('title', 'description',)

class MessageForm(forms.ModelForm):

    class Meta:
        model = Message
        fields = ('recipient', 'subject', 'message_body')

class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'email', 'password',)
        widgets = {'password': forms.PasswordInput()}

class TagForm(forms.ModelForm):

    class Meta:
        model = Tag
        fields = ('word',)

