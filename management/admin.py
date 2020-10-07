from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from management.models import ElectionManager


class ElectionManagerCreateForm(UserCreationForm):
    class Meta:
        model = ElectionManager
        fields = ('username', 'email', 'password')
        field_classes = {}


class ElectionManagerChangeForm(UserChangeForm):
    class Meta:
        model = ElectionManager
        fields = ('username', 'email',)
        field_classes = {}


class ElectionManagerAdmin(UserAdmin):
    add_form = ElectionManagerCreateForm
    form = ElectionManagerChangeForm
    model = ElectionManager
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2')}
         ),
    )
    list_display = ('username', 'email',)
    list_filter = ('username', 'email',)
    ordering = ('username', 'email',)
    filter_horizontal = tuple()


admin.site.register(ElectionManager, ElectionManagerAdmin)
