from django.shortcuts import render, redirect
from .models import Category, Set, Setup, Word, SrcLanguage, TargetLanguage
from django.http import HttpResponseRedirect
from django.urls import reverse
from .config import Config

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
    if request.method == 'POST':
        category_name = request.POST['category_name']
        category = Category(user=request.user, name=category_name)
        category.save()

        return HttpResponseRedirect(reverse('categories'))
    else:
        return render(request, 'intDictApp/add_new_category.html')


def add_set(request):

    table_list = list(range(1, 11))

    context = {
        'id': config.current_category_id,
        'tableLen': table_list
    }

    if request.method == 'POST':
        set_name = request.POST['set_name_2']
        current_user = request.user
        words_set = Set(user=current_user, category=config.current_category,
                        name=set_name)
        # TODO Let user choose desired languages
        src_language = SrcLanguage.objects.filter(name='Polish')[0]
        target_language = TargetLanguage.objects.filter(name='English')[0]

        setup = Setup(set=words_set, src_language=src_language, target_language=target_language,
                      target_side='l', last_result=0, best_result=0)
        words_set.save()
        setup.save()

        for i in table_list:
            src_word = request.POST['srcLan' + str(i)]
            target_word = request.POST['tarLan' + str(i)]

            if src_word == '' or target_word == '':
                continue

            words = Word(set=words_set, src_word=src_word, target_word=target_word)
            words.save()

        return HttpResponseRedirect(reverse('category-sets-list', kwargs={'pk': context["id"]}))
    else:
        return render(request, 'intDictApp/add_new_set.html', context)


def set_preview_list(request, pk):
    # pk - set UUID
    words_set = Set.objects.filter(id=pk)[0]
    config.current_set = words_set
    config.current_set_id = pk

    config.clean_up()

    words = Word.objects.filter(set=words_set)

    context = {
        'set': words_set,
        'words': words,
        'category_id': config.current_category_id,
    }

    return render(request, 'intDictApp/words_preview.html', context)


def exam(request):

    def create_context():
        shuffled_idx = config.shuffled_idxes[config.current_word_idx]
        words_to_show = words[shuffled_idx]
        config.curr_corr_ans = words_to_show.target_word
        context = {
            'category': config.current_category,
            'set': config.current_set,
            'words': words_to_show,
            'current_word_idx': config.current_word_idx + 1,
            'size': config.size
        }

        return context

    words = Word.objects.filter(set=config.current_set)

    # exam view initialization
    if request.method == 'GET':
        config.create_shuffle_list(len(words))
        return render(request, 'intDictApp/exam.html', create_context())

    # When user clicks "Submit"
    if request.method == 'POST':
        answer = request.POST['answer']
        if answer == config.curr_corr_ans:
                config.corr_ans_num += 1

        config.current_word_idx += 1

        if config.current_word_idx == config.size:

            result = int((float(config.corr_ans_num) / float(config.size)) * 100.0)
            setup = Setup.objects.filter(set=config.current_set)[0]

            if result > setup.best_result:
                setup.best_result = result

            setup.last_result = result
            setup.save()
            config.clean_up()

            return HttpResponseRedirect(reverse('category-sets-list',
                                                kwargs={'pk': config.current_category_id}))

        return render(request, 'intDictApp/exam.html', create_context())
