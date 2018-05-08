import mimetypes
import os

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.utils.encoding import smart_str
from django.utils.crypto import get_random_string
from .forms import UploadFileForm, DirectoryUserCreationForm, UpdateMaxSizeForm, AddFolderForm, DirectoryUserChangeForm, DeleteFolderForm
from .models import FileUploadPath, DirectoryUser, AllocateMaxFileSize, FolderNameTable
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# Create your views here.
def download(request, path):
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type=mimetypes.guess_type(file_path)[0])
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            response['X-Sendfile'] = smart_str(file_path)
            return response
    raise Http404

def delete_folder(request):
    pk = request.POST.get('parent')
    folder_details = get_object_or_404(FolderNameTable, pk=pk)
    folder_details.delete()
    return redirect("/")

def add_folder(request):
    if request.POST:
        user = DirectoryUser.objects.get(username=request.user)
        form = AddFolderForm(request.POST)
        base_path = os.path.join(settings.MEDIA_ROOT, str(user))
        parent = ""
        directory = ""
        ancestors = ""
        ancestors_path = ""
        current_parent_folder = ""
        if request.POST.get('parent'):
            parent = FolderNameTable.objects.filter(pk=form['parent'].value())
            current_parent_folder = parent.values_list('folder_name', flat=True).get(pk=form['parent'].value())
            if parent.get_ancestors():
                ancestors = parent.get_ancestors()
                for folder in ancestors:
                    ancestors_path = os.path.join(ancestors_path, str(folder))
        folder_name = form['folder_name'].value()
        if form.is_valid():

            try:
                if not os.path.exists(settings.MEDIA_ROOT):
                    os.makedirs(settings.MEDIA_ROOT)
                if not os.path.exists(base_path):
                    os.makedirs(base_path)
                if current_parent_folder:
                    directory = os.path.join(base_path ,ancestors_path , str(current_parent_folder),folder_name)
                else:
                    directory = os.path.join(base_path,folder_name)
                if directory and not os.path.exists(directory):

                    os.makedirs(directory)
                    try:
                        instance = form.save(commit=False)
                        instance.user_name = user
                        instance.save()
                        return redirect("/")
                    except Exception as exe:
                        return HttpResponse("Unable to store folder in database")
                else:
                    return HttpResponse("Path does not exists")
            except Exception as exe:
                return HttpResponse("Unable to create folder")
    else:
        folder_form = AddFolderForm()
        form = UploadFileForm()
        delete_folder = DeleteFolderForm()
        return render(request, 'directory_management_app/get_file_path.html',
                      {'form': form, 'folder_form': folder_form,'delete_folder': delete_folder})


def edit_file_name(request, path):
    if request.method == "GET":
        return render(request, 'directory_management_app/edit_file_name.html', {'path': path})


def rename_file(request):
    if request.method == "POST":
        #base_path = os.path.join(settings.MEDIA_ROOT, str(request.user))
        old_filename = request.POST.get("old_filename")
        new_filename = request.POST.get("new_filename")
        file_details = FileUploadPath.objects.all()
        try:
            for file in file_details:

                if file.file_path.name == old_filename:
                    filename, extension = os.path.splitext(file.file_path.name)
                    try:
                        file.rename(os.path.join(str(request.user) , new_filename.replace(' ','_') + extension))
                        return redirect("/")
                    except Exception as exe:
                        raise
                else:
                    return redirect("/")
        except Exception:
            raise


def delete_file(request, pk):
    file_details = get_object_or_404(FileUploadPath, pk=pk)
    file_details.delete()
    return redirect("/")


def add_file(request, user, id):
    if request.POST:
        size_allocate = None
        calculate_size = None
        total_remaining = None
        ancestors_path = ""
        directory = ""
        current_parent_folder = ""

        base_path = os.path.join(settings.MEDIA_ROOT, str(request.user))
        form = UploadFileForm(request.POST, request.FILES)
        files = request.FILES.getlist('file_path')
        folder = request.POST.get('folder')


        if folder and folder != "none":
            folder = FolderNameTable.objects.get(folder_name=folder)
            parent = FolderNameTable.objects.filter(folder_name=folder)
            current_parent_folder = parent.values_list('folder_name', flat=True).get(folder_name=folder)
            if parent.get_ancestors():
                ancestors = parent.get_ancestors()
                for folders in ancestors:
                    ancestors_path = os.path.join(ancestors_path, str(folders))


        if current_parent_folder:
            directory = os.path.join(base_path ,ancestors_path , str(current_parent_folder))
        else:
            directory = base_path


        if form.is_valid():

            user = DirectoryUser.objects.get(username=user)

            used_file_size = FileUploadPath.objects.values('file_size').annotate(Sum('file_size')).filter(user_name=id)
            for file in used_file_size:
                calculate_size = float(file['file_size__sum'])

            size_allocated = AllocateMaxFileSize.objects.values('max_file_size').filter(user_name=id)
            for size in size_allocated:
                size_allocate = float(size['max_file_size'])

            if size_allocate and calculate_size:
                total_remaining = size_allocate - calculate_size
            for filename in files:

                instance = FileUploadPath()
                instance.user_name = user
                instance.uploaded_at = timezone.now()
                if folder and folder != "none":
                    instance.folder_name = folder
                file_name = filename.name
                if os.path.exists(os.path.join(directory, file_name)):
                    unique_id = get_random_string(length=5)
                    file, extension = os.path.splitext(file_name)  # str(filename.name).rpartition('.')
                    new_file_name = file + unique_id + '.' + extension
                    filename.name = new_file_name
                    instance.file_path = filename
                    instance.file_path.name = os.path.join(ancestors_path , str(current_parent_folder), new_file_name)
                    return HttpResponse(os.path.join(ancestors_path , str(current_parent_folder), new_file_name))
                else:
                    dir = os.path.join(ancestors_path , str(current_parent_folder), file_name)
                    filename.name = file_name
                    instance.file_path = filename
                    instance.file_path.name = dir

                if size_allocate and total_remaining:
                    if filename.size < size_allocate and filename.size < total_remaining:
                        instance.file_size = filename.size
                    else:
                        return HttpResponse('<h1>File Size is greater than %s</h1>', [size_allocated])
                else:
                    instance.file_size = filename.size
                instance.save()
            return redirect("/")
    else:
        folder_form = AddFolderForm()
        folder_list = FolderNameTable.objects.all()
        form = UploadFileForm()
        delete_folder = DeleteFolderForm()
        return render(request, 'directory_management_app/get_file_path.html',
                      {'form': form, 'folder_form': folder_form,'folders_list': folder_list,'delete_folder': delete_folder})


@login_required(login_url="login/")
def get_path(request):
    if request.user.is_superuser:
        return redirect("/admin_page/")
    else:
        size_allocate = None
        calculate_size = None

        used_file_size = FileUploadPath.objects.values('file_size').annotate(Sum('file_size')).filter(
            user_name=request.user.pk)
        for file in used_file_size:
            calculate_size = float(file['file_size__sum'])

        size_allocated = AllocateMaxFileSize.objects.values('max_file_size').filter(user_name=request.user.pk)
        for size in size_allocated:
            size_allocate = float(size['max_file_size'])

        if size_allocate and calculate_size:
            total_remaining = size_allocate - calculate_size
        else:
            total_remaining = 0.0

        file_details = FileUploadPath.objects.order_by("-created_time")
        folder_name = FolderNameTable.objects.all()
        form = UploadFileForm()
        folder_form = AddFolderForm()
        delete_folder = DeleteFolderForm()
        page = request.GET.get('page', 1)
        paginator = Paginator(file_details, 5)
        try:
            files = paginator.page(page)
        except PageNotAnInteger:
            files = paginator.page(1)
        except EmptyPage:
            files = paginator.page(paginator.num_pages)

        return render(request, 'directory_management_app/get_file_path.html',
                      {'uploaded_file': files, 'form': form, 'Total_remaining_space': total_remaining,
                       'folder_form': folder_form,'folders_list':folder_name,'delete_folder': delete_folder})


def admin_page(request):
    user_details = DirectoryUser.objects.all()
    file_size_details = AllocateMaxFileSize.objects.all()
    used_file_size = FileUploadPath.objects.values('user_name').annotate(Sum('file_size'))
    return render(request, 'directory_management_app/admin_page.html',
                  {'user_details': user_details, 'file_size_details': file_size_details,
                   'used_file_size': used_file_size})


def delete_user(request, pk):
    user_details = get_object_or_404(DirectoryUser, pk=pk)
    user_details.delete()
    return redirect("/admin_page/")


def add_user_details(request):
    if request.method == 'POST':
        form = DirectoryUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            return redirect("/admin_page/")
    else:
        form = DirectoryUserCreationForm()
    return render(request, 'directory_management_app/add_user.html', {'form': form})


def edit_user(request, pk):
    user_detail = get_object_or_404(DirectoryUser, pk=pk)
    if request.method == "POST":
        form = DirectoryUserChangeForm(request.POST, instance=user_detail)
        if form.is_valid():
            user_detail = form.save(commit=False)
            user_detail.save()
            return redirect("/admin_page/")
    else:
        form = DirectoryUserChangeForm(instance=user_detail)
    return render(request, 'directory_management_app/add_user.html', {'form': form})


def file_size_allocation(request, username):
    user = DirectoryUser.objects.get(username=username)
    add_size = AllocateMaxFileSize(user_name=user, max_file_size=float(2147483648))
    add_size.save()
    return redirect("/admin_page/")


def change_size(request):
    user_detail = get_object_or_404(AllocateMaxFileSize, pk=request.user.pk)
    if request.method == "POST":
        form = UpdateMaxSizeForm(request.POST, instance=user_detail)
        if form.is_valid():
            user_detail = form.save(commit=False)
            user_detail.save()
            return redirect("/admin_page/")
    else:
        form = UpdateMaxSizeForm(instance=user_detail)
    return render(request, 'directory_management_app/change_size.html', {'form': form})


'''class FileFieldView(FormView):
	form_class = UploadFileForm
	template_name = 'directory_management_app/getFilePath.html'  # Replace with your template.
	success_url = 'get_path'

	def post(self, request, *args, **kwargs):
		form_class = self.get_form_class()
		form = self.get_form(form_class)
		files = request.FILES.getlist('file_path')
		size_allocate = None
		calculate_size = None
		Total_remaining = None

		if form.is_valid():

			user = DirectoryUser.objects.get(username=str(request.user))

			used_file_size = FileUploadPath.objects.values('file_size').annotate(Sum('file_size')).filter(user_name=request.user.pk)
			for file in used_file_size:
				calculate_size=float(file['file_size__sum'])


			size_allocated = AllocateMaxFileSize.objects.values('max_file_size').filter(user_name=request.user.pk)
			for size in size_allocated:
				size_allocate=float(size['max_file_size'])


			if size_allocate and calculate_size:
				Total_remaining = size_allocate - calculate_size

			#return HttpResponse(files)
			for filename in files:
				#return HttpResponse(filename)
				instance = form.save(commit=False)
				instance.user_name = user
				instance.uploaded_at = timezone.now()
				if size_allocate and Total_remaining:
					if filename.size < size_allocate and filename.size < Total_remaining:
						instance.file_size = filename.size
					else:
						return HttpResponse('<h1>File Size is greater than %s</h1>',[size_allocated])
				else:
					instance.file_size = filename.size
				form.save()
				return self.form_valid(form)
		else:
			return self.form_invalid(form)'''
