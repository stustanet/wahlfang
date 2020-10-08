from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _

from .models import Application
from .models import Election
from .models import Voter


class VoterCreationForm(UserCreationForm):
    class Meta:
        model = Voter
        fields = ('voter_id',)
        field_classes = {}


class VoterChangeForm(UserChangeForm):
    class Meta:
        model = Voter
        fields = ('voter_id',)
        field_classes = {}


class VoterAdmin(UserAdmin):
    add_form = VoterCreationForm
    form = VoterChangeForm
    model = Voter
    fieldsets = (
        (None, {'fields': ('voter_id', 'password', 'session',)}),
        (_('Personal info'), {'fields': ('email',)}),
        (_('Status'), {'fields': ('voted',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('voter_id', 'password1', 'password2', 'session')}
         ),
        (_('Personal info'), {'fields': ('email',)}),
    )
    list_display = ('voter_id', 'session',)
    list_filter = ()
    search_fields = ('voter_id', 'session', 'email',)
    ordering = ('voter_id',)
    filter_horizontal = tuple()


admin.site.register(Election)
admin.site.register(Application)
admin.site.register(Voter, VoterAdmin)
