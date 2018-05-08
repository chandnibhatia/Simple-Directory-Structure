from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
import shutil, os
from django.http import HttpResponse

# Create your models here.

def upload_to(instance, filename):
    return os.path.join('%s' % instance.user_name, filename)


class DirectoryUserManager(UserManager):
    pass


class DirectoryUser(AbstractUser):
    objects = DirectoryUserManager()


class FileUploadPath(models.Model):
    user_name = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    folder_name = models.ForeignKey('FolderNameTable', on_delete=models.CASCADE ,null=True, blank=True)
    file_path = models.FileField(upload_to=upload_to)
    created_time = models.DateTimeField(auto_now_add=True)
    file_size = models.IntegerField()

    def rename(self, new_name):
        old_path = self.file_path.path
        self.file_path.name = new_name
        shutil.move(old_path, self.file_path.path)
        self.save()



class AllocateMaxFileSize(models.Model):
    user_name = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    max_file_size = models.DecimalField(decimal_places=2, max_digits=12,
                                        help_text="Size should be in byte.")


class FolderNameTable(MPTTModel):
    user_name = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    folder_name = models.CharField(max_length=30)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)

    def __str__(self):
        return self.folder_name
