from django.urls import path
from . import views
#from .views import DishHistoryDetail

urlpatterns = [
  path('', views.index, name='index'),
  path('dish_history_input_form/', views.dish_history_input_form, name='reciperecommend/dish_history_input_form'),
  path('dish_classify_result/', views.dish_classify_result, name='dish_classify_result'),
  path('dish_history/', views.dish_history, name='dish_history'),
  #path('dish_history_detail/<int:pk>', DishHistoryDetail.as_view(), name='dish_history_detail'),
  path('dish_history_detail/<int:id>', views.dish_history_detail, name='dish_history_detail'),
  path('dish_history_edit/<int:id>', views.dish_history_edit, name='dish_history_edit'),
  path('dish_history_update/<int:id>', views.dish_history_update, name='dish_history_update'),
  path('dish_history_delete/<int:id>', views.dish_history_delete, name='dish_history_delete'),
  path('dish_master_list/', views.DishMasterList.as_view(), name='dish_master_list'),
  path('dish_master_detail/<int:id>', views.dish_master_detail, name='dish_master_detail'),
  path('recommend_by_dri/', views.recommend_by_dri, name='recommend_by_dri'),
  path('login/', views.Login.as_view(), name='login'), 
  path('logout/', views.Logout.as_view(), name='logout'),
  path('signup/', views.signup, name='signup'), 
]