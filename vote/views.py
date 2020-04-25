from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404

from vote.authentication import voter_login_required
from vote.forms import ApplicationUploadForm, VoteForm
from vote.models import Application, Voter

def code_login(request, access_code=None):
    if not access_code:
        messages.add_message(request, messages.ERROR, 'No access code provided.')
        return redirect('code_login')

    user = authenticate(access_code=access_code)
    if not user:
        messages.add_message(request, messages.ERROR, 'Invalid access code.')
        return redirect('code_login')

    login(request, user)

    return redirect('index')


@voter_login_required
def index(request):
    voter = Voter.objects.get(voter_id=request.user.voter_id)
    context = {
        'voter': voter,
    }

    return render(request, template_name='vote/index.html', context=context)


@voter_login_required
def vote(request):
    voter = Voter.objects.get(voter_id=request.user.voter_id)
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
        context['form'] = form

    return render(request, template_name='vote/vote.html', context=context)


@voter_login_required
def upload_application(request):
    voter = Voter.objects.get(voter_id=request.user.voter_id)
    if not voter.election.can_apply:
        messages.add_message(request, messages.ERROR, 'Applications are currently not accepted')
        return redirect('index')

    instance = Application.objects.filter(voter=request.user.voter_id).first()

    context = {
        'form': ApplicationUploadForm(request, instance=instance)
    }

    if request.POST:
        form = ApplicationUploadForm(request, request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('index')
        context['form'] = form

    return render(request, template_name='vote/upload_application.html', context=context)


@voter_login_required
def view_application(request, pk):
    voter = Voter.objects.get(voter_id=request.user.voter_id)
    application = get_object_or_404(Application, pk=pk, voter__election__pk=voter.election.pk)
    context = {
        'application': application
    }

    return render(request, template_name='vote/view_application.html', context=context)
