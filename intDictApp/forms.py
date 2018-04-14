from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from .models import SrcLanguage, TargetLanguage, Category


class CategoryForm(forms.Form):

    def __init__(self, *args, **kwargs):

        self.user = kwargs.pop("user")
        print("User: ", self.user)
        super(CategoryForm, self).__init__(*args, **kwargs)

        self.fields['category_name'] = forms.CharField(max_length=100,
                                                       help_text="Please enter category name")
        self.fields['category_name'].label = "Category name"

        src_languages = SrcLanguage.objects.filter(user=self.user)
        target_languages = TargetLanguage.objects.filter(user=self.user)

        self.fields['src_language'] = forms.ModelChoiceField(queryset=src_languages)
        self.fields['src_language'].label = "Default source language"
        self.fields['target_language'] = forms.ModelChoiceField(queryset=target_languages)
        self.fields['target_language'].label = "Default target language"

    def clean_category_name(self):
        category_name = self.cleaned_data['category_name']
        category_to_check = Category.objects.filter(user=self.user, name=category_name)

        if category_to_check.count() > 0:
            raise ValidationError("This category already exists!")

    def clean(self):
        src_language = self.cleaned_data['src_language']
        target_language = self.cleaned_data['target_language']

        if src_language.name == target_language.name:
            raise ValidationError("Languages are the same!")


class LanguageForm(forms.Form):

    language_name = forms.CharField(max_length=100, help_text="Please enter language name")

    def __init__(self, *args, **kwargs):
        if len(kwargs) != 0:
            self.user = kwargs.pop("user")
        super(LanguageForm, self).__init__(*args, **kwargs)
        self.fields['language_name'].label = "Language name"

    def clean_language_name(self):
        name = self.cleaned_data['language_name']
        src_language = SrcLanguage.objects.filter(user=self.user, name=name)
        target_language = TargetLanguage.objects.filter(user=self.user, name=name)
        if src_language.count() > 0:
            raise ValidationError('This language already exists!')
        if target_language.count() > 0:
            raise ValidationError('This language already exists!')

        return name

# class LanguageForm(ModelForm):
#
#     def validate_unique(self):
#         pass
#
#     class Meta:
#         model = SrcLanguage
#         fields = ['name', ]
#         labels = {'name': _('Language name'), }
#         help_texts = {'name': _("Please enter language name")}

