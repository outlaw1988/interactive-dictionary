from django.urls import path
from . import views


urlpatterns = [
    path('', views.categories_list, name='categories'),
    path('category/<int:pk>', views.category_sets_list, name='category-sets-list'),
    path('add_category', views.add_category, name='add-category'),
    path('add_set', views.add_set, name='add-set'),
    path('preview/<uuid:pk>', views.set_preview_list, name='set-preview-list'),
    path('exam', views.exam, name='exam'),
    path('exam_summary', views.exam_summary, name='exam-summary')
]
