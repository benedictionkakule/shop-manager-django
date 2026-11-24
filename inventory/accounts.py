from django.contrib import messages
from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.models import Group
from django.shortcuts import redirect, render

from .forms import SignUpForm


@login_not_required
def signup(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # an administrator must approve the account
            user.save()

            # New accounts start with the least-privileged role
            cashier = Group.objects.filter(name="Cashier").first()
            if cashier:
                user.groups.add(cashier)

            messages.success(
                request,
                "Account created. An administrator must approve it before you can sign in.",
            )
            return redirect("login")
    else:
        form = SignUpForm()

    return render(request, "registration/signup.html", {"form": form})
