from django.contrib import admin
from .models import Card, Deck, Message, QuizResult, Tag, UserProfile

admin.site.register(Card)
admin.site.register(Deck)
admin.site.register(Message)
admin.site.register(QuizResult)
admin.site.register(Tag)
admin.site.register(UserProfile)