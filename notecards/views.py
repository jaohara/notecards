import random
import time

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.core import serializers
from django.db.models.functions import Lower
from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.template import RequestContext
from django.utils import timezone

from django.contrib.auth.models import User
from .models import Card, Deck, Message, QuizResult, Tag, UserProfile
from .forms import CardForm, DeckForm, DeckEditForm, MessageForm, UserForm, TagForm

from .utils import reset_session_cards, reset_session_quiz, make_elipsis, save_quiz_results, mail_count_check


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

def deck_list(request, sort_method="created_date", sort_order="ascending", deck_query=None):
    
    if request.GET.get('search'):
        deck_query = request.GET["search"]

    accepted_methods = ["created_date", "author", "title", "card_count"]

    order_switch = ""

    if sort_order == "descending":
        order_switch = "-"

    if sort_method not in accepted_methods:
        sort_method = "created_date"

    if sort_method == "author":
        sort_method = "author__username"

    save_quiz_results(request)
    reset_session_cards(request)
    if deck_query is not None:
        # flesh this out in the future to be more robust, better pattern matching etc.
        decks = Deck.objects.filter(title__icontains=deck_query).order_by("{}{}".format(order_switch,sort_method))
    else:
        # Here's where we need to use Lower() to avoid case affecting sort order
        decks = Deck.objects.order_by("{}{}".format(order_switch,sort_method))
    form = DeckForm()
    return render(request, 'notecards/deck_list.html', {'decks': decks,
                                                        'deck_query': deck_query, 
                                                        'form': form,       # REMOVED IN SEARCH CASES?
                                                        'sort_method': sort_method,
                                                        'sort_order': sort_order,})

def tag_deck_list(request, tag_word):
    tag = get_object_or_404(Tag, word=tag_word)

    decks = tag.deck_set.all()

    # This will soon be removed, as this shouldn't be on every search result page.
    form = DeckForm()

    return render(request, 'notecards/deck_list.html', {'decks': decks,
                                                        'form': form,       # TO BE REMOVED
                                                        'tag': tag,})

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

    save_quiz_results(request)
    reset_session_cards(request)
    deck = get_object_or_404(Deck, pk=pk)
    cards = Card.objects.filter(deck__pk=deck.pk)
    card_form = CardForm()
    tag_form = TagForm()


    return render(request, 'notecards/deck_view.html', {'cards': cards,
                                                        'card_form': card_form,
                                                        'deck': deck,
                                                        'feedback_type': feedback_type, 
                                                        'quiz_results': quiz_results,
                                                        'tag_form': tag_form,})

@login_required
def deck_review(request, pk, card_index=0):
    save_quiz_results(request)

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
        request.session['quiz_finished'] = False
        request.session['quiz_index'] = quiz_index
        request.session['quiz_name'] = quiz_deck.title
        request.session['quiz_start_time'] = int(round(time.time()*1000))

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

    if request.user == deck.author:
        deck.delete()


    # this will probably be an  AJAX operation in the future, in the meantime redirect to the latest page

    # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    # return redirect('/')
    return redirect(request.META.get('HTTP_REFERER'))

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
        if request.user == deck.author:
            if form.is_valid():
                card = form.save(commit=False)
                card.deck = deck
                card.save()
                deck.add_card()
                return redirect('deck_view', pk=deck.pk)
        else:
            redirect('/')
    else:
        redirect('/')

@login_required
def add_tag_to_deck(request, pk):
    if request.method == "POST":
        deck = get_object_or_404(Deck, pk=pk)
        form = TagForm(request.POST)
        if request.user == deck.author:
            if form.is_valid():
                tag = form.save(commit=False)
                if Tag.objects.filter(word=form.cleaned_data['word']).count() == 0:
                    # create tag object
                    tag.save()

                tag = Tag.objects.get(word=form.cleaned_data['word'])
                # add tag to deck
                deck.add_tag(tag)
                deck.save()

                return redirect('deck_view', pk=deck.pk)
        else:
            return redirect('/')

    else:
        return redirect('/')

@login_required
def remove_tag_from_deck(request, pk, tag_word):
    deck = get_object_or_404(Deck, pk=pk)
    tag = get_object_or_404(Tag, word=tag_word)

    if request.user == deck.author:
        deck.remove_tag(tag)
        deck.save()
        return redirect('deck_view', pk=deck.pk)

    else:
        return redirect('/')

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


"""

    USER CREATION VIEWS

"""


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


"""


    USER PROFILE VIEWS


"""

# I don't know if you need to be logged in for any of this, but it would
# probably be the difference between viewing a profile and editing your own
@login_required
def user_profile(request, pk):

    selected_user = get_object_or_404(User, pk=pk)
    decks = Deck.objects.filter(author=selected_user.pk)

    mail_count = mail_count_check(request, selected_user)

    all_used_tags = dict()

    for deck in decks:
        for tag in deck.tags.all():
            if tag not in all_used_tags:
                all_used_tags[tag] = 1
            else:
                all_used_tags[tag] += 1

    favorite_tags = sorted(all_used_tags, key=all_used_tags.get, reverse=True)

    return render(request, 'user_profiles/user_profile.html', {'favorite_tags': favorite_tags[:10],
                                                               'mail_count': mail_count,
                                                               'selected_user': selected_user,})


@login_required
def user_messages(request, feedback_type=None, feedback_text=None):
    # why do I keep grabbing pks here? shouldn't I just check against the currently
    # logged in user?

    inbox = Message.objects.filter(recipient=request.user.pk).order_by("-message_date")
    outbox = Message.objects.filter(sender=request.user.pk)

    mail_count = mail_count_check(request, request.user)

    for message in inbox:
        message_changed = False
        if message.message_read == False:
            message.message_read = True
            message_changed = True
        elif message.message_read == True and message.message_is_new == True:
            message.message_is_new = False
            message_changed = True

        if message_changed:
            message.save()

    return render(request, 'user_profiles/user_messages.html', {'inbox': inbox,
                                                                'mail_count': mail_count,
                                                                'outbox': outbox,
                                                                'selected_user': request.user})


@login_required
def user_write_message(request, recipient_pk=None):
    if request.method == "POST":
        message_form = MessageForm(request.POST)
        if message_form.is_valid():

            # Is it worth preventing messages to yourself? Reddit allows it. It's useless but harmless.
            feedback_type = 'negative'
            feedback_text = 'You cannot send a message to yourself.'
            if request.user != message_form.cleaned_data.get('recipient'):
                new_message = Message(sender=request.user,
                                      recipient=message_form.cleaned_data.get('recipient'),
                                      subject=message_form.cleaned_data.get('subject'),
                                      message_body= message_form.cleaned_data.get('message_body'))


                new_message.save()
                feedback_type = 'positive'
                feedback_text = "Message to {} sent successfully.".format(message_form.cleaned_data.get('recipient'))
                """
                return render(request, 'user_profiles/user_messages.html', {'feedback_type': 'positive',
                                                                            'feedback_text': feedback_text,
                                                                            'selected_user': request.user})
                """
            return user_messages(request, feedback_type, feedback_text)
    
    message_form = MessageForm(initial={'recipient': recipient_pk})

    return render(request, 'user_profiles/user_write_message.html', {'mail_count': mail_count_check(request, request.user),
                                                                     'message_form': message_form,
                                                                     'selected_user': request.user})

@login_required
def user_delete_message(request, message_pk):
    message = get_object_or_404(Message, pk=message_pk)

    if request.user == message.recipient:
        message.delete()
        feedback_type = "neutral"
        feedback_text = "Message deleted."
        return user_messages(request, feedback_type, feedback_text)

    else:
        return redirect('/')

@login_required
def user_settings(request, pk):
    selected_user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        password_form = PasswordChangeForm(request.user, data=request.POST)
        if password_form.is_valid():
            password_form.save()
            update_session_auth_hash(request, password_form.user)
            redirect('/')

    password_form = PasswordChangeForm(request.user)

    mail_count = mail_count_check(request, selected_user)

    return render(request, 'user_profiles/user_settings.html', {'mail_count': mail_count,
                                                                'password_form': password_form,
                                                                'selected_user': selected_user,})


@login_required
def user_stats(request, pk):
    selected_user = get_object_or_404(User, pk=pk)
    stats = QuizResult.objects.filter(user=selected_user.pk)

    total_questions_correct = 0
    total_questions_attempted = 0
    total_quiz_duration = 0
    total_quizzes_attempted = len(stats)
    total_quizzes_completed = 0


    for stat in stats:
        if stat.quiz_completed:
            total_quizzes_completed += 1

        total_questions_correct += stat.questions_correct
        total_questions_attempted += stat.questions_attempted
        total_quiz_duration += stat.quiz_duration

    quiz_duration_minutes = '{:.0f}'.format((total_quiz_duration/1000)//60)
    quiz_duration_seconds = '{:.2f}'.format((total_quiz_duration/1000)%60)

    if total_quizzes_attempted > 0:
        quiz_completion_rate = '{:.2f}'.format(total_quizzes_completed/total_quizzes_attempted*100.00)
    else:
        quiz_completion_rate = '0.00'

    if total_questions_attempted > 0:
        question_correct_percentage = '{:.2f}'.format(total_questions_correct/total_questions_attempted*100.00)
    else:
        question_correct_percentage = '0.00'

    mail_count = mail_count_check(request, selected_user)

    return render(request, 'user_profiles/user_stats.html', {'mail_count': mail_count,
                                                             'question_correct_percentage': question_correct_percentage,
                                                             'questions_attempted': total_questions_attempted,
                                                             'questions_correct': total_questions_correct,
                                                             'quiz_completion_rate': quiz_completion_rate,
                                                             'quiz_duration': total_quiz_duration,
                                                             'quiz_duration_minutes': quiz_duration_minutes,
                                                             'quiz_duration_seconds': quiz_duration_seconds,
                                                             'quizzes_attempted': total_quizzes_attempted,
                                                             'quizzes_completed': total_quizzes_completed,
                                                             'selected_user': selected_user,
                                                             'stats': stats,})


@login_required
def user_decks(request, pk, sort_method="created_date", sort_order="ascending"):
    #decks = Deck.objects.filter(author=selected_user.pk)

    accepted_methods = ["created_date", "title", "card_count"]

    order_switch = ""

    if sort_order == "descending":
        order_switch = "-"

    if sort_method not in accepted_methods:
        sort_method = "created_date"

    save_quiz_results(request)
    reset_session_cards(request)
    
    selected_user = get_object_or_404(User, pk=pk)
    decks = Deck.objects.order_by("{}{}".format(order_switch,sort_method)).filter(author=selected_user.pk)

    mail_count = mail_count_check(request, selected_user)

    return render(request, 'user_profiles/user_decks.html', {'decks': decks,
                                                             'mail_count': mail_count,
                                                             'selected_user': selected_user,
                                                             'sort_method': sort_method,
                                                             'sort_order': sort_order,})


# this shares a little more than I'd like with deck_list
@login_required
def user_list(request, sort_method="date_joined", sort_order="ascending", user_query=None):
    # no current way to make a user_query

    if request.GET.get('search'):
        deck_query = request.GET["search"]

    accepted_methods = ["username", "date_joined"]

    order_switch = ""

    if sort_order == "descending":
        order_switch = "-"

    if sort_method not in accepted_methods:
        sort_method = "created_date"

    save_quiz_results(request)
    reset_session_cards(request)

    if user_query is not None:
        users = User.objects.filter(username__icontains=user_query).order_by("{}{}".format(order_switch,sort_method))
    else:
        # Here's where we need to use Lower() to avoid case affecting sort order
        users = User.objects.order_by("{}{}".format(order_switch,sort_method))

    return render(request, 'user_profiles/user_list.html', {'sort_method': sort_method,
                                                            'sort_order': sort_order,
                                                            'user_query': user_query,
                                                            'users': users,})
