from django.contrib import messages
from django.contrib.admin.models import LogEntry
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.views.decorators.http import require_POST


@require_POST
def clear_recent_actions(request):
    """Delete the logged-in superuser's admin history (the 'Recent actions' panel)."""
    if not request.user.is_superuser:
        raise PermissionDenied
    deleted, _ = LogEntry.objects.filter(user=request.user).delete()
    messages.success(request, f"Cleared {deleted} recent action(s).")
    return redirect("admin:index")
