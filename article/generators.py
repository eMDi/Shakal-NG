# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django_autoslugfield.utils import unique_slugify
from django_sample_generator import GeneratorRegister, ModelGenerator, samples

from .models import Category, Article
from accounts.models import User
from common_utils.samples import LongHtmlGenerator
from hitcount.models import HitCount


class CategoryGenerator(ModelGenerator):
	name = samples.NameSample(unique=True)
	description = samples.ParagraphSample()

	def get_object(self):
		obj = super(CategoryGenerator, self).get_object()
		unique_slugify(obj, 'slug')
		return obj


class ArticleGenerator(ModelGenerator):
	title = samples.SentenceSample(unique=True)
	category_id = samples.RelationSample(queryset=Category.objects.all().order_by("pk"), random_data=True, only_pk=True, fetch_all=True)
	original_annotation = samples.ParagraphSample(max_length=500)
	original_perex = samples.ParagraphSample(max_length=500)
	original_content = LongHtmlGenerator()
	author_id = samples.RelationSample(queryset=User.objects.all().order_by("pk"), random_data=True, only_pk=True, fetch_all=True)
	authors_name = samples.NameSample()
	pub_time = samples.DateTimeSample()
	updated = samples.DateTimeSample()
	top = samples.BooleanSample()

	def get_object(self):
		obj = super(ArticleGenerator, self).get_object()
		obj.title = obj.title[:50]
		obj.filtered_annotation = obj.original_annotation[3:]
		obj.filtered_perex = obj.original_perex[3:]
		obj.filtered_content = obj.original_content[3:]
		obj.published = True
		obj.created = obj.updated
		unique_slugify(obj, 'slug')
		return obj


class HitCountGenerator(ModelGenerator):
	hits = samples.NumberSample()
	object_id = samples.RelationSample(queryset=Article.objects.all().order_by("pk"), random_data=False, only_pk=True, fetch_all=True)

	def __init__(self, *args, **kwargs):
		super(HitCountGenerator, self).__init__(*args, **kwargs)
		self.content_type = ContentType.objects.get_for_model(Article)

	def get_object(self):
		obj = super(HitCountGenerator, self).get_object()
		obj.content_type = self.content_type
		return obj


register = GeneratorRegister()
register.register(CategoryGenerator(Category, settings.INITIAL_DATA_COUNT['article_category']))
register.register(ArticleGenerator(Article, settings.INITIAL_DATA_COUNT['article_article']))
register.register(HitCountGenerator(HitCount, settings.INITIAL_DATA_COUNT['article_article']))
