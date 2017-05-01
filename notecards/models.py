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
    deck_hits = models.PositiveIntegerField(default=0)
    deck_likes = models.ManyToManyField(User, blank=True, related_name="likers")
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

    def add_tag(self, tag):
        self.tags.add(tag)
        self.save()

    def remove_tag(self, tag):
        self.tags.remove(tag)
        self.save()

    def add_user(self, user):
        self.permitted_users.add(user)
        self.save()

    def remove_user(self, user):
        self.permitted_users.remove(user)
        self.save()

    def hit_deck(self):
        # this is some William Gibson sounding shit.
        # I'd totally name this "punch_deck" if it wasn't nondescript.
        self.deck_hits += 1
        self.save()

    def like(self, user):
        if user in self.deck_likes.all():
            self.deck_likes.remove(user)
        else:
            self.deck_likes.add(user)
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

    def __str__(self):
        return "{}{} - {}{} in '{}{}'".format(self.front[:25], make_elipsis(self.front), 
                                              self.back[:25], make_elipsis(self.back), 
                                              self.deck.title[:25], make_elipsis(self.deck.title))


class UserProfile(models.Model):

    """
        I think the best way to handle creating these is to have a method for creating
        users through the UserProfile model, instead of creating UserProfiles at a later
        date and binding them to the users.

        So, when we create a user, we'd ignore the default functionality and create
        one of these UserProfiles instead, and then there'd be some sort of 
        constructor method or a method that view could call that'd create a
        User with the supplied information and bind it to the 'user' field in its
        instance.

        Yeah. That sounds right.
    """




    user = models.OneToOneField(User)

    bio = models.TextField(max_length=500, blank=True, default="This user hasn't edited their bio yet!")
    birth_date = models.DateTimeField(blank=True, null=True)
    # location = 

    saved_decks = models.ManyToManyField(Deck, blank=True)

    def __str__(self):
        return "UserProfile for '{}'".format(self.user.username)


class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sender")
    recipient = models.ForeignKey(User, related_name="recipient")

    subject = models.CharField(max_length=300)
    message_body = models.TextField(max_length=5000)
    message_date = models.DateTimeField(default=timezone.now)
    message_read = models.BooleanField(default=False)
    message_is_new = models.BooleanField(default=True)

    """
        Okay, the last one there doesn't make much sense. I can't think of a good
        name for it. 

        I want to have new messages highlighted. The view will pull up the messages,
        and mark the unread ones (message_read as False) as read (message_read as True).
        These will be saved. Now, when we pass the queryset to the template, the 
        message will be already marked as read, as it was modified in the view. So
        new messages and old messages will look the same to the template.

        The idea is to check if message_is_new is true at the same time we check 
        if message_read is true. If both are true, we know that the message has 
        been read before, so message_is_new will then be flipped to false. this
        property is what determines which messages are highlighted in the template.

        If message_read is false and message_is_new is True (default), we'll keep
        message_is_new as is and flip message_read to True.

        First time through, the message will be highlighted. Next time through, 
        the view will flip message_is_new to False, so it won't be highlighted.
    """


    def __str__(self):
        return "Message from {} to {} on {}".format(self.sender.username,
                                                    self.recipient.username,
                                                    self.message_date)

class QuizResult(models.Model):
    deck = models.ForeignKey(Deck)
    user = models.ForeignKey(User)

    quiz_completed = models.BooleanField()
    quiz_date = models.DateTimeField(default=timezone.now)
    #duration of quiz in ms
    quiz_duration = models.PositiveIntegerField(default=1)

    questions_attempted = models.PositiveIntegerField(default=0)
    questions_correct = models.PositiveIntegerField(default=0)

    def __str__(self):

        quiz_completed_status = "COMPLETE" if self.quiz_completed else "INCOMPLETE"

        return "'{}{}' quiz result from {} on {} - {} : {} / {}".format(self.deck.title[:25],
                                                                   make_elipsis(self.deck.title),
                                                                   self.user.username,
                                                                   self.quiz_date,
                                                                   quiz_completed_status,
                                                                   self.questions_correct,
                                                                   self.questions_attempted)





