# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.template.loader import render_to_string
from django.utils import six


class GeopositionWidget(forms.MultiWidget):
	def __init__(self, attrs=None):
		widgets = (
			forms.TextInput(),
			forms.TextInput(),
		)
		super(GeopositionWidget, self).__init__(widgets, attrs)

	def decompress(self, value):
		if isinstance(value, six.text_type):
			return value.rsplit(',')
		if value:
			return [value.latitude, value.longitude]
		return [None,None]

	def format_output(self, rendered_widgets):
		return render_to_string('geoposition/widgets/geoposition.html', {
			'latitude_widget': rendered_widgets[0],
			'longitude_widget': rendered_widgets[1],
		})

	class Media:
		js = ('geoposition/geoposition.js',)
		css = {'all': ('geoposition/geoposition.css',)}