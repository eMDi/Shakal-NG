# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Section, Topic
from attachment.admin import AttachmentInline, AttachmentAdminMixin


class SectionAdmin(admin.ModelAdmin):
	list_display = ('name', 'slug',)
	search_fields = ('name', 'slug',)
	prepopulated_fields = {'slug': ('name',)}


class TopicAdmin(AttachmentAdminMixin, admin.ModelAdmin):
	list_display = ('title', 'get_authors_name', 'is_removed', 'is_resolved',)
	list_filter = ('section', 'is_removed', 'is_resolved',)
	search_fields = ('title', 'get_authors_name',)
	ordering = ('-id',)
	raw_id_fields = ('author',)
	inlines = [AttachmentInline]


admin.site.register(Section, SectionAdmin)
admin.site.register(Topic, TopicAdmin)
