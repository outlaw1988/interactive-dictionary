from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse  # Used to generate URLs by reversing the URL pattern
import uuid


class Category(models.Model):

    class Meta:
        verbose_name_plural = "categories"

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100, help_text="Category name")
    default_source_language = models.ForeignKey('SrcLanguage', on_delete=models.SET_NULL,
                                                null=True)
    default_target_language = models.ForeignKey('TargetLanguage', on_delete=models.SET_NULL,
                                                null=True)
    sides = (
        ('left', 'left'),
        ('right', 'right'))

    default_target_side = models.CharField(max_length=5, choices=sides, default='left',
                                           help_text="Target language default side")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """
        Returns the url to access a detail record for this book.
        """
        return reverse('category-sets-list', args=[str(self.id)])


class Set(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="Unique ID")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100, help_text="Words set name")

    def __str__(self):
        return '{0} ({1})'.format(self.name, self.category)

    def get_absolute_url(self):
        return reverse('set-preview-list', args=[str(self.id)])

    def get_edit_url(self):
        return reverse('update-set', args=[str(self.id)])


class SrcLanguage(models.Model):

    name = models.CharField(max_length=200, help_text="Source/target "
                                                      "word language")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class TargetLanguage(models.Model):

    name = models.CharField(max_length=200, help_text="Source/target "
                                                      "word language")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class Setup(models.Model):

    set = models.ForeignKey('Set', on_delete=models.SET_NULL, null=True)
    # TODO Not allowed to use one class Language in two ForeignKeys
    src_language = models.ForeignKey('SrcLanguage', on_delete=models.SET_NULL,
                                     null=True)
    target_language = models.ForeignKey('TargetLanguage', on_delete=models.SET_NULL,
                                        null=True)

    sides = (
        ('left', 'left'),
        ('right', 'right'))

    target_side = models.CharField(max_length=5, choices=sides, default='left',
                                   help_text="Target language side")
    last_result = models.IntegerField(default=0)
    best_result = models.IntegerField(default=0)

    def __str__(self):
        return str(self.set)


class Word(models.Model):

    set = models.ForeignKey('Set', on_delete=models.SET_NULL, null=True)
    src_word = models.CharField(max_length=500)
    target_word = models.CharField(max_length=500)

    def __str__(self):
        return str(self.set)
