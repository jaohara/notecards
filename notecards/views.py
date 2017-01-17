import random

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.core import serializers
from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.template import RequestContext
from django.utils import timezone

from django.contrib.auth.models import User
from .models import Tag, Deck, Card
from .forms import CardForm, DeckForm, DeckEditForm, UserForm

from .utils import reset_session_cards, reset_session_quiz, make_elipsis


# This might belong in a differen views.py, but it's here for now.
def handler404(request):
    response = render_to_response('404.html', {},
                                  context_instance=RequestContext(request))

    response.status_code = 404
    return response

def test_404(request):
    # solely to render and style the 404 page
    return render(request, '404.html', {})

def handler500(request):
    reponse = render_to_response('500.html', {},
                                 context_instance=RequestContext(request))

    request.status_code = 500
    return respose

def deck_list(request, sort_method="created_date", sort_order="ascending"):
    # Bug: Author isn't sorting alphabetically, it's sorting by author pk

    accepted_methods = ["created_date", "author", "title", "card_count"]

    order_switch = ""

    if sort_order == "descending":
        order_switch = "-"

    if sort_method not in accepted_methods:
        sort_method = "created_date"

    if sort_method == "author":
        sort_method = "author__username"

    reset_session_quiz(request)
    reset_session_cards(request)
    decks = Deck.objects.order_by("{}{}".format(order_switch,sort_method))
    form = DeckForm()
    return render(request, 'notecards/deck_list.html', {'decks': decks, 
                                                        'form': form,
                                                        'sort_method': sort_method,
                                                        'sort_order': sort_order,})

def deck_view(request, pk):

    quiz_results = ""
    feedback_type = "none"

    # this approach is reason enough to not have the reset_session_ methods as
    # decorators. Then again, if I made this results thing a decorator too...
    if 'quiz' in request.session:
        feedback_type = "neutral"
        quiz_correct = request.session['quiz_correct']
        quiz_attempted = request.session['quiz_attempted']
        quiz_percentage = '{:.2f}'.format((quiz_correct/quiz_attempted)*100)
        quiz_results = "Results: {} / {}  -  {}%".format(quiz_correct,
                                                       quiz_attempted,
                                                       quiz_percentage)

    reset_session_quiz(request)
    reset_session_cards(request)
    deck = get_object_or_404(Deck, pk=pk)
    cards = Card.objects.filter(deck__pk=deck.pk)
    form = CardForm()

    

    # return to this later, not necessary for first draft
    # tags = Tag.objects.filter()
    return render(request, 'notecards/deck_view.html', {'cards': cards,
                                                        'deck': deck,
                                                        'feedback_type': feedback_type, 
                                                        'form': form,
                                                        'quiz_results': quiz_results,})

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
        return render(request, 'notecards/deck_review.html', {'back': back,
                                                              'card_index': card_index,
                                                              'deck_length': len(cards),
                                                              'front': front,
                                                              'pk': pk,})

@login_required
def deck_quiz(request, deck_pk, answer_choice=None):

    if 'quiz' not in request.session:
        quiz_deck = get_object_or_404(Deck, pk=deck_pk)
        card_set = Card.objects.filter(deck__pk=quiz_deck.pk)

        quiz = list()
        quiz_index = 0

        for card in card_set:
            quiz.append({'front': card.front, 'back': card.back, 'pk': card.pk})

        random.shuffle(quiz)

        # is this the best way to approach question_answer?
        request.session['question_answer'] = quiz[quiz_index].get('pk')

        #save session vars
        request.session['quiz'] = quiz
        request.session['quiz_attempted'] = 0
        request.session['quiz_correct'] = 0
        request.session['quiz_count'] = quiz_deck.card_count
        request.session['quiz_deck_pk'] = deck_pk
        request.session['quiz_finished'] = 0
        request.session['quiz_index'] = quiz_index
        request.session['quiz_name'] = quiz_deck.title

    # initialize method vars
    feedback_text   = ""
    feedback_type   = "none"
    question_result = ""

    # pull session vars to local vars
    question_answer = request.session['question_answer']
    quiz            = request.session['quiz']
    quiz_attempted  = request.session['quiz_attempted']
    quiz_correct    = request.session['quiz_correct']
    quiz_count      = request.session['quiz_count']         # unnecessary?
    quiz_deck_pk    = request.session['quiz_deck_pk']       # unnecessary?
    quiz_finished   = request.session['quiz_finished']
    quiz_index      = request.session['quiz_index']
    quiz_name       = request.session['quiz_name']          # unnecessary?


    """
    The big problem I'm running into here is that there's no reliable way to 
    check if the page was refreshed. As of right now, I'm handling answer_choice
    via get, so that will always be resubmitted on a refresh. Because of this, 
    the quiz never knows whether or not to count that answer for the current 
    question or the question question.

    Here, we're fixing things up a bit. I'm planning on moving quiz_index to be
    handled by the view rather than by the URLs, so this should auto-increment.
    With this new behavior, the refresh will count as an incorrect answer 
    for the question question and move on to the next, but this is far from ideal.

    What if answers were submitted via POST? This would have that baked-in browser
    warning when resubmitting a form. The user is informed that what they're doing
    could break the functionality of the current page. Would I handle this via 
    a form instead of hyperlinks? Can I have links submit via post?

        This idea doesn't work, but I could rewrite my HTML to use a form with
        buttons styled like my Hyperlinks instead of just using the links. 
        I don't know how much I like this, but this would solve that problem.

    Is that even the solution to the problem? Is there a way to keep this solely 
    via GET and use session vars to check whether or not we've moved on to 
    another question?

    I suppose a good way to do this would be to save the new answer set as a 
    session var and check to see if the submitted answer is one of the ones from
    the current question's answer pool, assuming that if it doesn't match it would
    be one of the question question's answers and consider that a refresh instead
    of a submitted answer.

    A potential flaw of this approach would be if the current question's answer pool
    also contained the answer that was submitted for the question question. This 
    would result in it counting as an incorrect (or correct, I guess) answer for the
    current question, which isn't the intended functionality. This functionality would
    also happen without any warning, so the user would have no idea what happened.

    Is POST the best solution here?
    """



    """
    Conditions to check for:

        - Is the quiz finished?
        - Has an answer been submitted?
        - Was the page refreshed without an answer submitted?
    """

    """
    # case: quiz is finished
    if quiz_index >= len(quiz):
        # quiz is finished.

        # RETURN TO THIS, TALLY LAST ANSWER + SCORE BEFORE REDIRECTING
        quiz_finished = True
        request.session['quiz_finished'] = quiz_finished
        return redirect('/deck/{}'.format(quiz_deck_pk))
    """

    # case: answer is given, check for correctness
    if answer_choice is not None:
        quiz_attempted += 1

        answer_card = get_object_or_404(Card, pk=question_answer)
        answer_front = answer_card.front
        answer_back = answer_card.back

        feedback_type = "negative"
        question_result = "Sorry, wrong answer:"

        if int(answer_choice) == int(question_answer):
            feedback_type = "positive"
            question_result = "Correct!"
            quiz_correct += 1

        quiz_index += 1

        # check if quiz is finished
        if quiz_index >= len(quiz):
            quiz_finished = True

        feedback_text = "{} '{}{}' matches with '{}{}'".format(question_result,
                                                               answer_front[:25],
                                                               make_elipsis(answer_front),
                                                               answer_back[:25],
                                                               make_elipsis(answer_back))

    if not quiz_finished:
        # find next question
        new_question = quiz[quiz_index].get('front')
        answers_pk = [quiz[quiz_index].get('pk')]
        question_answer = answers_pk[0]

        # populate answer list
        while len(answers_pk) < 4:
            answer_pk = quiz[random.randrange(len(quiz))].get('pk')
            if answer_pk not in answers_pk:
                answers_pk.append(answer_pk)

        random.shuffle(answers_pk)

        answers = list()
        answers_index = 0

        for answer in answers_pk:
            answer_back = Card.objects.get(pk=answer).back

            answers.append((int(answer), answer_back, answers_index))
            answers_index += 1

    # score the quiz
    if quiz_attempted > 0:
        quiz_score = quiz_correct / quiz_attempted * 100.00
        quiz_score = '{:.2f}'.format(quiz_score)
    else:
        quiz_score = 0.00


    # AFTER operations, BEFORE rendering
    # quiz_count, quiz_deck_pk, quiz_name don't need to be reset
    request.session['question_answer']  = question_answer  
    request.session['quiz']             = quiz
    request.session['quiz_attempted']   = quiz_attempted
    request.session['quiz_correct']     = quiz_correct
    request.session['quiz_finished']    = quiz_finished
    request.session['quiz_index']       = quiz_index

    if (quiz_finished):
        return redirect('/deck/{}'.format(quiz_deck_pk))
    else:   
        return render(request, 'notecards/deck_quiz.html', {'answers': answers,
                                                            'deck_title': request.session['quiz_name'],
                                                            'feedback_type': feedback_type,
                                                            'feedback_text': feedback_text,
                                                            'question': new_question,
                                                            'quiz_attempted': quiz_attempted,
                                                            'quiz_correct': quiz_correct,
                                                            'quiz_deck_pk': quiz_deck_pk,
                                                            'quiz_index': quiz_index,
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
def edit_deck(request, pk):
    deck = get_object_or_404(Deck, pk=pk)

    if request.method == "POST":
        form = DeckEditForm(request.POST or None, instance=deck)
        if form.is_valid():
            form.save()
            #deck.log_modification()
            #deck.save()
            return redirect('deck_view', pk=pk)

    else:
        if request.user.is_authenticated():
            username = request.user
            if deck.author == username:
                form = DeckEditForm(initial={'title': deck.title, 
                                             'description': deck.description})

                return render(request, 'notecards/deck_edit.html', {'deck': deck,
                                                                    'form': form,
                                                                    'pk': pk,})
        else:
            return redirect('deck_view', pk=deck.pk)

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
def edit_card(request, deck_pk, card_pk):
    # what do I need the deck for?
    deck = get_object_or_404(Deck, pk=deck_pk)
    card = get_object_or_404(Card, pk=card_pk)

    if request.method == "POST":
        form = CardForm(request.POST or None, instance=card)
        if form.is_valid():
            form.save()
            return redirect('deck_view', pk=deck_pk)

    else:
        if request.user.is_authenticated():
            username = request.user
            if deck.author == username:
                form = CardForm(initial={'front': card.front,
                                         'back': card.back,})

                return render(request, 'notecards/card_edit.html', {'card': card,
                                                                    'card_pk': card_pk,
                                                                    'deck': deck,
                                                                    'deck_pk': deck_pk,
                                                                    'form': form,})
        else: 
            return redirect('deck_view', pk=deck_pk)

@login_required
def remove_card_from_deck(request, pk):
    card = get_object_or_404(Card, pk=pk)
    deck = card.deck
    card.delete()
    deck.remove_card()
    return redirect('deck_view', pk=deck.pk)

def create_user(request):
    if request.method == "POST":
        # here's where we handle the submitted data
        form = UserForm(request.POST)
        if form.is_valid():
            # **form.cleaned_data retrieves all keyword arguments from the form
            new_user = User.objects.create_user(**form.cleaned_data)
            login(request, new_user)
            return redirect('/')

    else:
        form = UserForm()

    return render(request, 'registration/create_user.html', {'form': form,})



# I don't know if you need to be logged in for any of this, but it would
# probably be the difference between viewing a profile and editing your own

@login_required
def user_profile(request, pk):
    selected_user = get_object_or_404(User, pk=pk)
    decks = Deck.objects.filter(author=selected_user.pk)

    return render(request, 'user_profiles/user_profile.html', {'selected_user': selected_user,
                                                               'decks': decks,})

@login_required
def user_stats(request, pk):
    # placeholder
    return redirect('/')

@login_required
def user_decks(request, pk):
    # placeholder
    return redirect('/')

@login_required
def user_list(request):
    # placeholder
    return redirect('/')