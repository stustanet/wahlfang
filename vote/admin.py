from django.contrib import admin

from .models import Election
from .models import Application
from .models import User

admin.site.register(Election)
admin.site.register(Application)
admin.site.register(User)
