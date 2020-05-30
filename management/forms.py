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
        fields = []

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
        fields = []

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.end_date = timezone.now()
        if commit:
            instance.save()

        return instance


class AddSessionForm(forms.ModelForm):
    def __init__(self, request, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['start_date'].widget = forms.TextInput(attrs={'placeholder': 'e.g.: 2020-05-12 13:00:00'})
        self.user = user
        self.request = request

    class Meta:
        model = Session
        fields = ('title', 'start_date', 'meeting_link')
        labels = {
            'title': 'Meeting name',
            'start_date': 'Meeting start (optional)',
            'meeting_link': 'Link to meeting call platform (optional)',
        }

    def save(self, commit=True):
        instance = super().save(commit=commit)
        self.user.sessions.add(instance)
        if commit:
            self.user.save()

        return instance


class AddElectionForm(forms.ModelForm):
    def __init__(self, user, session, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['session'].disabled = True
        self.fields['session'].initial = session
        self.fields['session'].widget = forms.HiddenInput()
        self.fields['start_date'].widget = forms.TextInput(attrs={'placeholder': 'e.g.: 2020-05-12 13:00:00'})
        self.fields['end_date'].widget = forms.TextInput(attrs={'placeholder': 'e.g.: 2020-05-12 13:00:00'})
        # self.fields['start_date'].initial = timezone.now()
        self.user = user
        self.session = session

    class Meta:
        model = Election
        fields = ('title', 'max_votes_yes', 'start_date', 'end_date', 'session')

        labels = {
            'title': 'Name',
            'max_votes_yes': 'Maximale Anzahl an JA Stimmen (optional)',
            'start_date': 'Wahlbeginn (optional)',
            'end_date': 'Wahlende (optional)',
        }

    def clean(self):
        super().clean()
        if self.session not in self.user.sessions.all():
            raise forms.ValidationError("You don't have the permission to add an election here.")

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
        self.fields['election'].initial = self.election
        self.fields['election'].disabled = True
        self.fields['election'].widget = forms.HiddenInput()

    class Meta:
        model = Application
        fields = ('election', 'display_name', 'email', 'text', 'avatar')

    def clean(self):
        super().clean()
        if not self.election.can_apply:
            raise forms.ValidationError('Applications are currently not allowed')

    def save(self, commit=True):
        instance = super().save(commit=False)

        if commit:
            instance.save()

        return instance


class AddVotersForm(forms.Form):
    voters_list = forms.CharField(widget=forms.Textarea, label='E-Mail Adressen')  # explicitly no max_length here

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
            voter.send_invitation(code)

        return voters

    def clean(self):
        emails = self.cleaned_data['voters_list'].splitlines()
        for email in emails:
            validate_email(email)
            if Voter.objects.filter(email=email, session=self.session).exists():
                raise forms.ValidationError('voter with this email address already exists')

        if not len(emails) == len(set(emails)):
            raise forms.ValidationError('duplicate email address')

        self.cleaned_data['email_list'] = emails
