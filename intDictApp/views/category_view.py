# -*- coding: utf-8 -*-

from django.shortcuts import render
from intDictApp.models import Category, Set, Setup, Word, SrcLanguage, TargetLanguage
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView, UpdateView, CreateView
from intDictApp.forms import LanguageForm, CategoryForm, CategoryFormUpdate
from django.urls import reverse_lazy


def categories_list(request):
    categories = Category.objects.filter(user=request.user)
    set_counters = []
    word_counters = []

    for category in categories:
        words_sets = Set.objects.filter(user=request.user, category=category)
        w_counter = 0
        for words_set in words_sets:
            words = Word.objects.filter(set=words_set)
            w_counter += words.count()
        set_counters.append(words_sets.count())
        word_counters.append(w_counter)

    context = {
        'categories': categories,
        'set_counters': set_counters,
        'word_counters': word_counters
    }

    return render(request, 'categories.html', context)


class CategoryAdd(CreateView):
    model = Category
    template_name = "intDictApp/add_new_category.html"
    fields = ['name', 'default_source_language', 'default_target_language',
              'default_target_side']


class CategoryAddWithForm(CreateView):
    model = Category
    template_name = "intDictApp/add_new_category.html"
    success_url = reverse_lazy('categories')
    form_class = CategoryForm


class CategoryUpdate(UpdateView):
    template_name = "intDictApp/edit_category.html"
    model = Category
    fields = ['user', 'name', 'default_source_language', 'default_target_language',
              'default_target_side']
    success_url = reverse_lazy('categories')
    # form_class = CategoryFormUpdate

    # def get_form(self, form_class=None):
    #     form_class = self.get_form_class()
    #     category = Category.objects.filter(id=self.kwargs['pk'])[0]
    #     return form_class(user=self.request.user, category=category)

    # def get_form_class(self):
    #     return CategoryFormUpdate

    # def get_form(self, form_class=CategoryFormUpdate):
    #     category = Category.objects.filter(user=self.request.user, id=self.kwargs['pk'])[0]
    #     return CategoryFormUpdate(user=self.request.user, category=category)
    #
    # def form_valid(self, form):
    #     return super(CategoryUpdate, self).form_valid(form)


class RemoveCategory(TemplateView):

    template_name = "intDictApp/remove_category.html"

    def get_context_data(self, **kwargs):
        category = Category.objects.filter(id=kwargs['pk'])[0]
        context = {
            'category_name': category.name,
            'category_id': kwargs['pk']
        }
        return context

    def post(self, request, **kwargs):

        if "yes" in request.POST:
            category = Category.objects.filter(id=kwargs['pk'])[0]
            words_sets = Set.objects.filter(category=category)

            for words_set in words_sets:
                Setup.objects.filter(set=words_set).delete()
                Word.objects.filter(set=words_set).delete()

            Set.objects.filter(category=category).delete()
            Category.objects.filter(id=kwargs['pk']).delete()

        return HttpResponseRedirect(reverse('categories'))


def add_language(request):

    if request.method == "POST":

        form = LanguageForm(request.POST, user=request.user)

        if form.is_valid():

            language_name = request.POST["language_name"]
            src_language = SrcLanguage(user=request.user, name=language_name)
            target_language = TargetLanguage(user=request.user, name=language_name)
            src_language.save()
            target_language.save()

            return HttpResponseRedirect(reverse('categories'))
    else:

        form = LanguageForm()

    context = {
        'form': form
    }

    return render(request, "intDictApp/add_language.html", context)
