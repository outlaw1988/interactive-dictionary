# -*- coding: utf-8 -*-

from django.shortcuts import render, redirect
from intDictApp.models import Category, Set, Setup, Word, SrcLanguage, TargetLanguage
from django.http import HttpResponseRedirect
from django.urls import reverse
from intDictApp.config import Config
from intDictApp.utils import *
from django.views.generic import TemplateView, View
from braces import views
from intDictApp.forms import LanguageForm, CategoryForm, SetForm, SetFormUpdate

# config = Config()


##############  Set


def category_sets_list(request, pk):
    category = Category.objects.get(id=pk)
    # config.current_category = category
    request.session['category_name'] = category.name
    request.session['category_id'] = pk

    # config.current_category_id = pk
    sets = Set.objects.filter(category=category)
    # prevents rewinding
    # config.clean_up()

    context = {
        'category': category,
        'sets': sets
    }

    return render(request, 'intDictApp/category_sets_list.html', context)


def add_set(request):
    # print("Current category from request session: ", request.session['category'])
    table_list = list(range(1, 11))
    category = Category.objects.filter(id=request.session['category_id'])[0]

    # def_src_language = config.current_category.default_source_language
    # def_target_language = config.current_category.default_target_language
    # target_side = config.current_category.default_target_side

    def_src_language = category.default_source_language
    def_target_language = category.default_target_language
    target_side = category.default_target_side

    form = SetForm(user=request.user, category=category)
    context = {
        'id': request.session['category_id'],
        'tableLen': table_list,
        'src_language': def_src_language,
        'target_language': def_target_language,
        'target_side': target_side,
        'form': form
    }

    if request.method == 'POST':
        set_name = request.POST['set_name']
        current_user = request.user
        words_set = Set(user=current_user, category=category,
                        name=set_name)

        target_language = request.POST['target_language']
        src_language = ""

        if target_language == def_target_language:
            target_language = TargetLanguage.objects.filter(user=current_user,
                                                            name=def_target_language)[0]
            src_language = SrcLanguage.objects.filter(user=current_user, name=def_src_language)[0]
        else:
            target_language = TargetLanguage.objects.filter(user=current_user,
                                                            name=def_src_language)[0]
            src_language = SrcLanguage.objects.filter(user=current_user,
                                                      name=def_target_language)[0]

        target_side = request.POST['target_side']

        setup = Setup(set=words_set, src_language=src_language, target_language=target_language,
                      target_side=target_side, last_result=0, best_result=0)
        words_set.save()
        setup.save()

        request_keys = request.POST.keys()
        high_idx = find_highest_request_idx(request_keys)
        # print("Highest idx: ", high_idx)

        for i in range(1, high_idx + 1):

            if "left_field" + str(i) in request.POST:
                src_word = ""
                target_word = ""

                if target_side == "left":
                    src_word = request.POST['right_field' + str(i)]
                    target_word = request.POST['left_field' + str(i)]
                elif target_side == "right":
                    src_word = request.POST['left_field' + str(i)]
                    target_word = request.POST['right_field' + str(i)]

                if src_word == '' or target_word == '':
                    continue

                words = Word(set=words_set, src_word=src_word, target_word=target_word)
                words.save()

        return HttpResponseRedirect(reverse('category-sets-list', kwargs={'pk': context["id"]}))
    else:
        return render(request, 'intDictApp/add_new_set.html', context)


class UpdateSet(TemplateView):
    template_name = 'intDictApp/update_set.html'

    def get_context_data(self, **kwargs):
        words_set = Set.objects.filter(id=self.kwargs['pk'])[0]  # pk - uuid
        self.request.session['set_name'] = words_set.name
        self.request.session['set_id'] = str(self.kwargs['pk'])
        # config.current_set = set
        # config.current_set_id = set.id

        words = Word.objects.filter(set=words_set)

        setup = Setup.objects.filter(set=words_set)[0]
        src_language = setup.src_language.name
        target_language = setup.target_language.name
        target_side = setup.target_side

        set_name = words_set.name
        size = len(words)

        form = SetFormUpdate(user=self.request.user, set=words_set)

        context = {
            'set_name': set_name,
            'src_language': src_language,
            'target_language': target_language,
            'target_side': target_side,
            'words': words,
            'id': self.request.session['category_id'],
            'size': size,
            'form': form
        }

        return context

    def post(self, request, **kwargs):

        set_name = request.POST['set_name']
        current_user = request.user

        # Changing set name
        words_set = Set.objects.filter(id=self.request.session['set_id'])[0]  # pk - uuid
        words_set.name = set_name
        words_set.save()

        # Setup
        setup = Setup.objects.filter(set=words_set)[0]

        target_language = request.POST['target_language']
        src_language = ""

        if target_language == setup.target_language.name:
            target_language = TargetLanguage.objects.filter(user=current_user,
                                                            name=setup.target_language.name)[0]
            src_language = SrcLanguage.objects.filter(user=current_user,
                                                      name=setup.src_language.name)[0]
        else:
            target_language = TargetLanguage.objects.filter(user=current_user,
                                                            name=setup.src_language.name)[0]
            src_language = SrcLanguage.objects.filter(user=current_user,
                                                      name=setup.target_language.name)[0]

        setup.src_language = src_language
        setup.target_language = target_language

        target_side = request.POST['target_side']
        setup.target_side = target_side
        setup.save()
        # End setup

        request_keys = request.POST.keys()
        high_idx = find_highest_request_idx(request_keys)
        # print("Highest idx: ", high_idx)

        # clean up
        Word.objects.filter(set=words_set).delete()

        for i in range(1, high_idx + 1):

            if "left_field" + str(i) in request.POST:
                src_word = ""
                target_word = ""

                if target_side == "left":
                    src_word = request.POST['right_field' + str(i)]
                    target_word = request.POST['left_field' + str(i)]
                elif target_side == "right":
                    src_word = request.POST['left_field' + str(i)]
                    target_word = request.POST['right_field' + str(i)]

                if src_word == '' or target_word == '':
                    continue

                words = Word(set=words_set, src_word=src_word, target_word=target_word)
                words.save()

        return HttpResponseRedirect(reverse('category-sets-list',
                                            kwargs={'pk': self.request.session['category_id']}))


def set_preview_list(request, pk):
    # pk - set UUID
    words_set = Set.objects.filter(id=pk)[0]
    # config.current_set = words_set
    # config.current_set_id = pk
    request.session['set_name'] = words_set.name
    request.session['set_id'] = str(pk)

    # config.clean_up()

    words = Word.objects.filter(set=words_set)
    setup = Setup.objects.filter(set=words_set)
    src_language = setup[0].src_language
    target_language = setup[0].target_language

    context = {
        'set': words_set,
        'words': words,
        'category_id': request.session['category_id'],
        'src_language': src_language,
        'target_language': target_language
    }

    return render(request, 'intDictApp/words_preview.html', context)


