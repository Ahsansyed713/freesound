from django.contrib.auth.models import User
from accounts.models import OldUsername
from django.http import Http404

def get_user_from_oldusername(username):
    # Helper to get the user from an username that could have changed
    user = None
    try:
        user = User.objects.select_related('profile').get(username__iexact=username)
    except User.DoesNotExist:
        try:
            old = OldUsername.objects.get(username__iexact=username)
            user = old.user
        except OldUsername.DoesNotExist:
            pass
    return user


def get_user_or_404(username):
    # Helper to get the user from an username or raise 404
    user = get_user_from_oldusername(username)
    if user == None:
        raise Http404
    return user
