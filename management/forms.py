from django import forms


class StartElectionForm(forms.Form):
    run_time = forms.IntegerField(label="run time")
