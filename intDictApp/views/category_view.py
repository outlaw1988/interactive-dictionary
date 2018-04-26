# -*- coding: utf-8 -*-

from django.shortcuts import render
from intDictApp.models import Category, Set, Setup, Word, SrcLanguage, TargetLanguage
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView, UpdateView, CreateView, ListView
from intDictApp.forms import LanguageForm, CategoryForm, CategoryFormUpdate
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required


class CategoriesList(LoginRequiredMixin, ListView):
    model = Category
    template_name = "categories.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        categories = Category.objects.filter(user=self.request.user)
        set_counters = []
        word_counters = []

        for category in categories:
            words_sets = Set.objects.filter(user=self.request.user, category=category)
            w_counter = 0
            for words_set in words_sets:
                words = Word.objects.filter(set=words_set)
                w_counter += words.count()
            set_counters.append(words_sets.count())
            word_counters.append(w_counter)

        data['set_counters'] = set_counters
        data['word_counters'] = word_counters
        return data

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)


class CategoryAddWithForm(LoginRequiredMixin, CreateView):
    model = Category
    template_name = "intDictApp/add_new_category.html"
    success_url = reverse_lazy('categories')
    form_class = CategoryForm


class CategoryUpdate(LoginRequiredMixin, UpdateView):
    template_name = "intDictApp/edit_category.html"
    model = Category
    success_url = reverse_lazy('categories')
    form_class = CategoryFormUpdate

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


class RemoveCategory(LoginRequiredMixin, TemplateView):

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


@login_required
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


# class AddLanguage(LoginRequiredMixin, CreateView):
#     template_name = "intDictApp/add_language.html"
#     success_url = reverse_lazy('categories')
#     form_class = LanguageForm
#
#     # def post(self, request, *args, **kwargs):
#     #     """
#     #     Handle POST requests: instantiate a form instance with the passed
#     #     POST variables and then check if it's valid.
#     #     """
#     #     form = self.get_form()
#     #     if form.is_valid():
#     #         return self.form_valid(form)
#     #     else:
#     #         return self.form_invalid(form)
#     #
#     def form_valid(self, form):
#         """If the form is valid, redirect to the supplied URL."""
#         print("Form valid called!!")
#         return HttpResponseRedirect(self.get_success_url())
#     #
#     # def form_invalid(self, form):
#     #     print("Form invalid called!!")
#     #     print("Request: ", self.request.POST)
#     #
#     # def get_form_kwargs(self):
#     #     # kwargs = super().get_form_kwargs()
#     #     print("Request method: ", self.request)
#     #     kwargs = {}
#     #     if self.request.POST:
#     #         kwargs = {'user': self.request.user}
#     #     return kwargs
