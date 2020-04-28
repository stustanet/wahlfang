from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404

from vote.models import Election


@staff_member_required(login_url='/management/login')
def index(request):
    context = {
        'elections': Election.objects.all()
    }

    return render(request, template_name='management/index.html', context=context)


@staff_member_required(login_url='/management/login')
def election_result(request, pk):
    election = get_object_or_404(Election, pk=pk)
    context = {
        'election': election
    }
    if not election.closed:
        return render(request, template_name='management/election_result.html', context=context)

    context = {
        'election': election,
        'applications': election.election_summary
    }

    return render(request, template_name='management/election_result.html', context=context)
