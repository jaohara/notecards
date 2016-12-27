import random

from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core import serializers
from .models import Tag, Deck, Card
from .forms import CardForm, DeckForm
from .utils import reset_session_cards, reset_session_quiz

def deck_list(request):
    reset_session_quiz(request)
    reset_session_cards(request)
    decks = Deck.objects.all()
    form = DeckForm()
    return render(request, 'notecards/deck_list.html', {'decks': decks, 'form': form,})

def deck_view(request, pk):
    reset_session_quiz(request)
    reset_session_cards(request)
    deck = get_object_or_404(Deck, pk=pk)
    cards = Card.objects.filter(deck__title=deck.title)
    form = CardForm()

    # return to this later, not necessary for first draft
    # tags = Tag.objects.filter()
    return render(request, 'notecards/deck_view.html', {'deck': deck, 
                                                        'cards': cards, 
                                                        'form': form,})

@login_required
def deck_review(request, pk, card_index=0):
    card_index = int(card_index)

    
    if 'cards' not in request.session:
        deck = get_object_or_404(Deck, pk=pk)
        card_set = Card.objects.filter(deck__title=deck.title)

        #test_card = None
        cards = list()

        for card in card_set:
            cards.append({'front': card.front, 'back': card.back})
            #test_card = card

        # TODO: make an extra argument as a boolean to allow for unshuffled or shuffled orders
        random.shuffle(cards)
        request.session['cards'] = cards
    else:
        cards = request.session['cards']

    if card_index >= len(cards):
        reset_session_cards(request)
        return redirect('/deck/{}/'.format(pk))

    else:
        front = cards[card_index].get('front')
        back = cards[card_index].get('back')
        return render(request, 'notecards/deck_review.html', {'front': front,
                                                              'back': back,
                                                              'card_index': card_index,
                                                              'deck_length': len(cards),
                                                              'pk': pk})

#I'm going to be implementing this in a very redundant manner; it will reuse a
#lot of code from the quiz_review view. This shared code should be made into
#a distinct helper method in a later update.

# also, what happens if you jump from review to quiz? You'd be using the same
# session variable. Maybe I should use 'quiz' instead...
@login_required
def deck_quiz(request, pk, quiz_index=0, answer_choice=None):

    quiz_index = int(quiz_index)


    # This will set up our session variables
    # ---
    # maybe I should check to make sure quiz_index is also 0 if the quiz doesn't exist
    if 'quiz' not in request.session:
        deck = get_object_or_404(Deck, pk=pk)
        card_set = Card.objects.filter(deck__title=deck.title)

        quiz = list()

        for card in card_set:
            quiz.append({'front': card.front, 'back': card.back, 'pk': card.pk})

        random.shuffle(quiz)
        request.session['quiz'] = quiz
        request.session['quiz_questions'] = deck.card_count
        request.session['quiz_attempted'] = 0
        request.session['quiz_correct'] = 0
        request.session['previous_answer'] = quiz[quiz_index].get('pk')
    else:
        quiz = request.session['quiz']

    # this should be made to account for finishing the quiz
    # maybe I should save quiz_index as a session variable
    # instead of revealing it via get?

    # also, what about repeating questions by changing the URL manually? should
    # the quiz object be treated as a queue?
    if quiz_index >= len(quiz):
        reset_session_quiz(request)
        return redirect('/deck/{}/'.format(pk))

    else:
        # first, we need to check if an answer has been submitted. 
        if answer_choice is not None:
            # we've submitted an answer, so let's check if it's right.
            if 'previous_answer' in request.session:
                request.session['quiz_attempted'] += 1
                if int(answer_choice) == int(request.session['previous_answer']):
                    request.session['quiz_correct'] += 1

        question = quiz[quiz_index].get('front')
        answers_pk = [quiz[quiz_index].get('pk')]
        request.session['previous_answer'] = answers_pk[0]

        if 'quiz_attempted' in request.session:
            quiz_attempted = request.session['quiz_attempted']
        else:
            # this is kind of a BS fallback, will be more elegant later
            quiz_attempted = 0
        if 'quiz_correct' in request.session:
            quiz_correct = request.session['quiz_correct']
        else:
            # same with this one
            quiz_correct = 0

        # pick randomly
        while len(answers_pk) < 4:
            answer_pk = quiz[random.randrange(len(quiz))].get('pk')
            if answer_pk not in answers_pk:
                answers_pk.append(answer_pk)

        # we should now have four random answers, so let's put them in random order:
        random.shuffle(answers_pk)

        answers = list()

        for answer in answers_pk:
            answer_back = Card.objects.get(pk=answer).back

            answers.append((int(answer), answer_back))

        # now we have answers, which is a list of tuples of (card.pk, card.back)

        if quiz_attempted > 0:
            quiz_score = quiz_correct / quiz_attempted * 100.00
            quiz_score = '{:.2f}'.format(quiz_score)
        else:
            quiz_score = 0.00

        return render(request, 'notecards/deck_quiz.html', {'question': question,
                                                            'answers': answers,
                                                            'quiz_index': quiz_index,
                                                            'pk': pk,
                                                            'quiz_attempted': quiz_attempted,
                                                            'quiz_correct': quiz_correct,
                                                            'quiz_score': quiz_score,})




@login_required
def flush_session(request):
    request.session.flush()
    return redirect('/')

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
