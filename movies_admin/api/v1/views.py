from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.list import BaseListView
from django.core import serializers
from django.forms.models import model_to_dict

from movies_admin.models import Filmwork


class MoviesListApi(BaseListView):
    model = Filmwork
    paginate_by = 50
    http_method_names = ['get']  # Список методов, которые реализует обработчик
    
    def get_queryset(self):
        return self.model.objects.values()# Сформированный QuerySet

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = self.get_queryset()
        paginator, page, queryset, is_paginated = self.paginate_queryset(
            queryset, 
            self.paginate_by
        )
        return {'count': paginator.count, 
            'total_pages':paginator.count // self.paginate_by + (paginator.count % self.paginate_by > 0),
            'prev':1,
            'next':2,
            'results':list(queryset)
        } 

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)
