from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms
from django.contrib.auth import authenticate
from django.db import transaction

from django.utils.translation import gettext_lazy as _

from vote.models import Application, User, VOTE_CHOICES, Vote


class TokenAuthenticationForm(forms.Form):
    error_messages = {
        'invalid_login': _(
            "Please enter a correct %(username)s and password. Note that both "
            "fields may be case-sensitive."
        ),
        'inactive': _("This account is inactive."),
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
                    self.errors_messages['invalid_login']
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

    field_order = ['first_name', 'last_name', 'text', 'avatar']

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = User.objects.get(token=request.user.username)
        self.request = request

        self.fields['first_name'].initial = self.user.first_name
        self.fields['last_name'].initial = self.user.first_name

    class Meta:
        model = Application
        fields = ('text', 'avatar')

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.user = self.user

        if commit:
            instance.save()

        return instance


class VoteForm(forms.Form):
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = User.objects.get(token=request.user.username)
        self.election = self.user.election
        self.request = request

        for application in self.election.applications:
            self.fields[f'{application.pk}'] = forms.ChoiceField(
                label=f'{application.user.first_name} {application.user.last_name}',
                choices=VOTE_CHOICES,
                widget=forms.RadioSelect)

        self.helper = FormHelper()
        self.helper.layout = Layout()

    def clean(self):
        super().clean()
        if not self.user.can_vote:
            raise forms.ValidationError('User is not allowed to vote')

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