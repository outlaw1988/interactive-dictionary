from django import forms
from django.core.exceptions import ValidationError
from .models import SrcLanguage, TargetLanguage, Category, Set, Setup


class CategoryForm(forms.Form):

    def __init__(self, *args, **kwargs):
        if "user" in kwargs:
            self.user = kwargs.pop('user')
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.fields['category_name'] = forms.CharField(max_length=100,
                                                       help_text="Please enter category name",
                                                       required=True)
        self.fields['default_source_language'] = forms.ModelChoiceField(queryset=SrcLanguage.objects.all())
        self.fields['default_target_language'] = forms.ModelChoiceField(queryset=TargetLanguage.objects.all())

        sides = (
            ('left', 'left'),
            ('right', 'right'))

        self.fields['default_target_side'] = forms.ChoiceField(choices=sides)

    def clean_category_name(self):
        print("Clean category name called...")
        print("User is: ", self.user)
        print("Cleaned data: ", self.cleaned_data)
        category_name = self.cleaned_data['category_name']
        category_to_check = Category.objects.filter(name=category_name, user=self.user)

        if category_to_check.count() > 0:
            self.add_error('category_name', ValidationError("This category already exists!"))

    def clean(self):
        if ("default_source_language" in self.cleaned_data) and \
                                ("default_target_language" in self.cleaned_data):
            src_language = self.cleaned_data['default_source_language']
            target_language = self.cleaned_data['default_target_language']
            if src_language.name == target_language.name:
                self.add_error(None, ValidationError('Languages are the same'))


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

    def __init__(self, *args, **kwargs):
        # print("Form kwargs: ", kwargs)
        if "user" in kwargs:
            self.user = kwargs.pop("user")
        super(LanguageForm, self).__init__(*args, **kwargs)
        self.fields['language_name'] = forms.CharField(max_length=100,
                                                       help_text="Please enter language name",
                                                       required=True)

    def clean_language_name(self):
        print("Clean language name called!!")
        name = self.cleaned_data['language_name']
        src_language = SrcLanguage.objects.filter(user=self.user, name=name)
        target_language = TargetLanguage.objects.filter(user=self.user, name=name)
        if src_language.count() > 0 or target_language.count() > 0:
            self.add_error(None, ValidationError('This language already exists!'))


# class LanguageForm(forms.ModelForm):
#
#     def __init__(self, *args, **kwargs):
#         print("Form kwargs: ", kwargs)
#         if len(kwargs) != 0:
#             self.user = kwargs.pop("user")
#         super(LanguageForm, self).__init__(*args, **kwargs)
#         # self.fields['language_name'].label = "Language name"
#
#     def clean(self):
#         print("Clean name called!!")
#
#     class Meta:
#         model = SrcLanguage
#         fields = ['name']

# class LanguageForm(forms.ModelForm):
#
#     # def __init__(self, *args, **kwargs):
#     #     print("Form kwargs: ", kwargs)
#     #     if len(kwargs) != 0:
#     #         self.user = kwargs.pop("user")
#     #     super(LanguageForm, self).__init__(*args, **kwargs)
#     #     # self.fields['language_name'].label = "Language name"
#
#     def clean(self):
#         # print("Clean language name called!!")
#         # print("Cleaned data: ", self.cleaned_data)
#         name = self.cleaned_data['name']
#         # TODO Add user
#         src_language = SrcLanguage.objects.filter(name=name)
#         target_language = TargetLanguage.objects.filter(name=name)
#         if src_language.count() > 0 or target_language.count() > 0:
#             self.add_error(None, ValidationError('This language already exists!'))
#
#     class Meta:
#         model = SrcLanguage
#         fields = ['user', 'name']
