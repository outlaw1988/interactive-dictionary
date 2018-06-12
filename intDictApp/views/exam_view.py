# -*- coding: utf-8 -*-

from django.shortcuts import render
from intDictApp.models import Category, Set, Setup, Word
from intDictApp.config import ExamConfig
from intDictApp.utils import *
from django.views.generic import TemplateView, View
from braces import views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

config = ExamConfig()


class ExamInit(LoginRequiredMixin, TemplateView):
    template_name = 'intDictApp/exam.html'

    def get_context_data(self, **kwargs):
        config.clean_up()
        category = Category.objects.filter(id=self.request.session['category_id'])[0]
        words_set = Set.objects.filter(id=self.request.session['set_id'])[0]

        words = Word.objects.filter(set=words_set)
        config.create_shuffle_list(len(words))
        shuffled_idx = config.shuffled_idxes[config.current_word_idx]
        words_to_show = words[shuffled_idx]
        src_word = words_to_show.src_word
        config.curr_corr_ans = words_to_show.target_word
        context = {
            'category': category,
            'category_id': self.request.session['category_id'],
            'set': words_set,
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

        words_set = Set.objects.filter(id=self.request.session['set_id'])[0]
        words = Word.objects.filter(set=words_set)

        config.current_word_idx += 1

        # Set end
        if config.current_word_idx == config.size:
            result = int((float(config.corr_ans_num) / float(config.size)) * 100.0)
            # print("End Corr ans num: ", config.corr_ans_num)
            # print("Result: ", result)
            setup = Setup.objects.filter(set=words_set)
            setup = setup[0]
            if result > setup.best_result:
                setup.best_result = result
                config.best_result = result

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


# @login_required
# def exam_summary(request):
#     words_set = Set.objects.filter(id=request.session['set_id'])[0]
#     words = Word.objects.filter(set=words_set)
#     src_words, target_words = convert_queryset_to_list_words(words)
#     setup = Setup.objects.filter(set=words_set)[0]
#
#     last_result = config.result
#     # best_result = config.best_result
#     # TODO Database BUG
#     # last_result = setup.last_result
#     best_result = setup.best_result
#
#     context = {
#         'src_words': src_words,
#         'target_words': target_words,
#         'category_name': request.session['category_name'],
#         'set': words_set,
#         'last_result': last_result,
#         'best_result': best_result,
#         'answers_list': config.answers_list,
#         'id': request.session['category_id'],
#         'src_language': setup.src_language,
#         'target_language': setup.target_language
#     }
#
#     config.clean_up()
#
#     return render(request, 'intDictApp/exam_summary.html', context)


class ExamSummary(LoginRequiredMixin, TemplateView):

    template_name = "intDictApp/exam_summary.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data()
        words_set = Set.objects.filter(id=self.request.session['set_id'])[0]
        words = Word.objects.filter(set=words_set)
        src_words, target_words = convert_queryset_to_list_words(words)
        setup = Setup.objects.filter(set=words_set)[0]

        last_result = config.result
        # best_result = config.best_result
        # TODO Database BUG
        # last_result = setup.last_result
        best_result = setup.best_result

        data['src_words'] = src_words
        data['target_words'] = target_words
        data['category_name'] = self.request.session['category_name']
        data['set'] = words_set
        data['last_result'] = last_result
        data['best_result'] = best_result
        data['answers_list'] = config.answers_list
        data['id'] = self.request.session['category_id']
        data['src_language'] = setup.src_language
        data['target_language'] = setup.target_language

        config.clean_up()

        return data
