from datetime import timedelta

from django.http import Http404
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages

from management.authentication import management_login_required
from management.forms import StartElectionForm, AddElectionForm, AddVotersForm, ApplicationUploadForm

from vote.models import Election, Application


@management_login_required(login_url='/management/login')
def index(request):
    context = {
        'elections': request.user.elections.all()
    }

    return render(request, template_name='management/index.html', context=context)


@management_login_required(login_url='/management/login')
def election(request, pk, action=None):
    election = request.user.get_election(pk=pk)
    if election is None:
        raise Http404('Election does not exist')

    context = {'election': election}

    if request.POST:
        action = request.POST.get("action", None)
        if action == "close":
            if election.can_vote:
                election.end_date = timezone.now()
                election.save()
            else:
                pass
        elif action == "open":
            form = StartElectionForm(request.POST)
            context['form'] = form
            if form.is_valid():
                run_time = form.cleaned_data['run_time']
                election.start_date = timezone.now()
                election.end_date = timezone.now() + timedelta(minutes=run_time)
                election.save()
            else:
                pass
        else:
            pass
    elif not election.end_date:
        form = StartElectionForm()
        context['form'] = form
    else:
        pass

    if not election.closed:
        context['applications'] = election.applications.all()
    else:
        context['applications'] = election.election_summary

    return render(request, template_name='management/election.html', context=context)


@management_login_required(login_url='/management/login')
def add_election(request):
    context = {
        'form': AddElectionForm(user=request.user)
    }

    if request.POST:
        form = AddElectionForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('management:index')

        context['form'] = form

    return render(request, template_name='management/add_election.html', context=context)


@management_login_required(login_url='/management/login')
def election_add_voters(request, pk):
    election = request.user.get_election(pk=pk)
    if election is None:
        raise Http404('Election does not exist')

    context = {
        'form': AddVotersForm(election=election),
        'election': election
    }

    if request.POST:
        form = AddVotersForm(election=election, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('management:election', pk=pk)

        context['form'] = form

    return render(request, template_name='management/election_add_voters.html', context=context)


@management_login_required(login_url='/management/login')
def election_upload_application(request, pk, application_id=None):
    election = request.user.get_election(pk=pk)
    if election is None:
        raise Http404('Election does not exist')

    if not election.can_apply:
        messages.add_message(request, messages.ERROR, 'Applications are currently not accepted')
        return redirect('management:index')

    if application_id:
        try:
            instance = Application.objects.get(pk=application_id)
            if instance.election_id != election.pk:
                raise Http404("Application does not exist")
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
