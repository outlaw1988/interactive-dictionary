# -*- coding: utf-8 -*-

from django.shortcuts import render, redirect
from .models import Category, Set, Setup, Word, SrcLanguage, TargetLanguage
from django.http import HttpResponseRedirect
from django.urls import reverse
from .config import Config
from .utils import *
from django.views.generic import TemplateView, View
from braces import views
from .forms import LanguageForm, CategoryForm

config = Config()


def categories_list(request):
    categories = Category.objects.filter(user=request.user)
    # prevents rewinding
    config.clean_up()

    context = {
        'categories': categories
    }

    return render(request, 'categories.html', context)


def category_sets_list(request, pk):
    category = Category.objects.get(id=pk)
    config.current_category = category
    config.current_category_id = pk
    sets = Set.objects.filter(category=category)
    # prevents rewinding
    config.clean_up()

    context = {
        'category': category,
        'sets': sets
    }

    return render(request, 'intDictApp/category_sets_list.html', context)


def add_category(request):

    if request.method == "POST":

        form = CategoryForm(request.POST, user=request.user)

        if form.is_valid():

            category_name = request.POST['category_name']
            def_src_lan_id = request.POST['src_language']
            def_src_lan = SrcLanguage.objects.filter(id=def_src_lan_id)
            def_target_lan_id = request.POST['target_language']
            def_target_lan = TargetLanguage.objects.filter(id=def_target_lan_id)

            category = Category(user=request.user, name=category_name,
                                default_source_language=def_src_lan[0],
                                default_target_language=def_target_lan[0])
            category.save()

            return HttpResponseRedirect(reverse('categories'))
    else:

        form = CategoryForm(user=request.user)

    context = {
        'form': form
    }

    return render(request, "intDictApp/add_new_category.html", context)


def add_set(request):

    table_list = list(range(1, 11))

    src_language = config.current_category.default_source_language
    target_language = config.current_category.default_target_language

    context = {
        'id': config.current_category_id,
        'tableLen': table_list,
        'src_language': src_language,
        'target_language': target_language
    }

    if request.method == 'POST':
        set_name = request.POST['set_name_2']
        current_user = request.user
        words_set = Set(user=current_user, category=config.current_category,
                        name=set_name)

        setup = Setup(set=words_set, src_language=src_language, target_language=target_language,
                      target_side='l', last_result=0, best_result=0)
        words_set.save()
        setup.save()

        request_keys = request.POST.keys()
        high_idx = find_highest_request_idx(request_keys)
        # print("Highest idx: ", high_idx)

        for i in range(1, high_idx + 1):

            if "srcLan" + str(i) in request.POST:
                src_word = request.POST['srcLan' + str(i)]
                target_word = request.POST['tarLan' + str(i)]

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
        set = Set.objects.filter(id=self.kwargs['pk'])[0]  # pk - uuid
        config.current_set = set
        config.current_set_id = set.id

        words = Word.objects.filter(set=config.current_set)
        src_language = config.current_category.default_source_language
        target_language = config.current_category.default_target_language

        set_name = config.current_set.name
        size = len(words)

        context = {
            'set_name': set_name,
            'src_language': src_language,
            'target_language': target_language,
            'words': words,
            'id': config.current_category_id,
            'size': size
        }

        return context

    def post(self, request, **kwargs):
        print(request.POST)
        set_name = request.POST['set_name']

        words_set = config.current_set
        words_set.name = set_name
        words_set.save()

        request_keys = request.POST.keys()
        high_idx = find_highest_request_idx(request_keys)

        # clean up
        Word.objects.filter(set=words_set).delete()

        for i in range(1, high_idx + 1):

            if "srcLan" + str(i) in request.POST:
                src_word = request.POST['srcLan' + str(i)]
                target_word = request.POST['tarLan' + str(i)]

                if src_word == '' or target_word == '':
                    continue

                words = Word(set=words_set, src_word=src_word, target_word=target_word)
                words.save()

        return HttpResponseRedirect(reverse('category-sets-list', kwargs={'pk': config.current_category_id}))


def set_preview_list(request, pk):
    # pk - set UUID
    words_set = Set.objects.filter(id=pk)[0]
    config.current_set = words_set
    config.current_set_id = pk

    config.clean_up()

    words = Word.objects.filter(set=words_set)
    setup = Setup.objects.filter(set=words_set)
    src_language = setup[0].src_language
    target_language = setup[0].target_language

    context = {
        'set': words_set,
        'words': words,
        'category_id': config.current_category_id,
        'src_language': src_language,
        'target_language': target_language
    }

    return render(request, 'intDictApp/words_preview.html', context)


class ExamInit(TemplateView):

    template_name = 'intDictApp/exam.html'

    def get_context_data(self, **kwargs):
        words = Word.objects.filter(set=config.current_set)
        config.create_shuffle_list(len(words))
        shuffled_idx = config.shuffled_idxes[config.current_word_idx]
        words_to_show = words[shuffled_idx]
        src_word = words_to_show.src_word
        config.curr_corr_ans = words_to_show.target_word
        context = {
            'category': config.current_category,
            'category_id': config.current_category_id,
            'set': config.current_set,
            'src_word': src_word,
            'word_idx_to_show': config.current_word_idx + 1,
            'size': config.size
        }

        return context


class ExamCheck(views.CsrfExemptMixin, views.JsonRequestResponseMixin, View):

    require_json = True

    def post(self, request, *args, **kwargs):
        config.is_check_clicked = True
        answer = self.request_json["answer"]
        shuffled_idx = config.shuffled_idxes[config.current_word_idx]

        message = ''

        if answer == config.curr_corr_ans:
            message = "OK"
            config.corr_ans_num += 1
            config.assign_val_to_answers_list(shuffled_idx, 1)
        else:
            message = "WRONG, right answer is: " + config.curr_corr_ans
            config.assign_val_to_answers_list(shuffled_idx, 0)
        # print("Corr num: ", config.corr_ans_num)
        return self.render_json_response({"message": message})


class ExamNext(views.CsrfExemptMixin, views.JsonRequestResponseMixin, View):

    require_json = True

    def post(self, request, *args, **kwargs):

        words = Word.objects.filter(set=config.current_set)
        config.current_word_idx += 1

        # Set end
        if config.current_word_idx == config.size:
            result = int((float(config.corr_ans_num) / float(config.size)) * 100.0)
            # print("End Corr ans num: ", config.corr_ans_num)
            # print("Result: ", result)
            setup = Setup.objects.filter(set=config.current_set)
            setup = setup[0]
            if result > setup.best_result:
                setup.best_result = result
            
            setup.last_result = result
            config.result = result
            setup.save()

            context = {
                "request": ""
            }

            return self.render_json_response(context)

        else:
            shuffled_idx = config.shuffled_idxes[config.current_word_idx]

            if config.is_check_clicked is False:
                config.assign_val_to_answers_list(shuffled_idx, 0)

            config.is_check_clicked = False

            words_to_show = words[shuffled_idx]
            src_word = words_to_show.src_word
            config.curr_corr_ans = words_to_show.target_word

            context = {
                'src_word': src_word,
                'word_idx_to_show': config.current_word_idx + 1,
            }

            return self.render_json_response(context)


def exam_summary(request):

    words = Word.objects.filter(set=config.current_set)
    src_words, target_words = convert_queryset_to_list_words(words)
    setup = Setup.objects.filter(set=config.current_set)[0]

    # print("Current setup display: ", setup)

    last_result = config.result
    # TODO Database BUG
    # last_result = setup.last_result
    best_result = setup.best_result

    # print("Last result display: ", last_result)
    # print("Best result display: ", best_result)

    context = {
        'src_words': src_words,
        'target_words': target_words,
        'category': config.current_category,
        'set': config.current_set,
        'setup': setup,
        'last_result': last_result,
        'best_result': best_result,
        'answers_list': config.answers_list,
        'id': config.current_category_id
    }

    config.clean_up()

    return render(request, 'intDictApp/exam_summary.html', context)


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
