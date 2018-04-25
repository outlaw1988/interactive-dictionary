from django import forms
from django.core.exceptions import ValidationError
from .models import SrcLanguage, TargetLanguage, Category, Set, Setup


class CategoryForm(forms.ModelForm):
    # TODO How to pass user?
    def clean(self):
        category_name = self.cleaned_data['name']
        category_to_check = Category.objects.filter(name=category_name)

        if category_to_check.count() > 0:
            self.add_error('name', ValidationError("This category already exists!"))

        if ("default_source_language" in self.cleaned_data) and \
                ("default_target_language" in self.cleaned_data):
            src_language = self.cleaned_data['default_source_language']
            target_language = self.cleaned_data['default_target_language']
            if src_language.name == target_language.name:
                # raise ValidationError("Languages are the same!")
                self.add_error(None, ValidationError('Languages are the same'))
        # self.cleaned_data['name'] = "Music2"
        # return cleaned_data

    # def clean_name(self):
    #     print("Clean name called!!!!")
    #     print("Cleaned data: ", self.cleaned_data)
    #     #cleaned_data = super(CategoryForm, self).clean()
    #     category_name = self.cleaned_data['name']
    #     # TODO name is empty https://stackoverflow.com/questions/19864854/this-field-cannot-be-null-error-in-a-django-1-5-modelform
    #     category_to_check = Category.objects.filter(name=category_name)
    #
    #     if category_to_check.count() > 0:
    #         self.add_error(None,
    #                        ValidationError("This category already exists!"))
    #     #return cleaned_data

    class Meta:
        model = Category
        fields = ['user', 'name', 'default_source_language', 'default_target_language',
                  'default_target_side']


class CategoryFormUpdate(forms.ModelForm):

    class Meta:
        model = Category
        fields = ['user', 'name', 'default_source_language', 'default_target_language',
                  'default_target_side']

    def clean(self):
        print("Clean called - CategoryFormUpdate!!")
        # category_name = self.cleaned_data['name']
        # TODO User! + validation of category existence
        # category_to_check = Category.objects.filter(name=category_name)
        #
        # if category_to_check.count() > 0:
        #     self.add_error('name', ValidationError("This category already exists!"))

        if ("default_source_language" in self.cleaned_data) and \
                ("default_target_language" in self.cleaned_data):
            src_language = self.cleaned_data['default_source_language']
            target_language = self.cleaned_data['default_target_language']
            if src_language.name == target_language.name:
                # raise ValidationError("Languages are the same!")
                self.add_error(None, ValidationError('Languages are the same'))


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
