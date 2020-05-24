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
        fields = ('title', 'max_votes_yes', 'start_date', 'end_date', 'application_due_date')
        labels = {
            'title': 'Name',
            'max_votes_yes': 'Maximale Anzahl an JA Stimmen',
            'start_date': 'Wahlbeginn (optional)',
            'end_date': 'Wahlende (optional)',
            'application_due_date': 'Deadline für Bewerbungen (optional)'
        }

    def save(self, commit=True):
        instance = super().save(commit=commit)

        self.user.elections.add(instance)
        if commit:
            self.user.save()

        return instance


class AddApplicationForm(forms.ModelForm):
    def __init__(self, election, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.election = election

    class Meta:
        model = Application
        fields = ('first_name', 'last_name', 'email', 'text', 'avatar')

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.election = self.election

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
