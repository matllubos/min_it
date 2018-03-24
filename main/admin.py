from django import http
from django.contrib import admin
from django.contrib import auth
from django.db.models import Q
from django.urls import path

from . import models

class AdminSite(admin.AdminSite):
    index_title = ''
    site_header = 'Minimalistic Issue Tracker'
    site_title = 'Minimalistic Issue Tracker'
    site_url = None

class UserAdmin(auth.admin.UserAdmin):
    actions = None
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions',
         {'fields': ('is_active', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}))
    readonly_fields = ['last_login', 'date_joined']
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'is_superuser')

    def save_model(self, request, obj, form, change):
        obj.is_staff = True
        super().save_model(request, obj, form, change)

class IssueAdmin(admin.ModelAdmin):
    actions = None
    fields = [
        'title', 'filed_at', 'filer', 'assignee', 'description',
        'category', 'status', 'last_modified_at', 'closed_at']
    readonly_fields = ['filed_at', 'closed_at', 'last_modified_at']
    list_display = [
        'title', 'filed_at', 'filer', 'assignee',
        'category', 'status', 'last_modified_at', 'closed_at']
    # Keep in mind that having 'filer' and 'assignee' in the list_filter
    # may result in a really long page if project have many users.
    # If this is the case, consider using text field to filter by user.
    list_filter = [
        'status', 'category', 'filer', 'assignee']
    # Default search may be slow on large sets, consider using
    # full-text search if DB-backend supports it.
    search_fields = ['title', 'description']

    def has_delete_permission(self, request, obj=None):
        return False

    def has_module_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def get_readonly_fields(self, request, obj=None):
        """
        Overriding method to make object readonly for staff-members.
        """
        if request.user.is_staff and not request.user.is_superuser:
            return self.fields
        return self.readonly_fields

    def change_view(self, request, object_id, form_url='', extra_context=None):
        # Disabling POST-request for non-superusers.
        if request.method == 'POST' and not request.user.is_superuser:
            return http.HttpResponseForbidden('Forbidden')
        return super().change_view(request, object_id, form_url, extra_context)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = 'List of issues'
        extra_context['statistics'] = self.get_statistics()
        return super().changelist_view(request, extra_context)

    def get_statistics(self):
        """
        Calculating some stats data.
        The calculation is performed on every request, therefore this method
        is not very efficient. Consider adding auxilary model
        to store statistics in the DB for better performance.
        """
        def seconds_to_human_str(t_seconds):
            """
            Convert total seconds into human readable format
            x days, y hours, z minutes
            """
            t_seconds = int(t_seconds)
            days, remainder = divmod(t_seconds, 24*60*60)
            hours, remainder = divmod(remainder, 60*60)
            minutes, _ = divmod(remainder, 60)
            result = ''
            if days == 1:
                result += '1 day '
            elif days > 1:
                result += '%s days ' % days
            if hours == 1:
                result += '1 hour '
            elif hours > 1:
                result += '%s hours ' % hours
            if minutes == 1:
                result += '1 minute'
            elif minutes > 1:
                result += '%s minutes' % minutes
            return result

        closed_issues = models.Issue.objects.filter(
            Q(status=models.STATUSES['Closed, verified']) |
            Q(status=models.STATUSES['Closed, not verified']))
        # Calculating resolution time of all closed bugs in seconds
        resolution_time_list = [
            (issue.closed_at - issue.filed_at).total_seconds()
            for issue in closed_issues]
        if resolution_time_list:
            min_resolution_time = seconds_to_human_str(min(resolution_time_list))
            max_resolution_time = seconds_to_human_str(max(resolution_time_list))
            avg_resolution_time = seconds_to_human_str(
                sum(resolution_time_list) / len(resolution_time_list))
        else:
            min_resolution_time = '-'
            max_resolution_time = '-'
            avg_resolution_time = '-'
        return {
            'Total issues': models.Issue.objects.all().count(),
            'Number of open issues': models.Issue.objects.filter(
                status=models.STATUSES['Open']).count(),
            'Number of closed issues': closed_issues.count(),
            'Number of WIP issues': models.Issue.objects.filter(
                status=models.STATUSES['Work in progress']).count(),
            'Min resolution time': min_resolution_time,
            'Max resolution time': max_resolution_time,
            'Average resolution time': avg_resolution_time,
        }

admin_site = AdminSite()
admin_site.register(models.Issue, IssueAdmin)
admin_site.register(auth.admin.User, UserAdmin)
