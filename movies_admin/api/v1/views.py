from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.list import BaseListView
from django.views.generic.detail import BaseDetailView

from movies_admin.models import Filmwork, Concat


class MoviesApiMixin:
    model = Filmwork
    http_method_names = ['get']
    extract_cols = [
        'id',
        'title',
        'description',
        'creation_date',
        'rating',
        'type'
        ]
    agg_cols = {'genres': Concat('genres__name'),
                'actors': Concat('persons__full_name', filter_role='actor'),
                'directors': Concat('persons__full_name', filter_role='director'),
                'writers': Concat('persons__full_name', filter_role='writer')}


    def get_distinct_list(self, string_agg):
        if string_agg is None:
            return []
        return list(set(string_agg.split(',')))
    
    def get_queryset(self):
        return self.model.objects.select_related().values(*self.extract_cols).annotate(**self.agg_cols)# Сформированный QuerySet

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):
    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = self.get_queryset()
        paginator, page, queryset, is_paginated = self.paginate_queryset(
            queryset, 
            self.paginate_by
        )

        res = list(queryset)
        for elem in res:
            for col in self.agg_cols.keys():
                elem[col] = self.get_distinct_list(elem[col])

        return {'count': paginator.count, 
            'total_pages':paginator.count // self.paginate_by + (paginator.count % self.paginate_by > 0),
            'prev':1,
            'next':2,
            'results': res
        } 

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):

    def get_context_data(self, **kwargs):
        # queryset = self.get_queryset().filter(uuid=kwargs['pk']).values()
        # queryset = self.get_queryset()
        # return  # Словарь с данными объекта
        res = kwargs['object']
        for col in self.agg_cols.keys():
            res[col] = self.get_distinct_list(res[col])
        return res