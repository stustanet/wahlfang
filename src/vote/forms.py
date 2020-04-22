from django import forms

from vote.models import Candidate


class ApplicationUploadForm(forms.ModelForm):

    class Meta:
        model = Candidate
