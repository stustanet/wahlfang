import csv
import io
import re
from datetime import timedelta
from typing import Tuple, List

from django import forms
from django.conf import settings
from django.core.validators import validate_email
from django.utils import timezone

from management.models import ElectionManager
from vote.models import Election, Application, Session, Voter, OpenVote


class StartElectionForm(forms.ModelForm):
    run_time = forms.IntegerField(label="run time", min_value=1)

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


class TemplateStringForm:
    def clean_email_text(self, test_data: List[str], field: str):
        """
        checks if the cleaned_text fails when formatted on the test_data.
        """
        test_data_dict = {i: "" for i in test_data}
        cleaned_text = self.cleaned_data[field]
        try:
            cleaned_text.format(**test_data_dict)
        except (KeyError, ValueError, IndexError):
            x = re.findall(r"\{\w*\}", cleaned_text)
            test_data = set(x) - {f"{{{i}}}" for i in test_data}
            self.add_error(field, "The following variables are not allowed: " + ", ".join(test_data))
        return cleaned_text


class AddSessionForm(forms.ModelForm, TemplateStringForm):
    variables = {
        "{name}": "Voter's name if set",
        "{title}": "Session's title",
        "{access_code}": "Access code/token for the voter to login",
        "{login_url}": "URL which instantly logs user in",
        "{base_url}": f"Will render to: https://{settings.URL}",
        "{start_time}": "Start time if datetime is set",
        "{start_date}": "Start date if datetime is set",
        "{start_time_en}": "Start time in english format e.g. 02:23 PM",
        "{start_date_en}": "Start date in english format e.g. 12/12/2020",
        "{meeting_link}": "Meeting link if set"
    }

    email = forms.EmailField(required=False, label="",
                             widget=forms.EmailInput(attrs={"class": "emailinput form-control",
                                                            "placeholder": "your@email.de"}))

    def __init__(self, request, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['start_date'].widget = forms.TextInput(attrs={'placeholder': 'e.g. 2020-05-12 13:00:00',
                                                                  'type': 'datetime'})
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
            # will be set by html
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

    def _save_m2m(self):
        super()._save_m2m()

        if not self.user.sessions.filter(pk=self.instance.pk):
            self.user.sessions.add(self.instance)
            self.user.save()

    def save(self, commit=True):
        self.instance = super().save(commit=False)

        if commit:
            self.instance.save()
            self._save_m2m()
        else:
            self.save_m2m = self._save_m2m  # pylint: disable=attribute-defined-outside-init

        return self.instance


class SessionSettingsForm(AddSessionForm):
    add_election_manager = forms.CharField(max_length=256, required=False, label='')

    class Meta:
        model = Session
        fields = ('start_date', 'meeting_link', 'invite_text')
        labels = {
            'start_date': 'Meeting start (optional)',
            'meeting_link': 'Link to meeting call platform (optional)',
            # will be set by html
            'invite_text': ''
        }
        widgets = {
            'start_date': forms.TextInput(attrs={'placeholder': 'e.g. 2020-05-12 13:00:00', 'type': 'datetime'})
        }

    def clean_add_election_manager(self):
        value = self.data['add_election_manager']
        if not value:
            return value
        if not ElectionManager.objects.filter(username=value).exists():
            raise forms.ValidationError(f'Cannot find election manager with username {value}')

        return ElectionManager.objects.get(username=value)

    def _save_m2m(self):
        super()._save_m2m()

        if self.cleaned_data['add_election_manager']:
            self.cleaned_data['add_election_manager'].sessions.add(self.instance)
            self.cleaned_data['add_election_manager'].save()

    def save(self, commit=True):
        self.instance = super().save(commit=False)
        if commit:
            self.instance.save()
            self._save_m2m()
        else:
            self.save_m2m = self._save_m2m  # pylint: disable=attribute-defined-outside-init

        return self.instance


class AddElectionForm(forms.ModelForm, TemplateStringForm):
    variables = {
        "{name}": "Voter's name if set",
        "{title}": "Session's title",
        "{url}": "URL to the election",
        "{end_time}": "End time if datetime is set",
        "{end_date}": "End date if datetime is set",
        "{end_time_en}": "End time in english format e.g. 02:23 PM",
        "{end_date_en}": "End date in english format e.g. 12/12/2020",
    }

    email = forms.EmailField(required=False, label="",
                             widget=forms.EmailInput(attrs={"class": "emailinput form-control",
                                                            "placeholder": "your@email.de"}))

    def __init__(self, user, session, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['session'].disabled = True
        self.fields['session'].initial = session
        self.fields['session'].widget = forms.HiddenInput()
        self.fields['start_date'].widget = forms.TextInput(
            attrs={'placeholder': 'e.g.: 2020-05-12 13:00:00', 'type': 'datetime'})
        self.fields['end_date'].widget = forms.TextInput(
            attrs={'placeholder': 'e.g.: 2020-05-12 13:00:00', 'type': 'datetime'})
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
            'remind_text', 'disable_abstention')

        labels = {
            'title': 'Election Name',
            'start_date': 'Start time (optional)',
            'end_date': 'End time (optional)',
            'voters_self_apply': 'Voters can apply for the election',
            'send_emails_on_start': 'Voters receive an e-mail when the election starts<br>'
                                    '(useful for elections that last several days)',
            'disable_abstention': 'Disable the option to abstain in this election<br>'
                                  '(only YES and NO votes will be allowed)',
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
        voters_codes = [
            Voter.from_data(email=email, session=self.session) for email in self.cleaned_data['voters_list']
        ]
        self.session.managers.all().first().send_invite_bulk_threaded(voters_codes)
        return voters_codes

    def clean_voters_list(self):
        lines = self.cleaned_data['voters_list'].splitlines()
        emails = []
        for line in lines:
            if line == '':
                continue

            try:
                validate_email(line)
            except forms.ValidationError:
                self.add_error('voters_list', f'{line} is not a valid email address')

            if Voter.objects.filter(email=line, session=self.session).exists():
                self.add_error('voters_list', f'a voter with email address {line} already exists')

            emails.append(line)

        if len(emails) != len(set(emails)):
            raise forms.ValidationError('duplicate email address')

        return emails


class AddTokensForm(forms.Form):
    nr_anonymous_voters = forms.IntegerField(min_value=1, max_value=50, label='Number of Tokens:')

    def __init__(self, session, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = session

    def save(self) -> List[Tuple[Voter, str]]:
        anonymous_voters = [
            Voter.from_data(session=self.session) for _ in range(self.cleaned_data['nr_anonymous_voters'])
        ]

        return anonymous_voters


class CSVUploaderForm(forms.Form):
    csv_data = forms.FileField(label='CSV File')

    def __init__(self, session, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = session

    def clean_csv_data(self):
        f = self.cleaned_data['csv_data'].file
        data = {}
        try:
            with io.TextIOWrapper(f, encoding='utf-8') as text_file:
                csv_reader = csv.DictReader(text_file)
                if 'email' not in csv_reader.fieldnames or 'name' not in csv_reader.fieldnames:
                    raise forms.ValidationError('CSV file needs to have columns "email" and "name".')
                for row in csv_reader:
                    if row['email']:
                        try:
                            validate_email(row['email'])
                        except forms.ValidationError:
                            self.add_error('csv_data', f'Invalid email {row["email"]}')
                    else:
                        row['email'] = None

                    if Voter.objects.filter(session=self.session, email=row['email']).exists():
                        self.add_error('csv_data', f'Voter with email address {row["email"]} already exists')

                    if row['email'] in data:
                        self.add_error('csv_data', f'Duplicate email in csv: {row["email"]}')

                    data[row['email']] = row['name']
        except UnicodeDecodeError as e:
            raise forms.ValidationError('File does not seem to be in CSV format.') from e

        return data

    def save(self):
        voters_codes = [
            Voter.from_data(session=self.session, email=email, name=name)
            for email, name in self.cleaned_data['csv_data'].items()
        ]
        self.session.managers.all().first().send_invite_bulk_threaded(voters_codes)
