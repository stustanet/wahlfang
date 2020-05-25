import logging
from datetime import timedelta

from django.http import Http404
from django.shortcuts import render, redirect, reverse
from django.utils import timezone
from django.contrib import messages

from management.authentication import management_login_required
from management.forms import StartElectionForm, AddElectionForm,AddSessionForm, AddVotersForm, ApplicationUploadForm

from vote.models import Election, Application, Session
from management.models import ElectionManager

logger = logging.getLogger('management.view')


@management_login_required
def index(request):
    manager = ElectionManager.objects.get(id=request.user.pk)

    if request.GET.get("action") == "add_session":
        form = AddSessionForm(request=request,user=request.user, data=request.POST if request.POST else None)
        if request.POST and form.is_valid():
            ses = form.save()
            return redirect('management:session', ses.id)
        else:
            return render(request, template_name='management/add_session.html', context={'form': form})

    context = {
        'sessions': manager.sessions.all()
    }
    return render(request, template_name='management/index.html', context=context)


@management_login_required
def session(request, pk=None):
    manager = ElectionManager.objects.get(id=request.user.pk)
    meeting = manager.sessions.get(id=pk)
    context = {
        'session': meeting,
        'elections': meeting.elections.all(),
    }
    return render(request, template_name='management/session.html', context=context)


@management_login_required
def add_election(request, pk=None):
    manager = ElectionManager.objects.get(id=request.user.pk)
    meeting = manager.sessions.get(id=pk)
    context = {
        'session': meeting,
    }

    form = AddElectionForm(session=meeting, user=manager, data=request.POST if request.POST else None)
    context['form'] = form
    if request.POST and form.is_valid():
        elect = form.save()
        return redirect('management:session', meeting.id)
    else:
        return render(request, template_name='management/add_election.html', context=context)



@management_login_required
def add_voters(request, pk):
    manager = ElectionManager.objects.get(id=request.user.pk)
    meeting = manager.sessions.get(id=pk)
    context = {
        'session': meeting,
    }
    form = AddVotersForm(session=meeting, data=request.POST if request.POST else None)
    context['form'] = form
    if request.POST and form.is_valid():
        form.save()
        return redirect('management:session', pk=pk)
    else:
        return render(request, template_name='management/add_voters.html', context=context)

def _unpack(request, pk):
    manager = ElectionManager.objects.get(id=request.user.pk)
    election = Election.objects.get(id=pk)
    meeting = election.session
    if not manager.sessions.filter(pk=meeting.pk).exists():
        raise Http404('Election does not exist/insufficient rights')
    return manager, election, meeting

@management_login_required
def election(request, pk):
    manager, elect, meeting = _unpack(request, pk)
    context = {'election': elect,
               'session': meeting,
               'applications': elect.applications.all()}

    if request.POST and request.GET.get('action') == "close" and election.can_vote:
        election.end_date = timezone.now()
        election.save()

    if request.POST and request.GET.get('action') == "open":
        form = StartElectionForm(request.POST)
        if form.is_valid():
            run_time = form.cleaned_data['run_time']
            election.start_date = timezone.now()
            election.end_date = timezone.now() + timedelta(minutes=run_time)
            election.save()
        if not election.end_date:
            form = StartElectionForm()
        context['form'] = form

    return render(request, template_name='management/election.html', context=context)


@management_login_required
def election_upload_application(request, pk, application_id=None):
    manager, election, meeting = _unpack(request,pk)

    if not election.can_apply:
        messages.add_message(request, messages.ERROR, 'Applications are currently not accepted')
        return redirect('management:election' ,pk=pk)

    if application_id:
        try:
            instance = election.applications.get(pk=application_id)
        except Application.DoesNotExist:
            raise Http404("Application does not exist")
    else:
        instance = None

    if request.POST:
        form = ApplicationUploadForm(election, request, request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('management:election', election.pk)
    else:
        form = ApplicationUploadForm(election, request, instance=instance)

    context = {
        'form': form,
        'election': election,
        'application_id': application_id
    }
    return render(request, template_name='management/application.html', context=context)
