from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, views as auth_views
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from ratelimit.decorators import ratelimit

from vote.authentication import voter_login_required
from vote.forms import AccessCodeAuthenticationForm, VoteForm, ApplicationUploadFormUser
from vote.models import Election, Voter


class LoginView(auth_views.LoginView):
    # login view settings
    # https://docs.djangoproject.com/en/3.0/topics/auth/default/#django.contrib.auth.views.LoginView
    authentication_form = AccessCodeAuthenticationForm
    template_name = 'vote/login.html'
    redirect_authenticated_user = False

    def get(self, request, *args, **kwargs):
        print(request, args)
        u = request.user
        if u.is_authenticated and isinstance(u, Voter):
            return redirect('vote:index')
        return super().get(request, *args, **kwargs)

    @method_decorator(ratelimit(key=settings.RATELIMIT_KEY, rate='10/h', method='POST'))
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
        'elections': [
            (e, voter.can_vote(e), voter.application.filter(election=e).exists())
            for e in voter.session.elections.order_by('pk')
        ]
    }

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


@voter_login_required
def apply(request, election_id):
    voter = request.user

    election = get_object_or_404(voter.session.elections, pk=election_id)

    if not election.can_apply:
        messages.add_message(request, messages.ERROR, 'Applications are currently not accepted')
        return redirect('vote:index')

    application = voter.application.filter(election__id=election_id)
    instance = None
    if application.exists():
        instance = application.first()

    if request.method == 'GET':
        form = ApplicationUploadFormUser(election, request, instance=instance)
    else:
        form = ApplicationUploadFormUser(election, request, data=request.POST, files=request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('vote:index')

    context = {
        'form': form,
        'election': election,
        'with_email': True,
        'with_description': True,
    }
    return render(request, template_name='vote/application.html', context=context)


@voter_login_required
def delete_own_application(request, election_id):
    voter = request.user
    election = get_object_or_404(voter.session.elections, pk=election_id)
    application = voter.application.filter(election__id=election_id)
    if not election.can_apply:
        messages.add_message(request, messages.ERROR, 'Applications can currently not be deleted')
        return redirect('vote:index')
    if application.exists():
        instance = application.first()
        instance.delete()
        return redirect('vote:index')
    else:
        raise Http404('Application does not exist')
