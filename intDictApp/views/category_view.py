# -*- coding: utf-8 -*-

from django.shortcuts import render
from intDictApp.models import Category, Set, Setup, Word, SrcLanguage, TargetLanguage
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView
from intDictApp.forms import LanguageForm, CategoryForm


def categories_list(request):
    categories = Category.objects.filter(user=request.user)

    context = {
        'categories': categories
    }

    return render(request, 'categories.html', context)


def add_category(request):

    if request.method == "POST":
        form = CategoryForm(request.POST, user=request.user)

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

        form = CategoryForm(user=request.user)

    context = {
        'form': form
    }

    return render(request, "intDictApp/add_new_category.html", context)


class EditCategory(TemplateView):
    pass


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
