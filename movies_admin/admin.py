from django.contrib import admin
from .models import Genre, Filmwork, GenreFilmwork, Person, PersonFilmwork


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    pass  

class GenreFilmworkInline(admin.TabularInline):
    model = GenreFilmwork

class PersonFilmworkInline(admin.TabularInline):
    model = PersonFilmwork


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    inlines = (GenreFilmworkInline,PersonFilmworkInline,)
    # Отображение полей в списке
    list_display = ('title', 'type', 'creation_date', 'rating', 'created_at', 'updated_at') 

    # Фильтрация в списке
    list_filter = ('type',)

    # Поиск по полям
    search_fields = ('title', 'description', 'id') 
    
    
@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    pass  
