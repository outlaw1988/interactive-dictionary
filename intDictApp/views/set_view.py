# -*- coding: utf-8 -*-

from intDictApp.models import Category, Set, Setup, Word, SrcLanguage, TargetLanguage
from django.http import HttpResponseRedirect
from django.urls import reverse
from intDictApp.utils import *
from django.views.generic import TemplateView
from intDictApp.forms import SetForm, SetFormUpdate
from django.contrib.auth.mixins import LoginRequiredMixin


class CategorySetsList(LoginRequiredMixin, TemplateView):

    template_name = "intDictApp/category_sets_list.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        category = Category.objects.get(id=self.kwargs['pk'])

        self.request.session['category_name'] = category.name
        self.request.session['category_id'] = self.kwargs['pk']

        sets = Set.objects.filter(category=category).order_by('name')
        word_counters = []
        last_results = []
        best_results = []

        for set in sets:
            words = Word.objects.filter(set=set)
            setup = Setup.objects.get(set=set)
            last_results.append(setup.last_result)
            best_results.append(setup.best_result)
            word_counters.append(words.count())

        data['sets'] = sets
        data['category'] = category
        data['word_counters'] = word_counters
        data['last_results'] = last_results
        data['best_results'] = best_results

        return data


class AddSet(LoginRequiredMixin, TemplateView):

    template_name = "intDictApp/add_new_set.html"

    def get_context_data(self, **kwargs):
        category = Category.objects.get(id=self.request.session['category_id'])

        if "form" not in kwargs:
            # GET request
            form = SetForm(category=category, user=self.request.user)
        else:
            # POST request
            form = kwargs['form']

        table_list = list(range(1, 11))

        def_src_language = category.default_source_language
        def_target_language = category.default_target_language
        target_side = category.default_target_side

        context = {
            'id': self.request.session['category_id'],
            'tableLen': table_list,
            'src_language': def_src_language,
            'target_language': def_target_language,
            'target_side': target_side,
            'form': form
        }
        return context

    def post(self, request, **kwargs):
        category = Category.objects.get(id=self.request.session['category_id'])
        def_src_language = category.default_source_language
        def_target_language = category.default_target_language

        set_name = request.POST['set_name']
        current_user = request.user
        words_set = Set(user=current_user, category=category, name=set_name)

        target_language = request.POST['target_language']
        src_language = ""

        if target_language == def_target_language.name:
            target_language = def_target_language
            src_language = def_src_language

        elif target_language == def_src_language.name:
            target_language = TargetLanguage.objects.filter(user=request.user,
                                                            name=def_src_language.name)[0]
            src_language = SrcLanguage.objects.filter(user=request.user,
                                                      name=def_target_language.name)[0]

        target_side = request.POST['target_side']

        setup = Setup(set=words_set, src_language=src_language, target_language=target_language,
                      target_side=target_side, last_result=0, best_result=0)
        words_set.save()
        setup.save()

        request_keys = request.POST.keys()
        high_idx = find_highest_request_idx(request_keys)

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


class UpdateSet(LoginRequiredMixin, TemplateView):
    template_name = 'intDictApp/update_set.html'

    def get_context_data(self, **kwargs):
        words_set = Set.objects.filter(id=self.kwargs['pk'])[0]  # pk - uuid
        self.request.session['set_name'] = words_set.name
        self.request.session['set_id'] = str(self.kwargs['pk'])

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


class SetPreviewList(LoginRequiredMixin, TemplateView):

    template_name = "intDictApp/words_preview.html"

    def get_context_data(self, **kwargs):
        words_set = Set.objects.get(id=self.kwargs['pk'])
        self.request.session['set_name'] = words_set.name
        self.request.session['set_id'] = str(self.kwargs['pk'])

        words = Word.objects.filter(set=words_set)
        setup = Setup.objects.get(set=words_set)
        src_language = setup.src_language
        target_language = setup.target_language

        context = {
            'set': words_set,
            'words': words,
            'category_id': self.request.session['category_id'],
            'src_language': src_language,
            'target_language': target_language
        }

        return context


class RemoveSet(LoginRequiredMixin, TemplateView):

    template_name = "intDictApp/remove_set.html"

    def get_context_data(self, **kwargs):
        words_set = Set.objects.filter(id=kwargs['pk'])[0]
        context = {
            'set_name': words_set.name,
            'set_id': kwargs['pk']
        }
        return context

    def post(self, request, **kwargs):
        if "yes" in request.POST:
            words_set = Set.objects.filter(id=kwargs['pk'])[0]

            Setup.objects.filter(set=words_set).delete()
            Word.objects.filter(set=words_set).delete()
            Set.objects.filter(id=kwargs['pk']).delete()

        return HttpResponseRedirect(reverse('category-sets-list',
                                            kwargs={'pk': self.request.session['category_id']}))
