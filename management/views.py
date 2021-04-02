import csv
import logging
import os
from argparse import Namespace
from functools import partial
from pathlib import Path
from typing import Dict

import qrcode
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.http import Http404, HttpResponse
from django.http.response import HttpResponseNotFound
from django.shortcuts import render, redirect, resolve_url
from django.template.loader import get_template
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from latex.build import PdfLatexBuilder
from ratelimit.decorators import ratelimit

from management.authentication import management_login_required
from management.forms import (
    StartElectionForm,
    AddElectionForm,
    AddSessionForm,
    AddVotersForm,
    ApplicationUploadForm,
    StopElectionForm,
    ChangeElectionPublicStateForm,
    AddTokensForm,
    CSVUploaderForm,
    SessionSettingsForm
)
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

    def get_success_url(self):
        url = self.get_redirect_url()
        return url or resolve_url('management:index')


@management_login_required
def index(request):
    manager = request.user

    if request.GET.get("action") == "add_session":
        form = AddSessionForm(request=request, user=request.user, data=request.POST or None)
        if request.POST and form.is_valid():

            if request.POST.get("submit_type") != "test":
                ses = form.save()
                return redirect('management:session', ses.id)

            messages.add_message(request, messages.INFO, 'Test email sent.')
            Voter.send_test_invitation(
                title=form.cleaned_data['title'],
                start_date=form.cleaned_data['start_date'] if form.cleaned_data['start_date'] else timezone.now(),
                meeting_link=form.cleaned_data['meeting_link'],
                invite_text=form.cleaned_data['invite_text'],
                to_email=form.cleaned_data['email'],
                from_email=manager.sender_email
            )

        return render(request, template_name='management/add_session.html',
                      context={'form': form, 'variables': form.variables})

    context = {
        'sessions': manager.sessions.order_by('-pk')
    }
    return render(request, template_name='management/index.html', context=context)


@management_login_required
def session_detail(request, pk=None):
    manager = request.user
    session = manager.sessions.get(id=pk)
    elections = session.elections.order_by('pk')
    existing_elections = bool(elections)
    open_elections = [e for e in elections if e.is_open]
    upcoming_elections = [e for e in elections if not e.started]
    published_elections = [e for e in elections if e.closed and int(e.result_published)]
    closed_elections = [e for e in elections if e.closed and not int(e.result_published)]
    context = {
        'session': session,
        'existing_elections': existing_elections,
        'open_elections': open_elections,
        'upcoming_elections': upcoming_elections,
        'published_elections': published_elections,
        'closed_elections': closed_elections,
        'voters': session.participants.all()
    }
    return render(request, template_name='management/session.html', context=context)


@management_login_required
def session_settings(request, pk=None):
    manager = request.user
    session = manager.sessions.get(pk=pk)

    form = SessionSettingsForm(instance=session, request=request, user=request.user, data=request.POST or None)
    if request.POST:
        if form.is_valid():
            if request.POST.get("submit_type") == "test":
                messages.add_message(request, messages.INFO, 'Test email sent.')
                Voter.send_test_invitation(
                    title=form.cleaned_data['title'],
                    start_date=form.cleaned_data['start_date'] if form.cleaned_data['start_date'] else timezone.now(),
                    meeting_link=form.cleaned_data['meeting_link'],
                    invite_text=form.cleaned_data['invite_text'],
                    to_email=form.cleaned_data['email'],
                    from_email=manager.sender_email
                )
            else:
                form.save()
                messages.add_message(request, messages.INFO, 'Session updated successfully!')
                return redirect('management:session', session.id)

    context = {
        'session': session,
        'elections': session.elections.order_by('pk'),
        'voters': session.participants.all(),
        'variables': form.variables,
        'form': form
    }
    return render(request, template_name='management/session_settings.html', context=context)


@management_login_required
def add_election(request, pk=None):
    manager = request.user
    session = manager.sessions.get(pk=pk)
    context = {
        'session': session,
    }

    form = AddElectionForm(session=session, request=request, user=manager, data=request.POST if request.POST else None)
    context['form'] = form
    context['variables'] = form.variables
    if request.POST and form.is_valid():
        if request.POST.get("submit_type") == "test":
            messages.add_message(request, messages.INFO, 'Test email sent.')

            test_voter = Namespace(**{
                "name": "Testname",
                "email": form.cleaned_data['email'],
            })
            test_voter.email_user = partial(Voter.email_user, test_voter)
            test_election = Namespace(**{
                "title": form.cleaned_data['title'],
                "remind_text": form.cleaned_data['remind_text'],
                "pk": 1,
                "end_date": form.cleaned_data['end_date'],
            })

            Voter.send_reminder(test_voter, manager.sender_email, test_election)
        else:
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


@management_login_required
def add_tokens(request, pk):
    manager = request.user
    session = manager.sessions.get(pk=pk)
    context = {
        'session': session,
        'form': AddTokensForm(session=session)
    }
    form = AddTokensForm(session=session, data=request.POST if request.POST else None)
    context['form'] = form
    if request.POST and form.is_valid():
        form.save()
        return redirect('management:session', pk=pk)

    return render(request, template_name='management/add_tokens.html', context=context)


def _unpack(request, pk):
    manager = request.user
    election = Election.objects.get(pk=pk)
    session = election.session
    if not manager.sessions.filter(pk=session.pk).exists():
        raise Http404('Election does not exist/insufficient rights')
    return manager, election, session


@management_login_required
def election_detail(request, pk):
    _, election, session = _unpack(request, pk)
    context = {
        'election': election,
        'session': session,
        'applications': election.applications.all(),
        'stop_election_form': StopElectionForm(instance=election),
        'start_election_form': StartElectionForm(instance=election),
        'election_upload_application_form': ChangeElectionPublicStateForm(instance=election)
    }

    if request.POST and request.POST.get('action') == 'close' and election.is_open:
        form = StopElectionForm(instance=election, data=request.POST)
        if form.is_valid():
            form.save()
        else:
            context['stop_election_form'] = form

    if request.POST and request.POST.get('action') == 'open':
        form = StartElectionForm(instance=election, data=request.POST)
        if form.is_valid():
            form.save()
            if election.send_emails_on_start:
                for voter in session.participants.all():
                    voter.send_reminder(session.managers.all().first().sender_email, election)
        else:
            context['start_election_form'] = form

    if request.POST and request.POST.get('action') == 'publish':
        form = ChangeElectionPublicStateForm(instance=election, data=request.POST)
        if form.is_valid():
            form.save()
            context['election_upload_application_form'] = form

    return render(request, template_name='management/election.html', context=context)


@management_login_required
def election_upload_application(request, pk, application_id=None):
    _, election, _ = _unpack(request, pk)

    if not election.can_apply:
        messages.add_message(request, messages.ERROR, 'Applications are currently not accepted')
        return redirect('management:election', pk=pk)

    if application_id:
        try:
            instance = election.applications.get(pk=application_id)
        except Application.DoesNotExist:
            return HttpResponseNotFound('Application does not exist')
    else:
        instance = None

    if request.method == 'GET':
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
        return HttpResponseNotFound('Election does not exist')
    e = e.first()
    try:
        a = e.applications.get(pk=application_id)
    except Application.DoesNotExist:
        return HttpResponseNotFound('Application does not exist')
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
        return HttpResponseNotFound('Election does not exist')
    e = e.first()
    session = e.session
    e.delete()
    return redirect('management:session', pk=session.pk)


@management_login_required
@csrf_protect
def delete_session(request, pk):
    s = request.user.sessions.filter(pk=pk)
    if not s.exists():
        return HttpResponseNotFound('Session does not exist')
    s = s.first()
    s.delete()
    return redirect('management:index')


@management_login_required
def print_token(request, pk):
    session = request.user.sessions.filter(pk=pk)
    if not session.exists():
        return HttpResponseNotFound('Session does not exist')
    session = session.first()
    participants = session.participants
    tokens = [participant.new_access_token() for participant in participants.all() if participant.is_anonymous]
    if len(tokens) == 0:
        messages.add_message(request, messages.ERROR, 'No tokens have yet been generated.')
        return redirect('management:session', pk=session.pk)

    img = [qrcode.make(f'https://{settings.URL}' + reverse('vote:link_login', kwargs={'access_code': access_code}))
           for access_code in tokens]
    tmp_qr_path = '/tmp/wahlfang/qr_codes/session_{}'.format(session.pk)
    Path(tmp_qr_path).mkdir(parents=True, exist_ok=True)
    if session.meeting_link:
        meeting_qr_path = os.path.join(tmp_qr_path, 'qr_meeting.png')
        qrcode.make(session.meeting_link).save(meeting_qr_path)
    else:
        meeting_qr_path = None

    paths = []
    for idx, i in enumerate(img):
        path_i = os.path.join(tmp_qr_path, 'qr_{}.png'.format(idx))
        i.save(path_i)
        paths.append(path_i)
    zipped = [{'path': path, 'token': token} for path, token in zip(paths, tokens)]
    context = {
        'session': session,
        'tokens': zipped,
        'meeting_link_qr': meeting_qr_path
    }

    template_name = 'vote/tex/invitation.tex'
    pdf = generate_pdf(template_name, context, tmp_qr_path)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="tokenlist.pdf"'
    response.write(bytes(pdf))
    return response


def generate_pdf(template_name: str, context: Dict, tex_path: str):
    template = get_template(template_name).render(context).encode('utf8')
    with open("/tmp/template.tex", "wb") as f:
        f.write(template)
    pdf = PdfLatexBuilder(pdflatex='pdflatex').build_pdf(template, texinputs=[tex_path, ''])
    return pdf


@management_login_required
def import_csv(request, pk):
    session = request.user.sessions.filter(pk=pk)
    if not session.exists():
        return HttpResponseNotFound('Session does not exist')
    session = session.first()

    if request.method == 'POST':
        form = CSVUploaderForm(session, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            return redirect('management:session', session.pk)
    else:
        form = CSVUploaderForm(session)
    return render(request, 'management/import_csv.html', {'form': form, 'session': session})


@management_login_required
def export_csv(request, pk):
    e = Election.objects.filter(session__in=request.user.sessions.all(), pk=pk)
    if not e.exists():
        return HttpResponseNotFound('Election does not exist')
    e = e.first()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="results.csv"'

    writer = csv.writer(response)
    header = ['#', 'applicant', 'email', 'yes', 'no', 'abstention']
    if e.max_votes_yes is not None:
        header.append('elected')
    writer.writerow(header)
    for i, applicant in enumerate(e.election_summary):
        row = [i + 1, applicant.get_display_name(), applicant.email, applicant.votes_accept, applicant.votes_reject,
               applicant.votes_abstention]
        if e.max_votes_yes is not None:
            row.append(i < e.max_votes_yes)
        writer.writerow(row)

    return response


@management_login_required
def spectator(request, pk):
    session = request.user.sessions.filter(pk=pk)
    if not session.exists():
        return HttpResponseNotFound('Session does not exist')
    session = session.first()
    if request.POST:
        do = request.POST.get("do-type")
        if do == "create":
            session.create_spectator_token()
        elif do == "delete":
            session.spectator_token = None
            session.save()
    context = {
        'token_url': request.build_absolute_uri(
            reverse('vote:spectator', kwargs={'uuid': session.spectator_token})) if session.spectator_token else None,
        'pk': session.pk,
    }
    return render(request, template_name='management/spectator_settings.html', context=context)
