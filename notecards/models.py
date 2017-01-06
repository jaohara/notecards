from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .utils import make_elipsis


class Tag(models.Model):
    word = models.CharField(max_length=30)

    def __str__(self):
        return "Tag: {}".format(self.word)

class Deck(models.Model):
    author = models.ForeignKey('auth.User')
    card_count = models.PositiveIntegerField(default=0)
    created_date = models.DateTimeField(default=timezone.now)
    description = models.TextField(blank=True, default="", max_length=800)
    modified_date = models.DateTimeField(default=timezone.now)
    tags = models.ManyToManyField(Tag, blank=True)
    title = models.CharField(max_length=200)
    permitted_users = models.ManyToManyField(User, blank=True, related_name="editors")

    # should this be called by the Card model on creation or by the view that creates it?
    def add_card(self):
        self.card_count += 1
        self.save()

    def remove_card(self):
        if self.card_count > 0:
            self.card_count -= 1
            self.save()

    def log_modification(self):
        self.modified_date = timezone.now
        self.save()

    def __str__(self):
        return "{}{} - Cards: {}".format(self.title, make_elipsis(self.title), self.card_count)

class Card(models.Model):
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE)
    front = models.TextField()
    back = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)

    """
        Some idea for functionality here - I should have a "position in deck" option
        to preserve some idea of order between the cards in a given deck.

        How would I handle this? I could have an integer for card number stored 
        in the Card model itself, and then when a new one is created we'll do
        the following:

            1. card in question calls add_card to increment deck
            2. card sets its integer id equal to the current card count

        I need to make sure this behavior is secure, as there could easily be a scenario
        where the counts get out of order (calling remove_card? That would completely
        mess with the order)

        You know what? I'm gonna ignore this for now. It's not really necessary for
        functionality. I'm going to leave this for a later version.
    """

    def __str__(self):
        return "{}{} - {}{} in '{}{}'".format(self.front[:25], make_elipsis(self.front), 
                                              self.back[:25], make_elipsis(self.back), 
                                              self.deck.title[:25], make_elipsis(self.deck.title))
"""
    I don't really know how to use this - there's a setting called AUTH_PROFILE_MODEL, but
    it seems that I can't use this setting after I've already created my database schema? 
    I'm keeping this here for now, but it doesn't really have any function.

    This should also have stats, right?
"""
class UserProfile(models.Model):
    user = models.OneToOneField(User)
    # this could probably be extended to allow user uploaded images, but let's keep
    # it simple for now.

    # 1-4 for one of the prefab avatars. They are located in the static directory,
    # named notecards-user-icon-x.png
    avatar = models.PositiveIntegerField(default=1)
