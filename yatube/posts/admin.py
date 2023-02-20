from .models import Group, Post

from django.contrib import admin


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'slug', 'pk')
    search_fields = (
        'title',
        'description',
    )
    list_filter = ('slug',)


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
