from django.contrib import admin
from .models import Category, Set, SrcLanguage, TargetLanguage, Setup, Word


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'default_source_language', 'default_target_language',
                    'default_target_side')


@admin.register(Set)
class SetAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'id', 'user')


@admin.register(SrcLanguage)
class SrcLanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')


@admin.register(TargetLanguage)
class TargetLanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')


@admin.register(Setup)
class SetupAdmin(admin.ModelAdmin):
    list_display = ('set', 'src_language', 'target_language', 'target_side',
                    'last_result', 'best_result')


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('set', 'src_word', 'target_word')
