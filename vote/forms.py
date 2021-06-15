from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django import forms
from django.contrib.auth import authenticate
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from management.forms import ApplicationUploadForm
from vote.models import Application, Voter, OpenVote, VOTE_CHOICES, Vote, VOTE_ABSTENTION, VOTE_ACCEPT, \
    VOTE_CHOICES_NO_ABSTENTION


class AccessCodeAuthenticationForm(forms.Form):
    error_messages = {
        'invalid_login': _(
            "Invalid access code."
        )
    }

    access_code = forms.CharField(label='access code')

    def __init__(self, *args, request=None, **kwargs):
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


class EmptyForm(forms.Form):
    pass


class VoteBoundField(forms.BoundField):
    def __init__(self, form, field, name, application):
        super().__init__(form, field, name)
        self.application = application


class VoteField(forms.ChoiceField):
    def __init__(self, *, application, disable_abstention=False, **kwargs):
        super().__init__(
            label=application.get_display_name(),
            choices=VOTE_CHOICES_NO_ABSTENTION if disable_abstention else VOTE_CHOICES,
            widget=forms.RadioSelect(),
            initial=None if disable_abstention else VOTE_ABSTENTION,
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
        if self.election.max_votes_yes is not None:
            self.max_votes_yes = self.election.max_votes_yes
        else:
            self.max_votes_yes = self.election.applications.count()

        # dynamically construct form fields
        for application in self.election.applications:
            self.fields[f'{application.pk}'] = VoteField(application=application,
                                                         disable_abstention=self.election.disable_abstention)

        self.num_applications = len(self.election.applications)

    def clean(self):
        super().clean()
        if not OpenVote.objects.filter(election_id=self.election.pk, voter_id=self.voter.pk).exists():
            raise forms.ValidationError('You are not allowed to vote')

        votes_yes = 0

        for _, vote in self.cleaned_data.items():
            if vote == VOTE_ACCEPT:
                votes_yes += 1

        if votes_yes > self.max_votes_yes:
            raise forms.ValidationError(
                f'Too many "yes" votes, only max. {self.max_votes_yes} allowed.')

    def save(self, commit=True):
        votes = [
            Vote(
                election=self.election,
                candidate=Application.objects.get(pk=int(name)),
                vote=value
            ) for name, value in self.cleaned_data.items()
        ]

        # existence of can_vote object already checked in clean()
        can_vote = OpenVote.objects.get(election_id=self.election.pk, voter_id=self.voter.pk)

        if commit:
            with transaction.atomic():
                Vote.objects.bulk_create(votes)
                can_vote.delete()
            # notify manager that new votes were cast
            group = "Election-" + str(self.election.pk)
            async_to_sync(get_channel_layer().group_send)(
                group,
                {'type': 'send_reload', 'id': '#votes'}
            )

        return votes


class ApplicationUploadFormUser(ApplicationUploadForm):
    def __init__(self, election, request, *args, **kwargs):
        super().__init__(election, request, *args, **kwargs)
        if self.request.user.name:
            # these rules are meant for the StuStaNet Hausadmin election
            self.fields['display_name'].initial = self.request.user.name
            self.fields['display_name'].disabled = True
            self.fields['email'].required = True
        self.fields['email'].initial = self.request.user.email

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.voter = self.request.user
        instance.election = self.election

        if commit:
            instance.save()

        return instance
