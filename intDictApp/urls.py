from django.urls import path
from .views import category_view, set_view, exam_view


urlpatterns = [
    path('', category_view.categories_list, name='categories'),
    path('category/<int:pk>', set_view.category_sets_list, name='category-sets-list'),
    path('add_category', category_view.add_category, name='add-category'),
    path('add_set', set_view.add_set, name='add-set'),
    path('preview/<uuid:pk>', set_view.set_preview_list, name='set-preview-list'),
    path('exam', exam_view.ExamInit.as_view(), name='exam'),
    path('exam_check', exam_view.ExamCheck.as_view(), name='exam-check'),
    path('exam_next', exam_view.ExamNext.as_view(), name='exam-next'),
    path('exam_summary', exam_view.exam_summary, name='exam-summary'),
    path('add_language', category_view.add_language, name='add-language'),
    path('update_set/<uuid:pk>', set_view.UpdateSet.as_view(), name='update-set'),
    path('edit_category/<int:pk>', category_view.EditCategory.as_view(), name="edit-category")
]
