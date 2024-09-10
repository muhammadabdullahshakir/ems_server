from django.urls import path
from .views import create_user , create_project , login_user , get_user_data , total_uers ,get_latest_project_data,latest_project_data , add_hardware , hardware_count , connected_hardware_count
from .views import user_project ,fetching_users , delete_user ,update_user
urlpatterns = [
    path('create-user/', create_user, name='create_user'),
    path('create_project/',create_project , name='create_project'),
    path('get_latest_project_data/',get_latest_project_data, name='get_latest_project_data'),
    path('login_user/', login_user , name='login_user'),
    path('user_data/', get_user_data , name='get_user_data'),
    path('user_count/', total_uers , name='total_uers'),
    path('connected_hardware_count/<int:project_id>/', connected_hardware_count , name='connected_hardware_count'),
    path('add_hardware/', add_hardware , name='add_hardware'),
    path('hardware_count/<int:project_id>/',hardware_count, name='hardware_count'),
    path('latest_project_data/', latest_project_data, name='latest_project_data'),
    path('user_project/', user_project , name='user_project'),
    path('fetch_users/', fetching_users , name='fetching_users'),
    path('delete_user/<int:user_id>/',delete_user, name='delete_user'),
    path('update_user/<int:user_id>/', update_user , name='update_user')

]