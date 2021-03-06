# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from datetime import timedelta

from django.apps import apps
from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.core.validators import MinValueValidator, MaxValueValidator, MaxLengthValidator
from django.db import models
from django.utils import timezone

from . import accounts_settings
from .utils import get_count_new
from autoimagefield.fields import AutoImageField
from common_utils import get_default_manager
from rich_editor.fields import RichTextOriginalField, RichTextFilteredField
from django_geoposition_field.fields import GeopositionField


class User(AbstractUser):
	objects = UserManager()

	jabber = models.CharField(max_length=127, blank=True)
	url = models.CharField(max_length=255, blank=True)
	signature = models.CharField('podpis', max_length=255, blank=True)
	display_mail = models.BooleanField('zobrazovať e-mail', default=False)
	distribution = models.CharField('linuxová distribúcia', max_length=50, blank=True)
	original_info = RichTextOriginalField(filtered_field='filtered_info', property_name='info', parsers={'html': 'profile'}, verbose_name='informácie', validators=[MaxLengthValidator(100000)], blank=True)
	filtered_info = RichTextFilteredField(blank=True)
	year = models.SmallIntegerField('rok narodenia', validators=[MinValueValidator(1900), MaxValueValidator(2015)], blank=True, null=True)
	avatar = AutoImageField('fotografia', upload_to='accounts/avatars', resize_source=dict(size=(512, 512)), blank=True)
	settings = models.TextField('nastavenia', blank=True)
	geoposition = GeopositionField(verbose_name='poloha', blank=True)

	def clean_fields(self, exclude=None):
		if self.email:
			qs = get_default_manager(self).filter(email=self.email).exclude(pk=self.pk)
			if qs.exists():
				raise ValidationError({'email': ['Používateľ s touto e-mailovou adresou už existuje']})
		super(User, self).clean_fields(exclude)

	@models.permalink
	def get_absolute_url(self):
		return ('accounts:profile', [], {'pk': self.pk})

	def get_full_name(self):
		full_name = ('%s %s' % (self.first_name, self.last_name)).strip()
		return full_name or self.username or self.email
	get_full_name.short_description = 'celé meno'
	get_full_name.admin_order_field = 'last_name,first_name,username'

	@property
	def user_settings(self):
		try:
			return json.loads(self.settings)
		except ValueError:
			return {}

	@user_settings.setter
	def user_settings(self, val):
		self.settings = json.dumps(val, cls=DjangoJSONEncoder)

	@property
	def count_new(self):
		return {k.replace('.', '_'): v for k, v in get_count_new(self).iteritems()}

	@property
	def last_desktop(self):
		Desktop = apps.get_model('desktops', 'desktop')
		return (Desktop.objects.all()
			.filter(author=self)
			.order_by('-pk')
			.first())

	def __unicode__(self):
		return self.get_full_name() or self.username

	class Meta:
		db_table = 'auth_user'
		verbose_name = 'používateľ'
		verbose_name_plural = 'používatelia'


class UserRating(models.Model):
	RATING_WEIGHTS = {
		'comments': 1,
		'articles': 200,
		'helped': 20,
		'news': 10,
		'wiki': 50,
	}

	user = models.OneToOneField(User, related_name='rating')
	comments = models.IntegerField(default=0)
	articles = models.IntegerField(default=0)
	helped = models.IntegerField(default=0)
	news = models.IntegerField(default=0)
	wiki = models.IntegerField(default=0)
	rating = models.IntegerField(default=0)

	def get_rating_label(self):
		r = self.rating
		return (r >= 1000 and '5') or (r >= 400 and '4') or (r >= 50 and '3') or (r >= 10 and '2') or '1'

	def __unicode__(self):
		return self.get_rating_label()


class RememberTokenManager(models.Manager):
	def get_by_string(self, token):
		try:
			user_id, token_hash = token.split(':')
		except ValueError:
			return None

		max_age = timezone.now() - timedelta(seconds=accounts_settings.COOKIE_AGE)
		for token in self.all().filter(created__gte=max_age, user=user_id):
			if check_password(token_hash, token.token_hash):
				return token

	def clean_remember_tokens(self):
		max_age = timezone.now() - timedelta(seconds=accounts_settings.COOKIE_AGE)
		return self.all().filter(created__lte=max_age).delete()


class RememberToken(models.Model):
	objects = RememberTokenManager()

	token_hash = models.CharField(max_length=255, blank=False, primary_key=True)
	created = models.DateTimeField(editable=False, blank=True, auto_now_add=True)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="remember_me_tokens")

	def __unicode__(self):
		return self.token_hash
