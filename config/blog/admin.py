from django.contrib import admin
from .models import *


def draft_status(model_admin, request, queryset):
    result = queryset.update(status=Post.Status.DRAFT)
    model_admin.message_user(request, f'{result}The post status changed to draft.')


draft_status.short_description = 'Change status to draft'


def publish_status(model_admin, request, queryset):
    result = queryset.update(status=Post.Status.PUBLISH)
    model_admin.message_user(request, f'{result}The post status has been changed to "Published".')


publish_status.short_description = 'Change status to Published'


def reject_status(model_admin, request, queryset):
    result = queryset.update(status=Post.Status.REJECT)
    model_admin.message_user(request, f'{result}The post status changed to "Rejected".')


reject_status.short_description = 'Change status to Rejected'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'publish', 'status']
    ordering = ['title', 'publish']
    list_filter = ['status', 'author', 'publish']
    search_fields = ['title', 'description']
    raw_id_fields = ['author']
    date_hierarchy = 'publish'
    list_editable = ['status']
    list_display_links = ['title']
    actions = [draft_status, publish_status, reject_status]

    def get_queryset(self, request):
        return Post._base_manager.all()


