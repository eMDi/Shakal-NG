# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

import inspect

from .middlewares.ThreadLocal import get_current_request

default_app_config = 'common_utils.apps.AppConfig'


def iterify(items):
	try:
		iter(items)
		return items
	except TypeError:
		return [items]


def get_host_name():
	return 'linuxos.sk'


def build_absolute_uri(path):
	request = get_current_request()
	if request:
		return request.build_absolute_uri(path)
	else:
		return 'https://' + get_host_name() + path


def clean_dir(path, root_path):
	path = os.path.abspath(path)
	root_path = os.path.abspath(root_path)

	current_dir = path
	while len(os.path.split(current_dir)) and current_dir.startswith(root_path) and current_dir != root_path:
		try:
			os.rmdir(current_dir)
		except OSError:
			return
		current_dir = os.path.join(*os.path.split(current_dir)[:-1])


def get_meta(instance):
	return getattr(instance, "_meta")


def get_default_manager(obj):
	if inspect.isclass(obj):
		return getattr(obj, "_default_manager")
	else:
		return getattr(obj.__class__, "_default_manager")


def reload_model(obj):
	return get_default_manager(obj.__class__).get(pk=obj.pk)


def get_client_ip(request):
	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
	if x_forwarded_for:
		ip = x_forwarded_for.split(',')[0]
	else:
		ip = request.META.get('REMOTE_ADDR')
	return ip
