from django.shortcuts import redirect, reverse

def index_view(request):
    return redirect(reverse('admin:main_issue_changelist'), permanent=True)
