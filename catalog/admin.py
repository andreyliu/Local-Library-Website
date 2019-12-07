from django.contrib import admin
from .models import Book, Author, Language, Genre, BookInstance


admin.site.register(Language)


class BookInline(admin.TabularInline):
    model = Book
    extra = 0


class BooksInstanceInline(admin.TabularInline):
    model = BookInstance
    extra = 0


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
    search_fields = ['first_name', 'last_name']
    inlines = [BookInline]


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')
    search_fields = ['author__first_name', 'author__last_name', 'genre__name']
    autocomplete_fields = ['author', 'genre']
    inlines = [BooksInstanceInline]


@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book', 'status', 'borrower', 'due_back', 'id')
    list_filter = ('status', 'due_back', 'language')
    search_fields = ['book__title', 'borrower__username', 'book__author__first_name',
                     'book__author__last_name', 'book__genre__name']
    autocomplete_fields = ['borrower']
    fieldsets = (
        (None, {'fields': ('book', 'imprint', 'language', 'id')}),
        ('Availability', {'fields': ('status', 'due_back', 'borrower')})
    )



