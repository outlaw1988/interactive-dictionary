from django.test import TestCase
from django.urls import reverse
from intDictApp.models import Category, SrcLanguage, TargetLanguage, User


class CategoriesListTest(TestCase):

    def setUp(self):
        self.user = User(username="outlaw1988")
        src_language_name = "Polish"
        target_language_name = "English"

        src_language = SrcLanguage(name=src_language_name, user=self.user)
        target_language = TargetLanguage(name=target_language_name, user=self.user)

        category_name = "Sport"
        def_target_side = "left"

        if Category.objects.filter(name=category_name, user=self.user).count() == 0:
            self.category = Category(name=category_name, user=self.user,
                                     default_source_language=src_language,
                                     default_target_language=target_language,
                                     default_target_side=def_target_side)

    def test_view_url_exists(self):
        resp = self.client.get(reverse('categories'))
        self.assertEquals(resp.status_code, 200)
