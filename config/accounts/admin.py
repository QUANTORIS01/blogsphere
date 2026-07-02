from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ['username', 'phone', 'role', 'first_name', 'last_name']
    list_filter = ['role']
    search_fields = ['username', 'phone', 'email']
    list_editable = ['role']
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Information',
         {'fields': ('role', 'phone', 'date_of_birth', 'bio', 'job','avatar')}),)
