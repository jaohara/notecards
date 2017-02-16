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

    def add_tag(self, tag):
        self.tags.add(tag)
        self.save()

    def remove_tag(self, tag):
        self.tags.remove(tag)
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
    # 1-4 for one of the prefab avatars. They are located in the static directory,
    # named notecards-user-icon-x.png
    avatar = models.PositiveIntegerField(default=1)
    user = models.OneToOneField(User)

    # these stats could probably be inferred by making a queryset of all a user's QuizResults
    # I'm going to keep these here to remember the stats I want to grab, but they won't
    # be handled in this model.

    #questions_attempted = models.PositiveIntegerField(default=0)
    #questions_correct = models.PositiveIntegerField(default=0)

    #quizzes_attempted = models.PositiveIntegerField(default=0)
    #quizzes_completed = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "UserProfile for '{}'".format(self.user.username)


class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sender")
    recipient = models.ForeignKey(User, related_name="recipient")

    subject = models.CharField(max_length=300)

    message_body = models.TextField(max_length=5000)

    message_date = models.DateTimeField(default=timezone.now)

    message_read = models.BooleanField(default=False)

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





