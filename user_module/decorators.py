from django.http import HttpResponseForbidden
from functools import wraps

def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.groups.filter(name__in=allowed_roles).exists():
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseForbidden("You are not authorized to view this page.")
        return wrapper
    return decorator
