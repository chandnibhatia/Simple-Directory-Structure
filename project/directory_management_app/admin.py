from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from mptt.admin import MPTTModelAdmin

from .forms import DirectoryUserCreationForm, DirectoryUserChangeForm
from .models import DirectoryUser, FileUploadPath, AllocateMaxFileSize, FolderNameTable


# Register your models here.


class DirectoryUserAdmin(UserAdmin):
    model = DirectoryUser
    add_form = DirectoryUserCreationForm
    form = DirectoryUserChangeForm


class FileUploadPathAdmin(admin.ModelAdmin):
    list_display = ('user_name','folder_name' ,'file_path', 'created_time', 'file_size')


class AllocateMaxFileSizeAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'max_file_size')

class FolderNameTableAdmin(MPTTModelAdmin):
	list_display = ('user_name', 'folder_name', 'parent')

admin.site.register(DirectoryUser, DirectoryUserAdmin)
admin.site.register(FileUploadPath, FileUploadPathAdmin)
admin.site.register(AllocateMaxFileSize, AllocateMaxFileSizeAdmin)
admin.site.register(FolderNameTable, FolderNameTableAdmin)