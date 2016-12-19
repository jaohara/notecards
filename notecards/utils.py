def reset_session_cards(request):
    if 'cards' in request.session:
        del request.session['cards']