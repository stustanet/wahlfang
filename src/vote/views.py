from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def index(request):
    context = {}

    return render(request, template_name='vote/index.html', context=context)


@login_required
def vote(request):
    context = {}

    return render(request, template_name='vote/upload_application.html', context=context)
