import uuid

from django.db import models
from django.db.models import Aggregate
from django.core.validators import MinValueValidator, MaxValueValidator
from psqlextra.indexes import UniqueIndex
from django.utils.translation import gettext_lazy as _


class Concat(Aggregate):
    function = 'string_agg'
    template = "%(function)s(%(field)s::text, ',')"
    allow_distinct = True

    def __init__(self, expression, all_values=False, **extra):
        if 'filter_role' in extra.keys():
            self.template = f"%(function)s(case when \"content\".\"person_film_work\".\"role\" = '{extra['filter_role']}' then %(field)s::text else null end, ',')"
        super().__init__(
            expression,
            all_values='ALL ' if all_values else '',
            **extra
        )


class TimeStampedMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Этот параметр указывает Django, что этот класс не является представлением таблицы
        abstract = True
        

class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    
    def __str__(self):
        return self.name 

    class Meta:
        # Ваши таблицы находятся в нестандартной схеме. Это нужно указать в классе модели
        db_table = "content\".\"genre"
        # Следующие два поля отвечают за название модели в интерфейсе
        verbose_name = _('Genre')
        verbose_name_plural = _('Genres')
        
        
class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.TextField(_('full_name'), blank=False)
    
    def __str__(self):
        return self.full_name 
    
    class Meta:
        # Ваши таблицы находятся в нестандартной схеме. Это нужно указать в классе модели
        db_table = "content\".\"person"
        # Следующие два поля отвечают за название модели в интерфейсе
        verbose_name = _('Actors')
        verbose_name_plural = _('Actors')
        

class Filmwork(UUIDMixin, TimeStampedMixin):
    title = models.TextField(_('title'), blank=False)
    description = models.TextField(_('description'), blank=True)
    creation_date = models.DateField(_('creation_date'), blank=True)
    file_path = models.TextField(_('file_path'), blank=True, null=True)
    rating = models.FloatField(_('rating'), blank=True,
                               validators=[MinValueValidator(0),
                                           MaxValueValidator(100)])
    type = models.CharField(_('type'), choices=models.TextChoices('type', ['movie', 'tv_show']).choices)
    
    def __str__(self):
        return self.title 

    class Meta:
        # Ваши таблицы находятся в нестандартной схеме. Это нужно указать в классе модели
        db_table = "content\".\"film_work"
        # Следующие два поля отвечают за название модели в интерфейсе
        verbose_name = _('film_work')
        verbose_name_plural = _('film_work')
    
    genres = models.ManyToManyField(Genre, through='GenreFilmwork')
    persons = models.ManyToManyField(Person, through='PersonFilmwork')
        
   
class GenreFilmwork(UUIDMixin):
    film_work = models.ForeignKey(Filmwork, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"genre_film_work"
    
    
class PersonFilmwork(UUIDMixin):
    film_work = models.ForeignKey(Filmwork, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    # role = models.TextField(_('role'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class RoleInFilm(models.TextChoices):
        ACTOR = 'actor', _('actor')
        DIRECTOR = 'director', _('director')
        WRITER = 'writer', _('writer')

    role = models.CharField(
        choices=RoleInFilm.choices,
        default=RoleInFilm.ACTOR,
    )
    
    class Meta:
        db_table = "content\".\"person_film_work"
        indexes = [
            UniqueIndex(fields=['film_work', 'person', 'role'], name="film_work_person_idx"),
            models.Index(fields=['created_at'], name="film_work_creation_date_idx")
        ]