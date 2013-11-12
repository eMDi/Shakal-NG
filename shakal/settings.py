# -*- coding: utf-8 -*-

import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
from django.utils.translation import ugettext_lazy as _

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
	('Miroslav Bendik', 'mireq@linuxos.sk'),
)
DEFAULT_FROM_EMAIL = 'mireq@linuxos.sk'

MANAGERS = ADMINS

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.sqlite3',
		'NAME': 'shakal.db',
		'USER': '',
		'PASSWORD': '',
		'HOST': '',
		'PORT': '',
	}
}

TIME_ZONE = 'Europe/Bratislava'
LANGUAGE_CODE = 'sk'
LANGUAGES = (('sk', 'Slovak'),)
TEMPLATES = (('desktop', ('default', 'bootstrap'),),)

SITE_ID = 1

USE_I18N = True
USE_L10N = True
USE_TZ = True
LOCALE_PATHS = (os.path.join(BASE_DIR, 'locale'), )

MEDIA_ROOT = os.path.abspath(os.path.join(BASE_DIR, 'media'))
MEDIA_URL = '/media/'

MEDIA_CACHE_DIR = os.path.join(MEDIA_ROOT, 'cache')
MEDIA_CACHE_URL = MEDIA_URL + 'cache/'
TEMPLATE_CACHE_DIR = os.path.join(BASE_DIR, 'templates', 'cache')

STATICSITEMAPS_BASE_DIR_SITEMAP = 'shakal.sitemaps.sitemaps'

STATIC_BASE_DIR = ''
STATIC_URL = '/static/'

LOGIN_URL = '/profil/prihlasit/'
LOGIN_REDIRECT_URL = '/profil/ja/'

STATICFILES_DIRS = (
	os.path.join(BASE_DIR, 'static'),
)

STATICFILES_FINDERS = (
	'django.contrib.staticfiles.finders.FileSystemFinder',
	'django.contrib.staticfiles.finders.AppDirectoriesFinder',
	#'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

SECRET_KEY = 'c)vwu21d)0!pi67*_@xyv3qp!*74w50!7795t*!d9rfdu(%8g$'

TEMPLATE_LOADERS = (
	'template_dynamicloader.loader_filesystem.Loader',
	'django.template.loaders.filesystem.Loader',
	'django.template.loaders.app_directories.Loader',
	#'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
	'django.core.context_processors.debug',
	'django.core.context_processors.i18n',
	'django.core.context_processors.media',
	'django.core.context_processors.static',
	'django.core.context_processors.request',
	'django.contrib.auth.context_processors.auth',
	'django.contrib.messages.context_processors.messages',
	'feeds.context_processors.feeds',
	'template_dynamicloader.context_processors.style',
)

MIDDLEWARE_CLASSES = (
	'django.middleware.common.CommonMiddleware',
	'django.middleware.locale.LocaleMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'auth_remember.middleware.AuthRememberMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django_tools.middlewares.ThreadLocal.ThreadLocalMiddleware',
	'template_dynamicloader.middleware.TemplateSwitcherMiddleware',
	'feeds.middleware.FeedsMiddleware',
	'maintenance.middleware.MaintenanceMiddleware',
)

AUTHENTICATION_BACKENDS = (
	'django.contrib.auth.backends.ModelBackend',
	'auth_remember.backend.AuthRememberBackend',
)

BASE_DIR_URLCONF = 'shakal.urls'

WSGI_APPLICATION = 'shakal.wsgi.application'

TEMPLATE_DIRS = (
	os.path.join(BASE_DIR, 'templates'),
)

INSTALLED_APPS = (
	'admin_dashboard',
	#'admin_tools',
	#'admin_tools.theming',
	#'admin_tools.menu',
	#'admin_tools.dashboard',
	'suit',
	'suit_redactor',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.sites',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'django.contrib.admin',
	'django.contrib.syndication',
	'django.contrib.sitemaps',
	'django_tools',
	'haystack',
	'queued_search',
	'registration',
	'accounts',
	'article',
	'attachment',
	'auth_remember',
	'blog',
	'bootstrap_toolkit',
	'breadcrumbs',
	'hitcount',
	'imgcompress',
	'maintenance',
	'mptt',
	'notifications',
	'paginator',
	'polls',
	'rich_editor',
	'reversion',
	'threaded_comments',
	'template_preprocessor',
	'forum',
	'feeds',
	'linuxos',
	'news',
	'search',
	'template_dynamicloader',
	'wiki',
	'fts',
	'static_sitemaps',
)

QUEUE_BACKEND = 'dummy'

COMMENTS_APP = 'threaded_comments'

LOGGING = {
	'version': 1,
	'disable_existing_loggers': False,
	'filters': {
		'require_debug_false': {
			'()': 'django.utils.log.RequireDebugFalse'
		}
	},
	'handlers': {
		'mail_admins': {
			'level': 'ERROR',
			'filters': ['require_debug_false'],
			'class': 'django.utils.log.AdminEmailHandler'
		}
	},
	'loggers': {
		'django.request': {
			'handlers': ['mail_admins'],
			'level': 'ERROR',
			'propagate': True,
		},
	}
}

AUTH_USER_MODEL = 'accounts.User'

ACCOUNT_ACTIVATION_DAYS = 7

ABSOLUTE_URL_OVERRIDES = {
	'auth.user': lambda o: '/profil/{0}/'.format(o.pk)
}

ATTACHMENT_MAX_SIZE = 1024 * 1024 * 50
ATTACHMENT_SIZE_FOR_CONTENT = {
	'django_comments': 1024 * 1024 * 2,
	'forum_topic': 1024 * 1024 * 2,
	'blog_post': 1024 * 1024 * 8,
}

HAYSTACK_CONNECTIONS = {
	'default': {
		'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
	},
}
HAYSTACK_CUSTOM_HIGHLIGHTER = 'search.utils.XapianHighlighter'
HAYSTACK_SIGNAL_PROCESSOR = 'queued_search.signals.QueuedSignalProcessor'

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

GRAVATAR_DEFAULT_SIZE = 200
GRAVATAR_URL_PREFIX = "http://sk.gravatar.com/"

FEED_SIZE = 20

ADMIN_DASHBOARD_APP_GROUPS = (
	(
		_('Content management'), {
			'models': (
				'article.*',
				'news.*',
				'wiki.models.*',
			),
			'exclude': (
				'article.models.Category',
			)
		}
	),
	(
		_('Administration'), {
			'models': (
				'accounts.*',
				'django.contrib.auth.*',
				'django.contrib.sites.*',
				'polls.*',
			),
		}
	),
	(
		_('Forum'), {
			'models': (
				'forum.*',
				'threaded_comments.*',
			),
		}
	),
	(
		_('Applications'), {
			'models': ('*',),
			'module': 'AppList',
			'exclude': ('auth_remember.*', 'registration.*', ),
			'collapsible': True,
		}
	),
)
ADMIN_DASHBOARD_APP_ICONS = {
	'accounts/user': 'user.png',
	'auth/group': 'group.png',
	'sites/site': 'site.png',
	'article/article': 'article.png',
	'news/news': 'news.png',
	'wiki/page': 'wiki.png',
	'threaded_comments/comment': 'comments.png',
	'forum/topic': 'topic.png',
	'polls/poll': 'poll.png',
	'forum/section': 'section.png',
}
ADMIN_TOOLS_INDEX_DASHBOARD = 'admin_dashboard.dashboard.AdminIndexDashboard'
ADMIN_TOOLS_MENU = 'admin_dashboard.menu.AdminMenu'
ADMIN_TOOLS_THEMING_CSS = 'admin/css/shakal.css'
SUIT_CONFIG = {
	'ADMIN_NAME': 'Shakal CMS',
	'HEADER_DATE_FORMAT': 'l, d F Y',
	'HEADER_TIME_FORMAT': 'H:i',
	'SHOW_REQUIRED_ASTERISK': True,
	'CONFIRM_UNSAVED_CHANGES': True,
	'SEARCH_URL': '/administracia/accounts/user/',
	'MENU_OPEN_FIRST_CHILD': True,
	'MENU_ICONS': {
		'sites': 'icon-leaf',
		'auth': 'icon-lock',
	},
	'MENU_EXCLUDE': ('auth_remember',),
	'LIST_PER_PAGE': 50,
	'MENU': (
		{
			'label': u'Ankety',
			'icon': 'icon-tasks',
			'permissions': 'polls.change_poll',
			'models': (
				'polls.poll',
			)
		},
		{
			'label': u'Blogy',
			'icon': 'icon-pencil',
			'permissions': 'blog.change_post',
			'models': (
				'blog.post',
				'blog.blog',
			)
		},
		{
			'label': u'Články',
			'icon': 'icon-font',
			'permissions': 'article.change_article',
			'models': (
				'article.article',
				'article.category',
			)
		},
		{
			'label': u'Fórum',
			'icon': 'icon-list',
			'permissions': 'forum.change_topic',
			'models': (
				'forum.topic',
				'forum.section',
			)
		},
		{
			'label': u'Používatelia',
			'icon': 'icon-lock',
			'permissions': 'accounts.change_user',
			'models': (
				'accounts.user',
				'auth.group',
			)
		},
		{
			'label': u'Správy',
			'icon': 'icon-globe',
			'permissions': 'news.change_news',
			'models': (
				'news.news',
			)
		},
		{
			'label': u'Wiki',
			'icon': 'icon-folder-open',
			'permissions': 'wiki.change_page',
			'models': (
				'wiki.page',
			)
		},
	),
}

CONN_MAX_AGE = 300

import sys
if len(sys.argv) > 1 and sys.argv[1] == 'test':
	DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:', }}
	TEMPLATES = (('desktop', ('test',),),)

	LANGUAGE_CODE = 'en'
	LANGUAGES = (('en', 'English'),)
	CAPTCHA_DISABLE = True
	LOGIN_URL = '/accounts/login/'
	LOGIN_REDIRECT_URL = '/accounts/me/'
