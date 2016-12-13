from django.contrib import admin
from .models import Tag, Deck, Card

# Register your models here.
admin.site.register(Tag)
admin.site.register(Deck)
admin.site.register(Card)