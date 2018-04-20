# -*- coding: utf-8 -*-

from django.shortcuts import render
from intDictApp.models import Category, Set, Setup, Word, SrcLanguage, TargetLanguage
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView, FormView
from intDictApp.forms import LanguageForm, CategoryForm


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


def add_category(request):

    if request.method == "POST":
        form = CategoryForm(request.POST, user=request.user, edit_mode=False)

        if form.is_valid():
            category_name = request.POST['category_name']
            def_src_lan_id = request.POST['src_language']
            def_src_lan = SrcLanguage.objects.filter(id=def_src_lan_id)
            def_target_lan_id = request.POST['target_language']
            def_target_lan = TargetLanguage.objects.filter(id=def_target_lan_id)
            def_target_side = request.POST['def_target_side']

            category = Category(user=request.user, name=category_name,
                                default_source_language=def_src_lan[0],
                                default_target_language=def_target_lan[0],
                                default_target_side=def_target_side)
            category.save()

            return HttpResponseRedirect(reverse('categories'))
    else:

        form = CategoryForm(user=request.user, edit_mode=False)

    context = {
        'form': form
    }

    return render(request, "intDictApp/add_new_category.html", context)


def edit_category(request, pk):
    request.session['category_id'] = pk

    if request.method == "POST":
        print("PK post: ", pk)

        category = Category.objects.filter(user=request.user, id=pk)[0]
        form = CategoryForm(user=request.user, edit_mode=False)

        if form.is_valid():
            print("Form is valid!!!!")
            category_name = request.POST['category_name']
            def_src_lan_id = request.POST['src_language']
            def_src_lan = SrcLanguage.objects.filter(id=def_src_lan_id)
            def_target_lan_id = request.POST['target_language']
            def_target_lan = TargetLanguage.objects.filter(id=def_target_lan_id)
            def_target_side = request.POST['def_target_side']

            category.name = category_name
            category.default_source_language = def_src_lan
            category.default_target_language = def_target_lan
            category.default_target_side = def_target_side
            category.save()

            return HttpResponseRedirect(reverse('categories'))
        else:
            print("Form is invalid!!!!")
            context = {
                'form': form,
                'category_id': request.session['category_id']
            }

            return render(request, "intDictApp/edit_category.html", context)

    else:
        print("PK get: ", pk)
        category = Category.objects.filter(user=request.user, id=pk)[0]
        form = CategoryForm(user=request.user, edit_mode=True, category=category)

        context = {
            'form': form,
            'category_id': request.session['category_id']
        }

        return render(request, "intDictApp/edit_category.html", context)


# class AddCategory(FormView):
#
#     template_name = "intDictApp/add_or_edit_category.html"
#     form_class = CategoryForm
#     success_url = ""
#
#     def get_context_data(self, **kwargs):
#
#         if "pk" in kwargs:
#             self.request.session['category_edit_mode'] = True
#             category = Category.objects.filter(id=kwargs['pk'])[0]
#             form = CategoryForm(user=self.request.user, edit_mode=True, category=category)
#         else:
#             self.request.session['category_edit_mode'] = False
#             form = CategoryForm(user=self.request.user, edit_mode=False)
#         context = {
#             'form': form,
#             'category_id': self.request.session['category_id'],
#             'edit_mode': self.request.session['category_edit_mode']
#         }
#         return context
#
#     def form_valid(self, form):
#         print("The form is valid!!")
#         return super().form_valid(form)
#
#     def form_invalid(self, form):
#         pass


# class AddOrEditCategory(TemplateView):
#
#     template_name = "intDictApp/add_or_edit_category.html"
#
#     def get_context_data(self, **kwargs):
#         if "pk" in kwargs:
#             self.request.session['category_edit_mode'] = True
#             category = Category.objects.filter(id=kwargs['pk'])[0]
#             form = CategoryForm(user=self.request.user, edit_mode=True, category=category)
#         else:
#             self.request.session['category_edit_mode'] = False
#             form = CategoryForm(user=self.request.user, edit_mode=False)
#         context = {
#             'form': form,
#             'category_id': self.request.session['category_id'],
#             'edit_mode': self.request.session['category_edit_mode']
#         }
#         return context
#
#     def post(self, request, **kwargs):
#         # print("Edit mode in post: ", self.request.session['category_edit_mode'])
#         # print("PK: ", kwargs['pk'])
#         if self.request.session['category_edit_mode']:
#             print("In category edit mode, PK: ", kwargs['pk'])
#             category = Category.objects.filter(id=kwargs['pk'])[0]
#             form = CategoryForm(user=self.request.user, edit_mode=True, category=category)
#
#             if form.is_valid():
#                 print('Edit mode')
#
#                 return HttpResponseRedirect(reverse('categories'))
#             else:
#                 context = self.get_context_data()
#                 context['form'] = form
#
#                 return render(request, "intDictApp/add_or_edit_category.html", context)
#
#         else:
#             form = CategoryForm(user=self.request.user, edit_mode=False)
#
#             if form.is_valid():
#                 print("Form is valid!!!!")
#                 category_name = request.POST['category_name']
#                 def_src_lan_id = request.POST['src_language']
#                 def_src_lan = SrcLanguage.objects.filter(id=def_src_lan_id)
#                 def_target_lan_id = request.POST['target_language']
#                 def_target_lan = TargetLanguage.objects.filter(id=def_target_lan_id)
#                 def_target_side = request.POST['def_target_side']
#
#                 category = Category(user=request.user, name=category_name,
#                                     default_source_language=def_src_lan[0],
#                                     default_target_language=def_target_lan[0],
#                                     default_target_side=def_target_side)
#                 category.save()
#
#                 return HttpResponseRedirect(reverse('categories'))
#
#             print("Form is invalid!!!!")
#             context = self.get_context_data(**kwargs)
#             context['form'] = form
#
#             return self.render_to_response(self.get_context_data(request=self.request, form=form))


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
