from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required(login_url='/management/login')
def index(request):
    context = {}

    return render(request, template_name='management/index.html', context=context)
