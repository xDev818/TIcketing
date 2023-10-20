
def extras(request):
    username = "Test"
    active = 1
    display= "Test User"
    context = {
        'username' : username,
        'active': active,
        'display': display
    }
    return context 