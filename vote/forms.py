from crispy_forms.bootstrap import InlineRadios
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms
from django.contrib.auth import authenticate
from django.db import transaction

from django.utils.translation import gettext_lazy as _

from vote.models import Application, User, VOTE_CHOICES, Vote, VOTE_ABSTENTION, VOTE_ACCEPT


class TokenAuthenticationForm(forms.Form):
    error_messages = {
        'invalid_login': _(
            "Please enter a correct access code."
        ),
        'inactive': _("This access code is inactive."),
    }

    token = forms.CharField(label='code', max_length=100)

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        token = self.cleaned_data.get('token')

        if token:
            self.user_cache = authenticate(token=token)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login']
                )

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )

    def get_user(self):
        return self.user_cache


class ApplicationUploadForm(forms.ModelForm):
    first_name = forms.CharField(disabled=True)
    last_name = forms.CharField(disabled=True)

    field_order = ['first_name', 'last_name', 'email', 'text', 'avatar']

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = User.objects.get(token=request.user.username)
        self.request = request

        self.fields['first_name'].initial = self.user.first_name
        self.fields['last_name'].initial = self.user.last_name

    class Meta:
        model = Application
        fields = ('email', 'text', 'avatar')

    def clean(self):
        super().clean()
        if not self.user.election.can_apply:
            raise forms.ValidationError('Applications are currently not allowed')

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.user = self.user

        if commit:
            instance.save()

        return instance


class VoteBoundField(forms.BoundField):
    def __init__(self, form, field, name, application):
        super().__init__(form, field, name)
        self.application = application


class VoteField(forms.ChoiceField):
    def __init__(self, *, application, **kwargs):
        super().__init__(
            label=f'{application.user.first_name} {application.user.last_name}',
            choices=VOTE_CHOICES,
            widget=forms.RadioSelect(attrs={'class': 'vote-list'}),
            initial=VOTE_ABSTENTION,
            **kwargs
        )
        self.application = application

    def get_bound_field(self, form, field_name):
        return VoteBoundField(form, self, field_name, application=self.application)


class VoteForm(forms.Form):
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = User.objects.get(token=request.user.username)
        self.election = self.user.election
        self.request = request

        for application in self.election.applications:
            self.fields[f'{application.pk}'] = VoteField(application=application)

    def clean(self):
        super().clean()
        if not self.user.can_vote:
            raise forms.ValidationError('User is not allowed to vote')

        votes_yes = 0

        for application_pk, vote in self.cleaned_data.items():
            if vote == VOTE_ACCEPT:
                votes_yes += 1

        if votes_yes > self.user.election.max_votes_yes:
            raise forms.ValidationError(
                f'Too many "yes" votes, only max. {self.user.election.max_votes_yes} allowed.')

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
                Vote.objects.bulk_create(votes)
                self.user.voted = True
                self.user.save()

        return votes
