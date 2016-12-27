def reset_session_cards(request):
    if 'cards' in request.session:
        del request.session['cards']

def reset_session_quiz(request):
    if 'quiz' in request.session:
        del request.session['quiz']
    if 'quiz_questions' in request.session:
        del request.session['quiz_questions']
    if 'previous_answer' in request.session:
        del request.session['previous_answer']
    if 'quiz_attempted' in request.session:
        del request.session['quiz_attempted']
    if 'quiz_correct' in request.session:
        del request.session['quiz_correct']