from functools import wraps
from django.contrib.auth.decorators import login_required

def login_required_nocache(view_func):
    """
    Gabungan @login_required + no-cache headers
    """
    @login_required
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        # Tambahkan headers anti-cache
        response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response["Pragma"] = "no-cache"
        response["Expires"] = "0"
        return response
    return _wrapped_view
