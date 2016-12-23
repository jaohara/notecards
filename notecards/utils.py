def reset_session_cards(request):
    if 'cards' in request.session:
        del request.session['cards']

def reset_session_quiz(request):
    if 'quiz' in request.session:
        del request.session['quiz']