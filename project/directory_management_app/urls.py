from django.urls import path
from django.contrib.auth import views as django_view
from . import views

app_name = 'directory_management_app'
urlpatterns = [
    path('login/', django_view.login, name='login', kwargs={'template_name': 'directory_management_app/login.html'}),
    path('logout/', django_view.logout, name='logout', kwargs={'next_page': '/'}),
    path('', views.get_path, name='get_path'),
    path('add_file/<str:user>/<int:id>/', views.add_file, name='add_file'),
    path('file/<int:pk>/remove/', views.delete_file, name='delete_file'),
    path('edit_file_name/<path:path>/', views.edit_file_name, name='edit_file_name'),
    path('rename_file/', views.rename_file, name='rename_file'),
    path('file/<path:path>/downloded/', views.download, name='download'),
    path('add_folder/',views.add_folder, name='add_folder'),
    path('delete_folder/',views.delete_folder,name='delete_folder'),
    path('user/<int:pk>/remove/', views.delete_user, name='delete_user'),
    path('admin_page/', views.admin_page, name='admin_page'),
    path('edit_user/<str:pk>/', views.edit_user, name='edit_user'),
    path('add_user_details/', views.add_user_details, name='add_user_details'),
    path('file_size_allocation/<str:username>/', views.file_size_allocation, name='file_size_allocation'),
    path('change_size/', views.change_size, name='change_size'),
    
]
