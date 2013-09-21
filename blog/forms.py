# -*- coding: utf-8 -*-
from django import forms

from .models import Blog, Post
from rich_editor.forms import RichOriginalField


class BlogForm(forms.ModelForm):
	original_description = RichOriginalField(Blog._meta.get_field('original_description').parsers, label = u'Popis', max_length = 1000, js = True) #pylint: disable=W0212
	original_sidebar = RichOriginalField(Blog._meta.get_field('original_sidebar').parsers, label = u'Bočný panel', max_length = 1000, js = True) #pylint: disable=W0212
	class Meta:
		model = Blog
		exclude = ('author', 'slug')


class PostForm(forms.ModelForm):
	original_perex = RichOriginalField(Post._meta.get_field('original_perex').parsers, label = u'Perex', max_length = 1000, js = True) #pylint: disable=W0212
	original_content = RichOriginalField(Post._meta.get_field('original_content').parsers, label = u'Obsah', max_length = 100000, js = True) #pylint: disable=W0212

	def __init__(self, *args, **kwargs):
		super(PostForm, self).__init__(*args, **kwargs)
		if self.instance and self.instance.published(): #pylint: disable=E1101
			del self.fields['pub_time']

	class Meta:
		model = Post
		exclude = ('blog', 'slug', 'linux')
