import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.http import Http404
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from ratelimit.decorators import ratelimit

from management.authentication import management_login_required
from management.forms import StartElectionForm, AddElectionForm, AddSessionForm, AddVotersForm, ApplicationUploadForm, \
    StopElectionForm, ChangeElectionPublicStateForm
from vote.models import Election, Application, Voter

logger = logging.getLogger('management.view')


class LoginView(auth_views.LoginView):
    # login view settings
    # https://docs.djangoproject.com/en/3.0/topics/auth/default/#django.contrib.auth.views.LoginView
    template_name = 'management/login.html'

    @method_decorator(ratelimit(key=settings.RATELIMIT_KEY, rate='10/h', method='POST'))
    def post(self, request, *args, **kwargs):
        ratelimited = getattr(request, 'limited', False)
        if ratelimited:
            return render(request, template_name='vote/ratelimited.html', status=429)
        return super().post(request, *args, **kwargs)


@management_login_required
def index(request):
    manager = request.user

    if request.GET.get("action") == "add_session":
        form = AddSessionForm(request=request, user=request.user, data=request.POST if request.POST else None)
        if request.POST and form.is_valid():
            ses = form.save()
            return redirect('management:session', ses.id)
        else:
            return render(request, template_name='management/add_session.html', context={'form': form})

    context = {
        'sessions': manager.sessions.order_by('-pk')
    }
    return render(request, template_name='management/index.html', context=context)


@management_login_required
def session_detail(request, pk=None):
    manager = request.user
    session = manager.sessions.get(id=pk)
    context = {
        'session': session,
        'elections': session.elections.order_by('pk'),
        'voters': session.participants.all()
    }
    return render(request, template_name='management/session.html', context=context)


@management_login_required
def add_election(request, pk=None):
    manager = request.user
    session = manager.sessions.get(id=pk)
    context = {
        'session': session,
    }

    form = AddElectionForm(session=session, user=manager, data=request.POST if request.POST else None)
    context['form'] = form
    if request.POST and form.is_valid():
        form.save()
        return redirect('management:session', pk=session.pk)

    return render(request, template_name='management/add_election.html', context=context)


@management_login_required
def add_voters(request, pk):
    manager = request.user
    session = manager.sessions.get(pk=pk)
    context = {
        'session': session,
        'form': AddVotersForm(session=session)
    }
    form = AddVotersForm(session=session, data=request.POST if request.POST else None)
    context['form'] = form
    if request.POST and form.is_valid():
        form.save()
        return redirect('management:session', pk=pk)

    return render(request, template_name='management/add_voters.html', context=context)


def _unpack(request, pk):
    manager = request.user
    election = Election.objects.get(pk=pk)
    session = election.session
    if not manager.sessions.filter(pk=session.pk).exists():
        raise Http404('Election does not exist/insufficient rights')
    return manager, election, session


@management_login_required
def election_detail(request, pk):
    manager, election, session = _unpack(request, pk)
    context = {
        'election': election,
        'session': session,
        'applications': election.applications.all(),
        'stop_election_form': StopElectionForm(instance=election),
        'start_election_form': StartElectionForm(instance=election),
        'election_upload_application_form': ChangeElectionPublicStateForm(instance=election)
    }

    if request.POST and request.POST.get('action') == "close" and election.is_open:
        form = StopElectionForm(instance=election, data=request.POST)
        if form.is_valid():
            form.save()
        else:
            context['stop_election_form'] = form

    if request.POST and request.POST.get('action') == "open":
        form = StartElectionForm(instance=election, data=request.POST)
        if form.is_valid():
            form.save()
        else:
            context['start_election_form'] = form

    if request.POST and request.POST.get('action') == "publish":
        form = ChangeElectionPublicStateForm(instance=election, data=request.POST)
        if form.is_valid():
            form.save()
            context['election_upload_application_form'] = form

    return render(request, template_name='management/election.html', context=context)


@management_login_required
def election_upload_application(request, pk, application_id=None):
    manager, election, meeting = _unpack(request, pk)

    if not election.can_apply:
        messages.add_message(request, messages.ERROR, 'Applications are currently not accepted')
        return redirect('management:election', pk=pk)

    if application_id:
        try:
            instance = election.applications.get(pk=application_id)
        except Application.DoesNotExist:
            raise Http404("Application does not exist")
    else:
        instance = None

    if request.POST.get("action") == "edit":
        form = ApplicationUploadForm(election, request, instance=instance)
    else:
        form = ApplicationUploadForm(election, request, data=request.POST, files=request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('management:election', election.pk)

    context = {
        'form': form,
        'election': election,
        'application_id': application_id,
        'with_email': False,
        'with_description': False,
    }
    return render(request, template_name='management/application.html', context=context)


@management_login_required
def election_delete_application(request, pk, application_id):
    e = Election.objects.filter(session__in=request.user.sessions.all(), pk=pk)
    if not e.exists():
        raise Http404('Election does not exist')
    e = e.first()
    try:
        a = e.applications.get(pk=application_id)
    except Application.DoesNotExist:
        raise Http404('Application does not exist')
    a.delete()
    return redirect('management:election', pk=pk)


@management_login_required
@csrf_protect
def delete_voter(request, pk):
    v = Voter.objects.filter(session__in=request.user.sessions.all(), pk=pk)
    if not v.exists():
        raise Http404('Voter does not exist')
    v = v.first()
    session = v.session
    v.delete()
    return redirect('management:session', pk=session.pk)


@management_login_required
@csrf_protect
def delete_election(request, pk):
    e = Election.objects.filter(session__in=request.user.sessions.all(), pk=pk)
    if not e.exists():
        raise Http404('Election does not exist')
    e = e.first()
    session = e.session
    e.delete()
    return redirect('management:session', pk=session.pk)


@management_login_required
@csrf_protect
def delete_session(request, pk):
    s = request.user.sessions.filter(pk=pk)
    if not s.exists():
        raise Http404('Session does not exist')
    s = s.first()
    s.delete()
    return redirect('management:index')
