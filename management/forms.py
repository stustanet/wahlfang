import csv
import io
import re
from datetime import timedelta
from typing import Tuple, List

from django import forms
from django.core.validators import validate_email
from django.utils import timezone

from vote.models import Election, Application, Session, Voter, OpenVote


class StartElectionForm(forms.ModelForm):
    run_time = forms.IntegerField(label="run time")

    class Meta:
        model = Election
        fields: List[str] = []

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.start_date = timezone.now()
        instance.end_date = timezone.now() + timedelta(minutes=self.cleaned_data['run_time'])
        if commit:
            instance.save()

        return instance


class StopElectionForm(forms.ModelForm):
    class Meta:
        model = Election
        fields: List[str] = []

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.end_date = timezone.now()
        if commit:
            instance.save()

        return instance


class ChangeElectionPublicStateForm(forms.ModelForm):
    class Meta:
        model = Election
        fields = ['result_published']
        widgets = {
            'result_published': forms.RadioSelect
        }
        labels = {
            'result_published': '',
        }


class TemplateStringForm(forms.ModelForm):
    def clean_email_text(self, test_data: List[str], field: str):
        """
        checks if the cleaned_text fails when formatted on the test_data.
        """
        test_data_dict = {i: "" for i in test_data}
        cleaned_text = self.cleaned_data[field]
        try:
            test = cleaned_text.format(**test_data_dict)
        except (KeyError, ValueError, IndexError):
            x = re.findall(r"\{\w*\}", cleaned_text)
            test_data = set(x) - set([f"{{{i}}}" for i in test_data])
            self.add_error(field, "The following variables are not allowed: " + ", ".join(test_data))
        return cleaned_text


class AddSessionForm(TemplateStringForm):
    email = forms.EmailField(required=False, label="",
                             widget=forms.EmailInput(attrs={"class": "emailinput form-control",
                                                            "placeholder": "your@email.de"}))

    def __init__(self, request, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['start_date'].widget = forms.TextInput(attrs={'placeholder': 'e.g. 2020-05-12 13:00:00'})
        self.fields['meeting_link'].widget = forms.TextInput(
            attrs={'placeholder': 'e.g. https://bbb.stusta.de/b/ssn-abc-123'})
        self.user = user
        self.request = request

    class Meta:
        model = Session
        fields = ('title', 'start_date', 'meeting_link', 'invite_text')
        labels = {
            'title': 'Session Name',
            'start_date': 'Meeting start (optional)',
            'meeting_link': 'Link to meeting call platform (optional)',
            'invite_text': ''
        }

    def clean(self):
        super().clean()
        if self.request.POST.get("submit_type") == "test" and not self.cleaned_data['email']:
            self.add_error('email', "Email must be set for sending the test mail.")
        if self.request.POST.get("submit_type") == "test" and not self.cleaned_data['invite_text']:
            self.add_error('invite_text', "The test email can only be send when the invite text is filled.")
        return self.cleaned_data

    def clean_invite_text(self):
        test_data = ["name", "title", "access_code", "login_url", "base_url", "start_time",
                     "start_date", "meeting_link", "start_date_en", "start_time_en"]
        return self.clean_email_text(test_data, 'invite_text')

    def save(self, commit=True):
        instance = super().save(commit=commit)
        self.user.sessions.add(instance)
        if commit:
            self.user.save()

        return instance


class AddElectionForm(TemplateStringForm):
    email = forms.EmailField(required=False, label="",
                             widget=forms.EmailInput(attrs={"class": "emailinput form-control",
                                                            "placeholder": "your@email.de"}))

    def __init__(self, user, session, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['session'].disabled = True
        self.fields['session'].initial = session
        self.fields['session'].widget = forms.HiddenInput()
        self.fields['start_date'].widget = forms.TextInput(attrs={'placeholder': 'e.g.: 2020-05-12 13:00:00'})
        self.fields['end_date'].widget = forms.TextInput(attrs={'placeholder': 'e.g.: 2020-05-12 13:00:00'})
        # self.fields['start_date'].initial = timezone.now()
        self.fields['max_votes_yes'] = forms.IntegerField(min_value=1, required=False,
                                                          label='Maximum number of YES votes (optional)')
        self.user = user
        self.session = session
        self.request = request

    class Meta:
        model = Election
        fields = (
            'title', 'start_date', 'end_date', 'session', 'max_votes_yes', 'voters_self_apply', 'send_emails_on_start',
            'remind_text')

        labels = {
            'title': 'Election Name',
            'start_date': 'Start time (optional)',
            'end_date': 'End time (optional)',
            'voters_self_apply': 'Voters can apply for the election',
            'send_emails_on_start': 'Voters receive an e-mail when the election starts<br>'
                                    '(useful for elections that last several days)',
            'remind_text': '',
        }

    def clean_remind_text(self):
        test_data = ["name", "title", "url", "end_time", "end_date", "end_date_en", "end_time_en"]
        return self.clean_email_text(test_data, 'remind_text')

    def clean(self):
        super().clean()
        if self.session not in self.user.sessions.all():
            raise forms.ValidationError("You don't have the permission to add an election here.")
        if not self.cleaned_data['send_emails_on_start'] and self.cleaned_data['remind_text']:
            self.add_error('send_emails_on_start', "Remind text can only be set when this option is activated.")
        if self.request.POST.get("submit_type") == "test" and not self.cleaned_data['email']:
            self.add_error('email', "Email must be set for sending the test mail.")
        if self.request.POST.get("submit_type") == "test" and not self.cleaned_data['remind_text']:
            self.add_error('remind_text', "The test email can only be send when the remind text is filled.")
        if self.cleaned_data['end_date'] and self.cleaned_data['end_date'] < timezone.now():
            self.add_error('end_date', "End date cannot be in the past.")
        if self.cleaned_data.get('end_date') and self.cleaned_data.get('start_date') and \
                self.cleaned_data['start_date'] > self.cleaned_data['end_date']:
            raise forms.ValidationError("Start date needs to be before end date")
        return self.cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=commit)
        self.session.elections.add(instance)
        if commit:
            self.session.save()
            open_votes = [
                OpenVote(voter=v, election=instance)
                for v in self.session.participants.all()
            ]
            OpenVote.objects.bulk_create(open_votes)

        return instance


class AvatarFileInput(forms.ClearableFileInput):
    template_name = 'management/image_input.html'


class ApplicationUploadForm(forms.ModelForm):
    field_order = ['election', 'display_name', 'email', 'text', 'avatar']

    def __init__(self, election, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.election = election
        self.fields['election'].required = False

    class Meta:
        model = Application
        fields = ('election', 'display_name', 'email', 'text', 'avatar')

    def clean(self):
        super().clean()
        if not self.election.can_apply:
            raise forms.ValidationError('Applications are currently not allowed')
        return self.cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.election = self.election
        if commit:
            instance.save()

        return instance


class AddVotersForm(forms.Form):
    voters_list = forms.CharField(widget=forms.Textarea, label='Emails')  # explicitly no max_length here

    def __init__(self, session, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = session

    def save(self) -> List[Tuple[Voter, str]]:
        voters = [
            Voter.from_data(email=email, session=self.session) for email in self.cleaned_data['email_list']
        ]

        open_votes = []
        for election in self.session.elections.all():
            if not election.closed:
                open_votes += [OpenVote(election=election, voter=v) for v, _ in voters]

        OpenVote.objects.bulk_create(open_votes)

        for voter, code in voters:
            voter.send_invitation(code, self.session.managers.all().first().stusta_email)

        return voters

    def clean(self):
        super().clean()
        emails = self.cleaned_data['voters_list'].splitlines()
        for email in emails:
            validate_email(email)
            if Voter.objects.filter(email=email, session=self.session).exists():
                raise forms.ValidationError('voter with this email address already exists')

        if not len(emails) == len(set(emails)):
            raise forms.ValidationError('duplicate email address')

        self.cleaned_data['email_list'] = emails
        return self.cleaned_data


class AddTokensForm(forms.Form):
    nr_anonymous_voters = forms.IntegerField(min_value=1, max_value=50, label='Number of Tokens:')

    def __init__(self, session, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = session

    def save(self) -> List[Tuple[Voter, str]]:
        anonymous_voters = [
            Voter.from_data(session=self.session) for _ in range(self.cleaned_data['nr_anonymous_voters'])
        ]

        open_votes = []
        for election in self.session.elections.all():
            if not election.closed:
                open_votes += [OpenVote(election=election, voter=v) for v, _ in anonymous_voters]

        OpenVote.objects.bulk_create(open_votes)

        return anonymous_voters


class CSVUploaderForm(forms.Form):
    file = forms.FileField(label='CSV File')

    def __init__(self, session, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = session

    def clean(self):
        super().clean()
        f = self.cleaned_data['file'].file
        try:
            with io.TextIOWrapper(f, encoding='utf-8') as text_file:
                csv_reader = csv.DictReader(text_file)
                if csv_reader.fieldnames != ['email', 'name']:
                    raise forms.ValidationError('CSV file needs to have columns "email" and "name".')
                voters = []
                for row in csv_reader:
                    if row['email']:
                        validate_email(row['email'])
                    else:
                        row['email'] = None
                    voters.append(Voter.from_data(session=self.session, email=row['email'], name=row['name']))
        except UnicodeDecodeError:
            raise forms.ValidationError('File seems to be not in CSV format.')

        self.cleaned_data['file'] = voters
        return self.cleaned_data

    def save(self):
        for voter, code in self.cleaned_data['file']:
            voter.send_invitation(code, self.session.managers.all().first().stusta_email)
