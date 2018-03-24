from django import http
from django.contrib import admin
from django.contrib import auth
from django.urls import path

from .models import Issue

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
        return super().changelist_view(request, extra_context)

admin_site = AdminSite()
admin_site.register(Issue, IssueAdmin)
admin_site.register(auth.admin.User, UserAdmin)
