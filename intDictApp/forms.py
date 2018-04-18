from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from .models import SrcLanguage, TargetLanguage, Category, Set, Setup


class CategoryForm(forms.Form):

    def __init__(self, *args, **kwargs):

        self.user = kwargs.pop("user")
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

        sides = (
            ('left', 'left'),
            ('right', 'right'))

        self.fields['def_target_side'] = forms.ChoiceField(choices=sides)
        self.fields['def_target_side'].label = "Default target side"

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


class SetForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.category_name = kwargs.pop('category')
        super(SetForm, self).__init__(*args, **kwargs)
        self.fields['set_name'] = forms.CharField(max_length=100,
                                                  help_text="Please enter set name")
        self.fields['set_name'].label = "Set name"

        category = Category.objects.filter(user=self.user, name=self.category_name)[0]
        src_lan = category.default_source_language.name
        target_lan = category.default_target_language.name
        target_side = category.default_target_side
        source_side = ""

        if target_side == 'left':
            # target_side = "left"
            source_side = "right"
        elif target_side == 'right':
            # target_side = "right"
            source_side = "left"

        languages = (
            (target_lan, target_lan),
            (src_lan, src_lan))

        self.fields['target_language'] = forms.ChoiceField(choices=languages)

        sides = (
            (target_side, target_side),
            (source_side, source_side))

        self.fields['target_side'] = forms.ChoiceField(choices=sides)

    # def clean_set_name(self):
    #     set_name = self.cleaned_data['set_name']
    #     set_to_check = Set.objects.filter(user=self.user, name=set_name, category=self.category)
    #
    #     if set_to_check.count() > 0:
    #         raise ValidationError("This set, within selected category, already exists!")


class SetFormUpdate(forms.Form):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.set = kwargs.pop('set')
        super(SetFormUpdate, self).__init__(*args, **kwargs)
        self.fields['set_name'] = forms.CharField(max_length=100,
                                                  help_text="Please enter set name")
        self.fields['set_name'].initial = self.set.name

        setup = Setup.objects.filter(set=self.set)[0]
        target_language = setup.target_language.name
        src_language = setup.src_language.name

        languages = (
            (target_language, target_language),
            (src_language, src_language))

        self.fields['target_language'] = forms.ChoiceField(choices=languages)

        target_side = setup.target_side
        source_side = ""

        if target_side == 'left':
            source_side = "right"
        elif target_side == 'right':
            source_side = "left"

        sides = (
            (target_side, target_side),
            (source_side, source_side))

        self.fields['target_side'] = forms.ChoiceField(choices=sides)


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
