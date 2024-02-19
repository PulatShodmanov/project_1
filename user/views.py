from django.shortcuts import render, redirect
from user.forms import SignUpForm

def sign_up(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("user:sign_in")
    else:
        form = SignUpForm()
    data = {
        "form": form,
    }

    return render(request, 'registration/signup.html', data)

def sign_in(request):
    return render(request, 'registration/signin.html')