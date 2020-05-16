from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from datetime import timedelta

from vote.models import Election
from management.forms import StartElectionForm


@staff_member_required(login_url='/management/login')
def index(request):
    context = {
        'elections': Election.objects.all()
    }

    return render(request, template_name='management/index.html', context=context)


@staff_member_required(login_url='/management/login')
def election(request, pk):
    election = get_object_or_404(Election, pk=pk)

    if request.POST:
        form = StartElectionForm(request.POST)
        if form.is_valid():
            run_time = form.cleaned_data['run_time']
            election.start_date = timezone.now()
            election.end_date = timezone.now() + timedelta(minutes=run_time)
            election.save()
    else:
        form = StartElectionForm()

    context = {
        'election': election,
        'form': form
    }
    if not election.closed:
        return render(request, template_name='management/election.html', context=context)

    context['applications'] = election.election_summary

    return render(request, template_name='management/election.html', context=context)
