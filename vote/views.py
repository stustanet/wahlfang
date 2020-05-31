from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, views as auth_views
from django.http import Http404
from django.shortcuts import render, redirect
from ratelimit.decorators import ratelimit

from vote.authentication import voter_login_required
from vote.forms import AccessCodeAuthenticationForm, VoteForm, EmptyForm
from vote.models import Election


class LoginView(auth_views.LoginView):
    # login view settings
    # https://docs.djangoproject.com/en/3.0/topics/auth/default/#django.contrib.auth.views.LoginView
    authentication_form = AccessCodeAuthenticationForm
    template_name = 'vote/login.html'
    redirect_authenticated_user = True

    @ratelimit(key=settings.RATELIMIT_KEY, rate='10/h', method='POST')
    def post(self, request, *args, **kwargs):
        ratelimited = getattr(request, 'limited', False)
        if ratelimited:
            return render(request, template_name='vote/ratelimited.html', status=429)
        return super().post(request, *args, **kwargs)


@ratelimit(key=settings.RATELIMIT_KEY, rate='10/h')
def code_login(request, access_code=None):
    ratelimited = getattr(request, 'limited', False)
    if ratelimited:
        return render(request, template_name='vote/ratelimited.html', status=429)

    if not access_code:
        messages.error(request, 'No access code provided.')
        return redirect('vote:code_login')

    user = authenticate(access_code=access_code)
    if not user:
        messages.error(request, 'Invalid access code.')
        return redirect('vote:code_login')

    login(request, user)

    return redirect('vote:index')


@voter_login_required
def index(request):
    voter = request.user
    context = {
        'title': voter.session.title,
        'meeting_link': voter.session.meeting_link,
        'voter': voter,
    }

    context['elections'] = [
        (e, voter.can_vote(e)) for e in voter.session.elections.all()
    ]
    # overview
    return render(request, template_name='vote/index.html', context=context)


@voter_login_required
def vote(request, election_id):
    voter = request.user
    try:
        election = voter.session.elections.get(pk=election_id)
    except Election.DoesNotExist:
        raise Http404('election does not exists')

    can_vote = voter.can_vote(election)
    if election.max_votes_yes is not None:
        max_votes_yes = min(election.max_votes_yes, election.applications.count())
    else:
        max_votes_yes = election.applications.count()

    context = {
        'title': election.title,
        'election': election,
        'voter': voter,
        'can_vote': can_vote,
        'max_votes_yes': max_votes_yes,
        'form': VoteForm(request, election=election)
    }

    if request.POST and can_vote:
        form = VoteForm(request, election=election, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('vote:index')

    return render(request, template_name='vote/vote.html', context=context)
