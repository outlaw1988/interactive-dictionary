from django.test import TestCase
from intDictApp.forms import CategoryForm, CategoryFormUpdate
from intDictApp.models import Category, SrcLanguage, TargetLanguage, User


class CategoryFormTest(TestCase):

    def setUp(self):
        self.user = User(username="outlaw1988")
        src_language_name = "Polish"
        target_language_name = "English"

        if SrcLanguage.objects.filter(name=src_language_name, user=self.user).count() == 0:
            src_language = SrcLanguage(name=src_language_name, user=self.user)
        else:
            src_language = SrcLanguage.objects.get(name=src_language_name, user=self.user)

        if TargetLanguage.objects.filter(name=target_language_name, user=self.user).count() == 0:
            target_language = TargetLanguage(name=target_language_name, user=self.user)
        else:
            target_language = TargetLanguage.objects.get(name=target_language_name, user=self.user)

        category_name = "Sport"
        def_target_side = "left"

        if Category.objects.filter(name=category_name, user=self.user).count() == 0:
            self.category = Category(name=category_name, user=self.user,
                                     default_source_language=src_language,
                                     default_target_language=target_language,
                                     default_target_side=def_target_side)

    def test_clean_category_name(self):
        src_language_name = "Polish"
        target_language_name = "English"
        src_language = SrcLanguage(name=src_language_name, user=self.user)
        target_language = TargetLanguage(name=target_language_name, user=self.user)

        form_data = {'category_name': "Sport2",
                     'default_source_language': src_language,
                     'default_target_language': target_language,
                     'default_target_side': "left"}
        form = CategoryForm(data=form_data, user=self.user)
        self.assertTrue(form.fields['category_name'].label == "category name" or
                        form.fields['category_name'].label == None)

    # def test_clean_languages(self):
    #     src_language_name = "Polish"
    #     target_language_name = "Polish"
    #     src_language = SrcLanguage(name=src_language_name, user=self.user)
    #     target_language = TargetLanguage(name=target_language_name, user=self.user)
    #
    #     form_data = {'category_name': "Sport2", 'default_source_language': src_language,
    #                  'default_target_language': target_language,
    #                  'default_target_side': "left"}
    #     form = CategoryForm(user=self.user, data=form_data)
    #
    #     self.assertFalse(form.is_valid())


class CategoryFormUpdateTest(TestCase):

    def setUp(self):
        self.user = User(username="outlaw1988")
        src_language_name = "Polish"
        target_language_name = "English"

        if SrcLanguage.objects.filter(name=src_language_name, user=self.user).count() == 0:
            src_language = SrcLanguage(name=src_language_name, user=self.user)
        else:
            src_language = SrcLanguage.objects.get(name=src_language_name, user=self.user)

        if TargetLanguage.objects.filter(name=target_language_name, user=self.user).count() == 0:
            target_language = TargetLanguage(name=target_language_name, user=self.user)
        else:
            target_language = TargetLanguage.objects.get(name=target_language_name, user=self.user)

        category_name = "Sport"
        def_target_side = "left"

        if Category.objects.filter(name=category_name, user=self.user).count() == 0:
            self.category = Category(name=category_name, user=self.user,
                                     default_source_language=src_language,
                                     default_target_language=target_language,
                                     default_target_side=def_target_side)

    def test_category_name(self):

        form_data = {'category_name': "Sport"}

        form = CategoryFormUpdate(data=form_data, user=self.user, category=self.category,
                                  prev_name=self.category.name)

        self.assertTrue(form.fields['category_name'].initial == "Sport")

    def test_target_side(self):

        form_data = {'default_target_side': "left"}
        form = CategoryFormUpdate(data=form_data, user=self.user, category=self.category,
                                  prev_name=self.category.name)

        self.assertTrue(form.fields['default_target_side'].initial == "left")
