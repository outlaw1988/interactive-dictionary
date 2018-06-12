from django.urls import path
from .views import category_view, set_view, exam_view, registration_view


urlpatterns = [
    path('', category_view.CategoriesList.as_view(), name='categories'),
    path('category/<int:pk>', set_view.CategorySetsList.as_view(), name='category-sets-list'),
    path('add_category', category_view.CategoryAdd.as_view(), name='add-category'),
    path('edit_category/<int:pk>', category_view.CategoryUpdate.as_view(),
         name="edit-category"),
    path('add_set', set_view.AddSet.as_view(), name='add-set'),
    path('preview/<uuid:pk>', set_view.SetPreviewList.as_view(), name='set-preview-list'),
    path('exam', exam_view.ExamInit.as_view(), name='exam'),
    path('exam_check', exam_view.ExamCheck.as_view(), name='exam-check'),
    path('exam_next', exam_view.ExamNext.as_view(), name='exam-next'),
    path('exam_summary', exam_view.ExamSummary.as_view(), name='exam-summary'),
    path('languages', category_view.Languages.as_view(), name='languages'),
    path('add_language', category_view.LanguageAdd.as_view(), name='add-language'),
    path('remove_language/<int:pk>', category_view.RemoveLanguage.as_view(), name='remove-language'),
    path('update_set/<uuid:pk>', set_view.UpdateSet.as_view(), name='update-set'),
    path('remove_category/<int:pk>', category_view.RemoveCategory.as_view(),
         name="remove-category"),
    path('remove_set/<uuid:pk>', set_view.RemoveSet.as_view(), name='remove-set'),
    path('sign_up', registration_view.SignUp.as_view(), name='sign-up')
]
