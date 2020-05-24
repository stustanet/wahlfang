from datetime import timedelta

from django.http import Http404
from django.shortcuts import render, redirect
from django.utils import timezone

from management.authentication import management_login_required
from management.forms import StartElectionForm, AddElectionForm, AddVotersForm, AddApplicationForm


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
        return Http404('Election does not exist')

    context = {'election': election}

    if request.POST:
        if action == "close":
            if election.is_active:
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
def election_add_application(request, pk):
    election = request.user.get_election(pk=pk)
    if election is None:
        return Http404('Election does not exist')

    context = {
        'form': AddApplicationForm(election=election),
        'election': election
    }

    if request.POST:
        form = AddApplicationForm(election=election, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            return redirect('management:index')

        context['form'] = form

    return render(request, template_name='management/add_application.html', context=context)


@management_login_required(login_url='/management/login')
def election_add_voters(request, pk):
    election = request.user.get_election(pk=pk)
    if election is None:
        return Http404('Election does not exist')

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
