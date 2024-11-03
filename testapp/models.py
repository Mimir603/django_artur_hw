from datetime import datetime
from os.path import splitext

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

from django.contrib.postgres.fields import DateTimeRangeField, ArrayField, HStoreField, CICharField


class AdvUser(models.Model):
    is_activated = models.BooleanField(default=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Spare(models.Model):
    name = models.CharField(max_length=30)
    notes = GenericRelation('Note')

    def __str__(self):
        return self.name


class Machine(models.Model):
    name = models.CharField(max_length=30)
    spares = models.ManyToManyField(Spare, through='Kit',
                                   through_fields=('machine', 'spare'))
    notes = GenericRelation('Note')

    def __str__(self):
        return self.name


class Kit(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    spare = models.ForeignKey(Spare, on_delete=models.CASCADE)
    count = models.IntegerField()

    def __str__(self):
        return f'{self.machine} ({self.spare}): {self.count} шт.'


class Note(models.Model):
    content = models.TextField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey(
        ct_field='content_type',
        fk_field='object_id',
    )


# class PGSRoomReserving(models.Model):
#     name = models.CharField(max_length=20, verbose_name='Помещение')
#     reserving = DateTimeRangeField(verbose_name='Время резервирования')
#     canceled = models.BooleanField(default=False, verbose_name='Отменить резервирование')
#
#
# class PGSRubric(models.Model):
#     name = models.CharField(max_length=20, verbose_name='Имя')
#     description = models.TextField(verbose_name='Описание')
#     tags = ArrayField(base_field=models.CharField(max_length=20), verbose_name='Теги')
#
#
# class PGSProject2(models.Model):
#     name = models.CharField(max_length=20, verbose_name='Название')
#     platforms = HStoreField(verbose_name='Использованные платформы')
#
#
# class PGSProject3(models.Model):
#     name = CICharField(max_length=40, verbose_name='Название')
#     data = models.JSONField()


def get_timestamp_path(instance, filename):
    return '%s%s' % (datetime.now().timestamp(), splitext(filename)[1])


class Img(models.Model):
    img = models.ImageField(verbose_name="Изображение", upload_to='images/%Y/%m/%d/')
    desc = models.TextField(verbose_name='Описание')

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображение'

