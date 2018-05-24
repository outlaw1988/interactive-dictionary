# -*- coding: utf-8 -*-

from intDictApp.models import Category, Set, Setup, Word, SrcLanguage, TargetLanguage
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView, UpdateView, CreateView, ListView
from intDictApp.forms import LanguageForm, CategoryForm, CategoryFormUpdate
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin


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
        return Category.objects.filter(user=self.request.user).order_by('name')


class CategoryAdd(LoginRequiredMixin, TemplateView):
    template_name = "intDictApp/add_new_category.html"

    def get_context_data(self, **kwargs):
        if "form" not in kwargs:
            # GET request
            form = CategoryForm(user=self.request.user)
        else:
            # POST request
            form = kwargs['form']

        context = {
            'form': form
        }
        return context

    def post(self, request):
        print("POST request: ", request.POST)
        form = CategoryForm(request.POST, user=self.request.user)
        if form.is_valid():
            category_name = request.POST['category_name']
            def_src_lan_id = request.POST['default_source_language']
            def_src_lan = SrcLanguage.objects.filter(id=def_src_lan_id)[0]
            def_target_lan_id = request.POST['default_target_language']
            def_target_lan = TargetLanguage.objects.filter(id=def_target_lan_id)[0]
            def_target_side = request.POST['default_target_side']
            category = Category(name=category_name, default_source_language=def_src_lan,
                                default_target_language=def_target_lan,
                                default_target_side=def_target_side, user=self.request.user)
            category.save()

            return HttpResponseRedirect(reverse('categories'))
        else:
            context = self.get_context_data(form=form)
            return self.render_to_response(context=context)


class CategoryUpdate(LoginRequiredMixin, TemplateView):

    template_name = "intDictApp/edit_category.html"

    def get_context_data(self, **kwargs):
        category = Category.objects.filter(id=self.kwargs['pk'])[0]
        if "form" not in kwargs:
            # GET request
            form = CategoryFormUpdate(category=category, user=self.request.user)
        else:
            # POST request
            form = kwargs['form']

        context = {
            'form': form,
            'category_id': self.kwargs['pk']
        }
        return context

    def post(self, request, *args, **kwargs):
        category = Category.objects.filter(id=self.kwargs['pk'])[0]
        form = CategoryFormUpdate(request.POST, user=self.request.user, category=category,
                                  prev_name=category.name)
        if form.is_valid():
            category_name = request.POST['category_name']
            def_src_lan_id = request.POST['default_source_language']
            def_src_lan = SrcLanguage.objects.filter(id=def_src_lan_id)[0]
            def_target_lan_id = request.POST['default_target_language']
            def_target_lan = TargetLanguage.objects.filter(id=def_target_lan_id)[0]
            def_target_side = request.POST['default_target_side']

            category = Category.objects.filter(id=self.kwargs['pk'])[0]
            category.name = category_name
            category.default_source_language = def_src_lan
            category.default_target_language = def_target_lan
            category.default_target_side = def_target_side
            category.save()

            return HttpResponseRedirect(reverse('categories'))
        else:
            context = self.get_context_data(form=form)
            return self.render_to_response(context=context)


# class CategoryUpdate(LoginRequiredMixin, UpdateView):
#     template_name = "intDictApp/edit_category.html"
#     model = Category
#     success_url = reverse_lazy('categories')
#     form_class = CategoryFormUpdate
#
#     def post(self, request, *args, **kwargs):
#         form = CategoryForm(request.POST, user=self.request.user, prev_name="Previous name")
#         if form.is_valid():
#             print("Form is valid!")
#             return HttpResponseRedirect(reverse('categories'))
#         else:
#             print("Invalid form!")
#             context = self.get_context_data(form=form)
#             return self.render_to_response(context=context)
#
#     # def get_form(self, form_class=None):
#     #     form_class = self.get_form_class()
#     #     category = Category.objects.filter(id=self.kwargs['pk'])[0]
#     #     return form_class(user=self.request.user, category=category)
#
#     # def get_form_class(self):
#     #     return CategoryFormUpdate
#
#     # def get_form(self, form_class=CategoryFormUpdate):
#     #     category = Category.objects.filter(user=self.request.user, id=self.kwargs['pk'])[0]
#     #     return CategoryFormUpdate(user=self.request.user, category=category)
#     #
#     # def form_valid(self, form):
#     #     return super(CategoryUpdate, self).form_valid(form)


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


class LanguageAdd(LoginRequiredMixin, TemplateView):

    template_name = "intDictApp/add_language.html"

    def get_context_data(self, **kwargs):
        if "form" not in kwargs:
            # GET request
            form = LanguageForm()
        else:
            # POST request
            form = kwargs['form']

        context = {
            'form': form
        }
        return context

    def post(self, request):
        form = LanguageForm(request.POST, user=self.request.user)
        if form.is_valid():
            language_name = request.POST['language_name']
            src_language = SrcLanguage(user=self.request.user, name=language_name)
            target_language = TargetLanguage(user=self.request.user, name=language_name)
            src_language.save()
            target_language.save()
            return HttpResponseRedirect(reverse('languages'))
        else:
            context = self.get_context_data(form=form)
            return self.render_to_response(context=context)


class Languages(LoginRequiredMixin, ListView):

    model = SrcLanguage
    template_name = "languages.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        src_languages = SrcLanguage.objects.filter(user=self.request.user)
        data['src_languages'] = src_languages

        return data


class RemoveLanguage(LoginRequiredMixin, TemplateView):

    template_name = "intDictApp/remove_language.html"

    def get_context_data(self, **kwargs):
        language = SrcLanguage.objects.get(id=kwargs['pk'])
        context = {
            'language_name': language.name,
            'language_id': kwargs['pk']
        }
        return context

    def post(self, request, **kwargs):

        if "yes" in request.POST:
            src_language = SrcLanguage.objects.get(id=kwargs['pk'])
            language_name = src_language.name
            src_language.delete()
            TargetLanguage.objects.filter(name=language_name, user=self.request.user).delete()

        return HttpResponseRedirect(reverse('languages'))
