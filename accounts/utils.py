# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import hashlib
import os

from PIL import Image, ImageFilter
from django.apps import apps
from django.conf import settings
from django.core.cache import caches
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from common_utils import get_meta


MODELS = [
	'article.article',
	'blog.post',
	'forum.topic',
	'news.news',
	'wiki.page',
]


AVATAR_IMAGES = {
	'male': (
		('background', 5),
		('face', 4),
		('clothes', 66),
		('mouth', 26),
		('hair', 37),
		('eye', 33),
	),
	'female': (
		('background', 5),
		('face', 4),
		('clothes', 59),
		('mouth', 17),
		('head', 34),
		('eye', 53),
	),
}


default_cache = caches['default']


def last_objects():
	objects_cache = default_cache.get('last_objects')
	if objects_cache is None:
		objects_cache = {}
		for model in MODELS:
			last = (apps.get_model(model).objects
				.order_by('-created')
				.values_list('pk', 'created')[:99])
			objects_cache[model] = list(reversed(last))
		default_cache.set('last_objects', objects_cache, 60)
	return objects_cache


def clear_last_objects_cache(sender, **kwargs):
	opts = get_meta(sender)
	if '.'.join((opts.app_label, opts.model_name)) not in MODELS:
		return
	default_cache.delete('last_objects')


def count_new(last_visited, visited_items):
	counts = {}
	for model, items in last_objects().iteritems():
		count = None
		count = 0
		if model in last_visited:
			visited_date = parse_datetime(last_visited[model])
		else:
			visited_date = None
		visited_ids = set(visited_items.get(model, []))
		for pk, date in items:
			if (visited_date is None or date > visited_date) and not pk in visited_ids:
				count += 1
		counts[model] = count
	return counts


def update_last_visited(user, content_type):
	now = timezone.now()
	user_settings = user.user_settings
	user_settings.setdefault('last_visited', {})
	last_visited = user_settings['last_visited']
	if content_type:
		last_visited[content_type] = now
	for model_name in MODELS:
		last_visited.setdefault(model_name, now)
	user.user_settings = user_settings
	user.save()


def update_visited_items(user, content_type, object_id):
	user_settings = user.user_settings
	user_settings.setdefault('visited_items', {})
	visited_items = user_settings['visited_items']
	content_visited_items = set(visited_items.get(content_type, []))
	content_visited_items.add(object_id)
	content_visited_items = content_visited_items.intersection(set(i[0] for i in last_objects()[content_type]))
	user_settings['visited_items'][content_type] = list(content_visited_items)
	user.user_settings = user_settings
	user.save()


def get_count_new(user):
	user_settings = user.user_settings
	last_visited = user_settings.get('last_visited', {})
	visited_items = user_settings.get('visited_items', {})
	return count_new(last_visited, visited_items)


def generated_avatar(data):
	hash_str = hashlib.md5(data).hexdigest()

	avatar_dirname = os.path.join('CACHE', 'avatars', hash_str[-2:])
	avatar_filename = hash_str[:8] + '.png'
	if os.path.exists(os.path.join(settings.STATICFILES_DIRS[0], avatar_dirname, avatar_filename)):
		return os.path.join(avatar_dirname, avatar_filename)

	data_hash = int(hash_str, 16)
	sex = 'male' if bool(data_hash % 4) else 'female'
	data_hash = data_hash / 4
	avatar_recipe = AVATAR_IMAGES[sex]

	img = None
	for name, count in avatar_recipe:
		imgnum = (data_hash % count) + 1
		filename = os.path.join(os.path.dirname(__file__), '8biticon', '8bit-client', 'img', sex, name + str(imgnum) + '.png')
		data_hash = data_hash / count
		if img is None:
			img = Image.open(filename).convert('RGB')
			img = img.filter(ImageFilter.GaussianBlur(25))
			img = img.resize((48, 48), Image.NEAREST)
		else:
			past = Image.open(filename)
			past = past.resize((40, 40), Image.NEAREST)
			img.paste(past, (4, 7, 44, 47), past)


	try:
		os.makedirs(os.path.join(settings.STATICFILES_DIRS[0], avatar_dirname))
	except OSError:
		pass
	img.save(os.path.join(settings.STATICFILES_DIRS[0], avatar_dirname, avatar_filename))
	if hasattr(settings, 'STATIC_ROOT'):
		try:
			os.makedirs(os.path.join(settings.STATIC_ROOT, avatar_dirname))
		except OSError:
			pass
		img.save(os.path.join(settings.STATIC_ROOT, avatar_dirname, avatar_filename))
	return os.path.join(avatar_dirname, avatar_filename)
