# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models import Q
from django_jinja import library

from ..cache import get_cache, set_cache
from ..models import HitCount
from common_utils.content_types import get_lookups


@library.global_function
def add_hitcount(*models):
	hitcounts_lookups, content_types = get_lookups(models)

	cache = get_cache()

	# odstránenie prázdnych
	hitcounts_lookups = {content_type: [i for i in id_list if (i, content_type.pk) not in cache] for content_type, id_list in hitcounts_lookups.iteritems()}
	hitcounts_lookups = {content_type: id_list for content_type, id_list in hitcounts_lookups.iteritems() if id_list}

	if not hitcounts_lookups:
		return ''

	hitcount_q = None

	for content_type, ids in hitcounts_lookups.iteritems():
		q = Q(content_type=content_type, object_id__in=ids)
		hitcount_q = q if hitcount_q is None else hitcount_q | q

	hitcounts = HitCount.objects.all().\
		filter(hitcount_q).\
		values_list('object_id', 'content_type_id', 'hits')
	hitcounts_dict = {h[:2]: h[2] for h in hitcounts}

	for model, content_type in zip(models, content_types):
		for obj in model:
			key = (obj.pk, content_type.pk)
			count = cache.get(key, hitcounts_dict.get(key))
			obj.display_count = count
			cache[key] = count

	set_cache(cache)

	return ''
