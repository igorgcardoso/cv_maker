
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.shortcuts import redirect, render

from core.forms import GenerateForm, LoginForm


# Create your views here.
def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
    return render(request, 'login.html', {'form': form})


@login_required(login_url='/login/')
def home(request):
    user = request.user
    if request.method == 'POST':
        filled = GenerateForm(user, request.POST)
        if not filled.is_valid():
            return render(request, 'home.html', {'form': filled})
        data = filled.cleaned_data
        language = data.get('language')
        role = data.get('role')
        brief = data.get('brief')
        skills = data.get('skills')
        user = request.user
        cv = user.generate_cv(language, role, brief, skills)
        response = FileResponse(open(cv.name, 'rb'), as_attachment=True, filename=f'{user.first_name} {user.last_name} - {language.language}.pdf')
        cv.close()
        return response
    form = GenerateForm(user=user)
    return render(request, 'home.html', {'form': form})
