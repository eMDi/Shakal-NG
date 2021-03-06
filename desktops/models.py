# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import permalink, Count

from autoimagefield.fields import AutoImageField
from comments.models import RootHeader, Comment
from common_utils.models import TimestampModelMixin
from hitcount.models import HitCountField
from rich_editor.fields import RichTextOriginalField, RichTextFilteredField


DESKTOP_DESCRIPTION_MAX_LENGTH = 10000


class DesktopManager(models.Manager):
	def annotated_favorite(self):
		return (self.get_queryset()
			.annotate(favorited_count=Count('favorited')))


class Desktop(TimestampModelMixin, models.Model):
	objects = DesktopManager()

	author = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		verbose_name='autor',
		related_name='my_desktops'
	)
	title = models.CharField(
		'názov',
		max_length=255
	)
	image = AutoImageField(
		'desktop',
		upload_to='desktops',
		resize_source=dict(size=(4096, 4096))
	)

	original_text = RichTextOriginalField(
		filtered_field='filtered_text',
		property_name='text',
		verbose_name='popis',
		max_length=DESKTOP_DESCRIPTION_MAX_LENGTH
	)
	filtered_text = RichTextFilteredField()

	favorited = models.ManyToManyField(
		settings.AUTH_USER_MODEL,
		through='FavoriteDesktop'
	)

	comments_header = GenericRelation(RootHeader)
	comments = GenericRelation(Comment)
	hit = HitCountField()

	@permalink
	def get_absolute_url(self):
		return ('desktops:detail', (self.pk,), {})

	@permalink
	def get_update_url(self):
		return ('desktops:update', (self.pk,), {})

	def __unicode__(self):
		return self.title

	class Meta:
		verbose_name = 'desktop'
		verbose_name_plural = 'desktopy'


class FavoriteDesktop(TimestampModelMixin, models.Model):
	desktop = models.ForeignKey(Desktop, verbose_name='desktop')
	user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='používateľ')

	def __unicode__(self):
		return str(self.pk)

	class Meta:
		unique_together = ('desktop', 'user',)
