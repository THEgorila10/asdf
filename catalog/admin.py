from django.contrib import admin
from django.utils.html import format_html
from .models import Author, Genre, Book, BookInstance, Language
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class BooksInstanceInline(admin.TabularInline):
    model = BookInstance
class BookInline(admin.TabularInline):
    model = Book
    extra = 5

admin.site.unregister(User)
admin.site.register(Genre)

admin.site.register(Language)


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'display_groups')
    def display_groups(self, obj):
        return ', '.join(group.name for group in obj.groups.all())
    display_groups.short_description = 'קבוצה'


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
    inlines = [BookInline]
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')
    inlines = [BooksInstanceInline]
    
@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book', 'status', 'due_back', 'id' ,'borrower')
    list_filter = ('status', 'due_back' )
   


    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            # הוספנו את 'borrower' בסוף
            'fields': ('status', 'due_back', 'borrower') 
        }),
    )
    
    