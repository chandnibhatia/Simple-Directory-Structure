from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import DirectoryUser, FileUploadPath, AllocateMaxFileSize, FolderNameTable


class DirectoryUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta(UserCreationForm.Meta):
        model = DirectoryUser
        fields = ('username', 'first_name', 'last_name', 'email', 'is_staff')


class DirectoryUserChangeForm(UserChangeForm):
    class Meta:
        model = DirectoryUser
        fields = ('password','username', 'first_name', 'last_name', 'email', 'is_staff')


class UploadFileForm(forms.ModelForm):
    file_path = forms.FileField(widget=forms.FileInput(attrs={'multiple': True}))

    class Meta:
        model = FileUploadPath
        fields = ('file_path',)


class UpdateMaxSizeForm(forms.ModelForm):
    class Meta:
        model = AllocateMaxFileSize
        fields = ('user_name', 'max_file_size')

class AddFolderForm(forms.ModelForm):
    class Meta:
        model = FolderNameTable
        fields = ('parent','folder_name')

class DeleteFolderForm(forms.ModelForm):
    class Meta:
        model = FolderNameTable
        fields = ('parent' ,)
