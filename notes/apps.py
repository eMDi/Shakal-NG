# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig as CoreAppConfig


class AppConfig(CoreAppConfig):
	name = 'notes'
	verbose_name = "Poznámky"

