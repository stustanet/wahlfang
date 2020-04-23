from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from vote.forms import ApplicationUploadForm, VoteForm
from vote.models import Application, User


@login_required
def index(request):
    voter = User.objects.get(token=request.user.username)
    context = {
        'voter': voter,
    }

    return render(request, template_name='vote/index.html', context=context)


@login_required
def vote(request):
    context = {
       'form': VoteForm(request)
    }

    if request.POST:
        form = VoteForm(request, request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
        else:
            context['form'] = form

    return render(request, template_name='vote/vote.html', context=context)


@login_required
def upload_application(request):
    instance = Application.objects.filter(user__token=request.user.username).first()

    context = {
        'form': ApplicationUploadForm(request, instance=instance)
    }

    if request.POST:
        form = ApplicationUploadForm(request, request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('index')
        else:
            context['form'] = form

    return render(request, template_name='vote/upload_application.html', context=context)

