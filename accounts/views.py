# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import timedelta

from braces.views import LoginRequiredMixin
from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db.models import Count, Max
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.views.generic import RedirectView, DetailView, UpdateView

from .forms import ProfileEditForm
from common_utils import get_meta
from common_utils.generic import ListView
from common_utils.time_series import time_series, set_gaps_zero


class UserZone(LoginRequiredMixin, RedirectView):
	permanent = False
	pattern_url = 'accounts:my_profile'


class Profile(DetailView):
	pattern_url = 'accounts:my_profile'
	model = get_user_model()
	template_name = 'account/profile.html'
	context_object_name = 'user_profile'

	def get_context_data(self, **kwargs):
		ctx = super(Profile, self).get_context_data(**kwargs)
		user = self.get_object()
		user_table = (
			{'name': 'Používateľské meno', 'value': user.username, 'class': 'nickname'},
			{'name': 'Celé meno', 'value': (user.first_name + ' ' + user.last_name).strip(), 'class': 'fn'},
			{'name': 'Podpis', 'value': mark_safe(user.signature), 'class': ''},
			{'name': 'Linuxová distribúcia', 'value': user.distribution, 'class': 'note'},
			{'name': 'Rok narodenia', 'value': user.year},
		)
		if user.display_mail:
			email = user.email.replace('@', ' ZAVINÁČ ').replace('.', ' BODKA ')
			user_table = user_table + ({'name': 'E-mail', 'value': email}, )
		ctx['user_table'] = user_table
		ctx['is_my_profile'] = self.request.user.pk == user.pk
		return ctx

class MyProfileMixin(object):
	def get_object(self):
		return self.request.user


class MyProfile(LoginRequiredMixin, MyProfileMixin, Profile):
	pass


class MyProfileEdit(LoginRequiredMixin, MyProfileMixin, UpdateView):
	template_name = 'account/profile_change.html'
	form_class = ProfileEditForm

	def get_success_url(self):
		return reverse('accounts:my_profile')


class UserStatsMixin(object):
	paginate_by = 50
	object = None

	def get_articles(self):
		return apps.get_model('article.Article').objects.filter(author=self.object)

	def get_blog_posts(self):
		return apps.get_model('blog.Post').objects.filter(blog__author=self.object)

	def get_forum_topics(self):
		return apps.get_model('forum.Topic').objects.filter(author=self.object)

	def get_news(self):
		return apps.get_model('news.News').objects.filter(author=self.object)

	def get_commented(self):
		return (apps.get_model('threaded_comments.Comment')
			.objects
			.filter(user=self.object, parent__isnull=False)
			.values_list('content_type_id', 'object_id')
			.annotate(max_pk=Max('pk'))
			.order_by('-max_pk'))

	def get_object(self):
		return get_object_or_404(get_user_model(), pk=self.kwargs['pk'])

	def get_last_updated_wiki_pages(self):
		return (apps.get_model('wiki.Page')
			.objects
			.filter(last_author=self.object, parent__isnull=False))

	def resolve_content_objects(self, content_object_list):
		object_list_by_content = {}
		for obj in content_object_list:
			object_list_by_content.setdefault(obj[0], [])
			object_list_by_content[obj[0]].append(obj[1])
		content_types = {obj.id: obj for obj in ContentType.objects.filter(pk__in=object_list_by_content.keys())}

		for content_type, content_object_ids in object_list_by_content.iteritems():
			object_list_by_content[content_type] = (content_types[content_type]
				.model_class()
				.objects
				.filter(pk__in=content_object_ids))

		objects_idx = {}
		for content_type, content_objects in object_list_by_content.iteritems():
			for content_object in content_objects:
				objects_idx[(content_type, content_object.pk)] = content_object

		object_list = [objects_idx[(o[0], int(o[1]))] for o in content_object_list if (o[0], int(o[1])) in objects_idx]
		return object_list, object_list_by_content

	def get_context_data(self, **kwargs):
		ctx = super(UserStatsMixin, self).get_context_data(**kwargs)
		ctx['user_profile'] = self.object
		return ctx

	def get(self, request, **kwargs):
		self.object = self.get_object()
		return super(UserStatsMixin, self).get(request, **kwargs)


class UserPosts(UserStatsMixin, DetailView):
	template_name = 'account/user_posts.html'

	def get_context_data(self, **kwargs):
		def url(view_name):
			return reverse('accounts:user_posts_' + view_name, args=(self.object.pk,), kwargs={})

		ctx = super(UserPosts, self).get_context_data(**kwargs)
		ctx['stats'] = (
			{'label': 'Články', 'url': url('article'), 'count': self.get_articles().count()},
			{'label': 'Blogy', 'url': url('blogpost'), 'count': self.get_blog_posts().count()},
			{'label': 'Správy', 'url': url('news'), 'count': self.get_news().count()},
			{'label': 'Témy vo fóre', 'url': url('forumtopic'), 'count': self.get_forum_topics().count()},
			{'label': 'Komentované diskusie', 'url': url('commented'), 'count': self.get_commented().count()},
			{'label': 'Wiki stránky', 'url': url('wikipage'), 'count': self.get_last_updated_wiki_pages().count()},
		)
		return ctx


class UserStatsListBase(UserStatsMixin, ListView):
	stats_by_date_field = None
	template_name = 'account/user_posts_detail.html'

	def get_time_series(self, interval, time_stats_ago=365):
		now = timezone.localtime(timezone.now())
		return set_gaps_zero(time_series(
			qs=self.get_stats_queryset(),
			date_field=self.stats_by_date_field,
			interval=interval,
			aggregate=Count('id'),
			date_from=now.date() + timedelta(-time_stats_ago),
			date_to=now.date()
		))

	def get_stats_queryset(self):
		return self.get_queryset()

	def get_stats_by_date(self):
		monthly_stats = self.get_time_series('month', 365*10)
		daily_stats = self.get_time_series('day', 365)
		return {
			'monthly_stats': monthly_stats,
			'daily_stats': daily_stats,
		}

	def get_objects_name(self):
		return get_meta(self.get_queryset().model).verbose_name_plural

	def get_context_data(self, **kwargs):
		ctx = super(UserStatsListBase, self).get_context_data(**kwargs)
		if self.stats_by_date_field is not None:
			ctx.update(self.get_stats_by_date())
		ctx['objects_name'] = self.get_objects_name()
		return ctx


class UserPostsArticle(UserStatsListBase):
	stats_by_date_field = 'pub_time'

	def get_queryset(self):
		return self.get_articles().order_by('-pk')


class UserPostsBlogpost(UserStatsListBase):
	stats_by_date_field = 'pub_time'

	def get_queryset(self):
		return self.get_blog_posts().order_by('-pk')


class UserPostsNews(UserStatsListBase):
	stats_by_date_field = 'created'

	def get_queryset(self):
		return self.get_news().order_by('-pk')


class UserPostsForumTopic(UserStatsListBase):
	stats_by_date_field = 'created'

	def get_queryset(self):
		return self.get_forum_topics().order_by('-pk')


class UserPostsCommented(UserStatsListBase):
	template_name = 'account/user_posts_commented.html'
	stats_by_date_field = 'submit_date'

	def get_stats_queryset(self):
		return apps.get_model('threaded_comments.Comment').objects.filter(parent__isnull=False, user=self.object)

	def get_queryset(self):
		return self.get_commented()

	def get_context_data(self, **kwargs):
		ctx = super(UserPostsCommented, self).get_context_data(**kwargs)
		ctx['object_list'], ctx['object_list_by_content'] = self.resolve_content_objects(ctx['object_list'])
		return ctx


class UserPostsWikiPage(UserStatsListBase):
	stats_by_date_field = 'updated'

	def get_queryset(self):
		return self.get_last_updated_wiki_pages().order_by('-pk')
