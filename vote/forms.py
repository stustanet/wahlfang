from django import forms
from django.contrib.auth import authenticate
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from vote.models import Application, Voter, OpenVote, VOTE_CHOICES, Vote, VOTE_ABSTENTION, VOTE_ACCEPT, Election


class AccessCodeAuthenticationForm(forms.Form):
    error_messages = {
        'invalid_login': _(
            "Invalid access code."
        )
    }

    access_code = forms.CharField(label='access code')

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

        # self.fields['access_code'].max_length = 128

    def clean(self):
        access_code = self.cleaned_data.get('access_code')
        if access_code:
            self.user_cache = authenticate(self.request, access_code=access_code)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                )

        return self.cleaned_data

    def get_user(self):
        return self.user_cache


class AvatarFileInput(forms.ClearableFileInput):
    template_name = 'vote/image_input.html'


class ApplicationUploadForm(forms.ModelForm):
    field_order = ['first_name', 'last_name', 'email', 'text', 'avatar']

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.voter = Voter.objects.get(voter_id=request.user.voter_id)

        self.fields['avatar'].widget = AvatarFileInput()
        self.fields['first_name'].initial = self.voter.first_name
        self.fields['last_name'].initial = self.voter.last_name
        self.fields['email'].initial = self.voter.email

    class Meta:
        model = Application
        fields = ('first_name', 'last_name', 'email', 'text', 'avatar')

    def clean(self):
        super().clean()
        if not self.voter.election.can_apply:
            raise forms.ValidationError('Applications are currently not allowed')

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.voter = self.voter

        if commit:
            instance.save()

        return instance


class EmptyForm(forms.Form):
    pass


class VoteBoundField(forms.BoundField):
    def __init__(self, form, field, name, application):
        super().__init__(form, field, name)
        self.application = application


class VoteField(forms.ChoiceField):
    def __init__(self, *, application, **kwargs):
        super().__init__(
            label=application.get_display_name(),
            choices=VOTE_CHOICES,
            widget=forms.RadioSelect(),
            initial=VOTE_ABSTENTION,
            **kwargs
        )
        self.application = application

    def get_bound_field(self, form, field_name):
        return VoteBoundField(form, self, field_name, application=self.application)


class VoteForm(forms.Form):
    def __init__(self, request, election, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.voter = Voter.objects.get(voter_id=request.user.voter_id)
        self.election = election
        self.request = request

        for application in self.election.applications:
            self.fields[f'{application.pk}'] = VoteField(application=application)

        self.num_applications = len(self.election.applications)

    def clean(self):
        super().clean()
        if not OpenVote.objects.get(election_id=self.election.id, voter_id=self.voter.id):
            raise forms.ValidationError('You are not allowed to vote')

        votes_yes = 0

        for application_pk, vote in self.cleaned_data.items():
            if vote == VOTE_ACCEPT:
                votes_yes += 1

        if votes_yes > self.voter.election.max_votes_yes:
            raise forms.ValidationError(
                f'Too many "yes" votes, only max. {self.voter.election.max_votes_yes} allowed.')

    def save(self, commit=True):
        votes = [
            Vote(
                election=self.election,
                candidate=Application.objects.get(pk=int(name)),
                vote=value
            ) for name, value in self.cleaned_data.items()
        ]

        if commit:
            with transaction.atomic():
                can_vote = OpenVote.objects.get(election_id=self.election.id, voter_id=self.voter.id)
                if not can_vote:
                    raise forms.ValidationError('You are not allowed to vote')
                Vote.objects.bulk_create(votes)
                can_vote.delete()
        return votes
