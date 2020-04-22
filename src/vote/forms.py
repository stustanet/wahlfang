from django import forms
from django.contrib.auth import authenticate

from django.utils.translation import gettext_lazy as _

from vote.models import Application


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
    class Meta:
        model = Application
        fields = '__all__'
