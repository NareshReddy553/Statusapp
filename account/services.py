from django.core.cache import cache
from account.models import Users


def get_cached_user(userid):
    if userid is None:
        return None
    user = cache.get("USER_" + str(userid))
    if user is None:
        user = Users.objects.values(
            "user_id", "email", "first_name", "last_name"
        ).filter(pk=userid).first()
        if user is not None:
            cache.set("USER_" + str(userid), user, 120)
    return user