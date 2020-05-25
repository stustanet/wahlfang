from django import forms

from vote.models import Election, Application


class StartElectionForm(forms.Form):
    run_time = forms.IntegerField(label="run time")


class AddElectionForm(forms.ModelForm):

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    class Meta:
        model = Election
        fields = ('title', 'max_votes_yes', 'start_date', 'end_date')
        labels = {
            'title': 'Name',
            'max_votes_yes': 'Maximale Anzahl an JA Stimmen',
            'start_date': 'Wahlbeginn (optional)',
            'end_date': 'Wahlende (optional)',
        }

    def save(self, commit=True):
        instance = super().save(commit=commit)

        self.user.elections.add(instance)
        if commit:
            self.user.save()

        return instance


class AvatarFileInput(forms.ClearableFileInput):
    template_name = 'vote/image_input.html'


class ApplicationUploadForm(forms.ModelForm):
    field_order = ['election', 'first_name', 'last_name', 'room', 'email', 'text', 'avatar']

    def __init__(self, election, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.election = election
        self.fields['election'].initial = self.election
        self.fields['election'].disabled = True

        self.request = request

    class Meta:
        model = Application
        fields = ('election', 'first_name', 'last_name', 'room', 'email', 'text', 'avatar')

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

    def __init__(self, election, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.election = election

    def save(self, commit=True):
        pass

    def clean(self):
        pass
