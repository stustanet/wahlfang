from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from vote.forms import ApplicationUploadForm


@login_required
def index(request):
    context = {}

    return render(request, template_name='vote/index.html', context=context)


@login_required
def vote(request):
    context = {}

    return render(request, template_name='vote/vote.html', context=context)


@login_required
def upload_application(request):
    context = {
        'form': ApplicationUploadForm(request)
    }

    if request.POST:
        form = ApplicationUploadForm(request, request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('index')
        else:
            context['form'] = form

    return render(request, template_name='vote/upload_application.html', context=context)

