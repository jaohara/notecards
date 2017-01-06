"""
    Here are some helper function declarations for the notecards app. 
"""


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
    if 'quiz_name' in request.session:
        del request.session['quiz_name']
    if 'quiz_questions' in request.session:
        del request.session['quiz_questions']
    if 'previous_answer' in request.session:
        del request.session['previous_answer']
    if 'quiz_attempted' in request.session:
        del request.session['quiz_attempted']
    if 'quiz_correct' in request.session:
        del request.session['quiz_correct']

# used in random spots for string formatting, this will either return 
# an elipsis or an empty string based on the length of the string
# provided.
def make_elipsis(name_string):
    if len(name_string) > 25:
        return "..."
    else:
        return ""