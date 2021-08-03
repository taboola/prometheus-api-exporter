from django.shortcuts import redirect
from django.shortcuts import render


def index(request):
    return render(request, 'main/index.html')


def view_404(request, exception=None):
    return redirect('/')
