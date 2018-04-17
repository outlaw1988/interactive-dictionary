from django.urls import path
from . import views


urlpatterns = [
    path('', views.categories_list, name='categories'),
    path('category/<int:pk>', views.category_sets_list, name='category-sets-list'),
    path('add_category', views.add_category, name='add-category'),
    path('add_set', views.add_set, name='add-set'),
    path('preview/<uuid:pk>', views.set_preview_list, name='set-preview-list'),
    path('exam', views.ExamInit.as_view(), name='exam'),
    path('exam_check', views.ExamCheck.as_view(), name='exam-check'),
    path('exam_next', views.ExamNext.as_view(), name='exam-next'),
    path('exam_summary', views.exam_summary, name='exam-summary'),
    path('add_language', views.add_language, name='add-language'),
    path('update_set/<uuid:pk>', views.UpdateSet.as_view(), name='update-set')
]
