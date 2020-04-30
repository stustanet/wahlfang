from django.contrib import messages
from django.contrib.auth import authenticate, login, views as auth_views
from django.shortcuts import render, redirect, get_object_or_404
from ratelimit.decorators import ratelimit

from vote.authentication import voter_login_required
from vote.forms import AccessCodeAuthenticationForm, ApplicationUploadForm, VoteForm
from vote.models import Application


class LoginView(auth_views.LoginView):
    # login view settings
    # https://docs.djangoproject.com/en/3.0/topics/auth/default/#django.contrib.auth.views.LoginView
    authentication_form = AccessCodeAuthenticationForm
    template_name = 'vote/login.html'
    redirect_authenticated_user = True

    @ratelimit(key='ip', rate='10/h', method='POST')
    def post(self, request, *args, **kwargs):
        ratelimited = getattr(request, 'limited', False)
        if ratelimited:
            return render(request, template_name='vote/ratelimited.html', status=429)
        return super().post(request, *args, **kwargs)


@ratelimit(key='ip', rate='10/h')
def code_login(request, access_code=None):
    ratelimited = getattr(request, 'limited', False)
    if ratelimited:
        return render(request, template_name='vote/ratelimited.html', status=429)

    if not access_code:
        messages.add_message(request, messages.ERROR, 'No access code provided.')
        return redirect('vote:code_login')

    user = authenticate(access_code=access_code)
    if not user:
        messages.add_message(request, messages.ERROR, 'Invalid access code.')
        return redirect('vote:code_login')

    login(request, user)

    return redirect('vote:index')


@voter_login_required
def index(request):
    voter = request.user

    context = {
        'title': voter.election.title,
        'max_votes_yes': voter.election.max_votes_yes,
        'voter': voter,
    }

    # vote
    if voter.can_vote:
        if request.POST:
            form = VoteForm(request, request.POST)
            if form.is_valid():
                form.save()
                return redirect('vote:index')
            context['form'] = form
        else:
            context['form'] = VoteForm(request)

        return render(request, template_name='vote/vote.html', context=context)

    # overview
    return render(request, template_name='vote/index.html', context=context)


@voter_login_required
def upload_application(request):
    voter = request.user
    if not voter.election.can_apply:
        messages.add_message(request, messages.ERROR, 'Applications are currently not accepted')
        return redirect('vote:index')

    instance = Application.objects.filter(voter=voter.voter_id).first()

    if request.POST:
        form = ApplicationUploadForm(request, request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('vote:index')
    else:
        form = ApplicationUploadForm(request, instance=instance)

    context = {
        'form': form
    }
    return render(request, template_name='vote/upload_application.html', context=context)
