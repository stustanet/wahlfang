from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404

from vote.authentication import token_login
from vote.forms import ApplicationUploadForm, VoteForm
from vote.models import Application, User


def code_authentication(request):
    token = request.GET.get('token')
    if not token:
        messages.add_message(request, messages.ERROR, 'No login code provided')
        return redirect('login')

    user = authenticate(token=token)
    if not user:
        messages.add_message(request, messages.ERROR, 'Invalid code')
        return redirect('login')

    login(request, user)

    return redirect('index')


@token_login
def index(request):
    voter = User.objects.get(token=request.user.username)
    context = {
        'voter': voter,
    }

    return render(request, template_name='vote/index.html', context=context)


@token_login
def vote(request):
    voter = User.objects.get(token=request.user.username)
    if not voter.can_vote:
        messages.add_message(request, messages.ERROR, 'Voting is not enabled yet')
        return redirect('index')

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


@token_login
def upload_application(request):
    voter = User.objects.get(token=request.user.username)
    if not voter.election.can_apply:
        messages.add_message(request, messages.ERROR, 'Applications are currently not accepted')
        return redirect('index')

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


@token_login
def view_application(request, pk):
    voter = User.objects.get(token=request.user.username)
    application = get_object_or_404(Application, pk=pk, user__election__pk=voter.election.pk)
    context = {
        'application': application
    }

    return render(request, template_name='vote/view_application.html', context=context)

