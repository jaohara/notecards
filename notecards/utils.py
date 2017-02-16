import time

from . import models

"""
    Here are some helper function declarations for the notecards app. 
"""

def make_elipsis(name_string):
    if len(name_string) > 25:
        return "..."
    else:
        return ""

def mail_count_check(request, selected_user):
    if selected_user == request.user:
        return models.Message.objects.filter(recipient=request.user.pk).order_by("-message_date").filter(message_read=False).count()
    else: 
        return 0


# these "reset_session_" methods are pretty straightforward; they delete
# a particular session variable if present to make sure they don't exist
# at the wrong time.

# these should probably be made into decorators. 
def reset_session_cards(request):
    if 'cards' in request.session:
        del request.session['cards']


def reset_session_quiz(request):
    if 'quiz' in request.session:
        del request.session['quiz']
    if 'quiz_attempted' in request.session:
        del request.session['quiz_attempted']
    if 'quiz_correct' in request.session:
        del request.session['quiz_correct']
    if 'quiz_count' in request.session:
        del request.session['quiz_count']
    if 'quiz_deck_pk' in request.session:
        del request.session['quiz_deck_pk']
    if 'quiz_finished' in request.session:
        del request.session['quiz_finished']
    if 'quiz_index' in request.session:
        del request.session['quiz_index']
    if 'quiz_name' in request.session:
        del request.session['quiz_name']
    if 'quiz_questions' in request.session:
        del request.session['quiz_questions']
    if 'quiz_start_time' in request.session:
        del request.session['quiz_start_time']


def save_quiz_results(request):
    if request.user.is_authenticated() and 'quiz' in request.session:
        deck = models.Deck.objects.get(pk=request.session['quiz_deck_pk'])
        user = request.user

        # i should probably unify this name across the views and model
        quiz_completed = request.session.get('quiz_finished')
        quiz_duration = int(round(time.time()*1000)) - request.session.get('quiz_start_time', 0)

        questions_attempted = request.session.get('quiz_attempted')
        questions_correct = request.session.get('quiz_correct')

        quiz_result = models.QuizResult(deck=deck,
                                        user=user,
                                        quiz_completed=quiz_completed,
                                        questions_attempted=questions_attempted,
                                        questions_correct=questions_correct,
                                        quiz_duration=quiz_duration)

        quiz_result.save()

    reset_session_quiz(request)