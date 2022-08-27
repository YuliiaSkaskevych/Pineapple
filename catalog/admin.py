from django.contrib import admin

from .models import Quote, Comment


class CommentInlineModelAdmin(admin.TabularInline):
    model = Comment


@admin.register(Quote)
class QuoteModelAdmin(admin.ModelAdmin):
    list_display = ['heading', 'description', 'message', 'author', 'status']
    fields = ['heading', 'description', 'message', 'image', 'author', 'publish']
    raw_id_fields = ['author', ]
    date_hierarchy = "publish"
    search_fields = ["author", "heading"]
    actions = ["change_status_to_draft", "change_status_to_published"]
    inlines = [CommentInlineModelAdmin]

    def change_status_to_draft(self, request, queryset):
        queryset.update(status='draft')
    change_status_to_draft.short_description = "Status: draft"

    def change_status_to_published(self, request, queryset):
        queryset.update(status='published')
    change_status_to_published.short_description = "Status: published"


@admin.register(Comment)
class CommentModelAdmin(admin.ModelAdmin):
    list_display = ["name", "text", "post", "published"]
    fields = ['name', 'text', "post", "created"]
    search_fields = ["post", ]
    date_hierarchy = "created"
    actions = ["allow_comment", "block_comment"]

    def allow_comment(self, request, queryset):
        queryset.update(published=True)

    allow_comment.short_description = "Allow comment to publication"

    def block_comment(self, request, queryset):
        queryset.update(published=False)

    block_comment.short_description = "Block comment to publication"
