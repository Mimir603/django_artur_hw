from datetime import datetime
from os.path import splitext

from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from django.http import HttpResponse
from precise_bbcode.fields import BBCodeTextField

from testapp.models import get_timestamp_path


def is_active_default():
    return True


def validate_even(val):
    if val % 2 != 0:
        raise ValidationError('Число %(value)s нечётное', code='odd',
                              params={'value': val})


class MinMaxValueValidator:
    def __init__(self, min_value, max_value):
        self.min_value = min_value
        self.max_value = max_value

    def __call__(self, val):
        if val < self.min_value or val > self.max_value:
            raise ValidationError('Введённое число должно находиться в диапазоне от '
                                  '%(min)s до %(max)s',
                                  code='out_of_range',
                                  params={'min': self.min_value, 'max': self.max_value})

    def get_timestamp_path(instance, filename):
        return '%s%s' % (datetime.now().timestamp(), splitext(filename)[1])


class Img(models.Model):
    img = models.ImageField(verbose_name="Изображение", upload_to='images/%Y/%m/%d/')
    desc = models.TextField(verbose_name='Описание')

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображение'


class RubricQuerySet(models.QuerySet):
    def order_by_bb_count(self):
        return super().annotate(
            cnt=models.Count('bb')
        ).order_by('-cnt')


class RubricManager(models.Manager):
    # def get_queryset(self):
    #     return super().get_queryset().annotate(
    #         cnt=models.Count('bb')
    #     ).order_by('order', 'name')

    # def order_by_bb_count(self):
    #     return super().get_queryset().annotate(
    #         cnt=models.Count('bb')
    #     ).order_by('-cnt')

    def get_queryset(self):
        return RubricQuerySet(self.model, using=self._db)

    def order_by_bb_count(self):
        return self.get_queryset().order_by_bb_count()


class Rubric(models.Model):
    name = models.CharField(max_length=20, db_index=True, unique=True,
                            verbose_name='Название')
    order = models.SmallIntegerField(default=0, db_index=True,
                                     verbose_name='Порядок')

    # objects = RubricManager()
    # objects = models.Manager()
    # objects = RubricQuerySet.as_manager()
    objects = models.Manager.from_queryset(RubricQuerySet)()
    bbs = RubricManager()

    def __str__(self):
        return self.name

    # def save(self, *args, **kwargs):
    #     if self.is_model_correct():
    #         super().save(*args, **kwargs)

    # def delete(self, *args, **kwargs):
    #     super().delete(*args, **kwargs)

    def get_absolute_url(self):
        return f"/{self.pk}/"

    class Meta:
        verbose_name = 'Рубрика'
        verbose_name_plural = 'Рубрики'
        # ordering = ['order', 'name']


class RevRubric(Rubric):
    class Meta:
        proxy = True
        ordering = ['-order', '-name']


class BbManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by('price')


class Bb(models.Model):
    # KINDS = (
    #     ('b', 'Куплю'),
    #     ('s', 'Продам'),
    #     ('c', 'Обменяю'),
    # )
    # KINDS = (
    #     ('Купля-продажа', (
    #         ('b', 'Куплю'),
    #         ('s', 'Продам'),
    #     )),
    #     ('Обмен', (
    #         ('c', 'Обменяю'),
    #     ))
    # )
    KINDS = (
        (None, 'Выберите тип публикуемого объявления'),
        ('b', 'Куплю'),
        ('s', 'Продам'),
        ('c', 'Обменяю'),
    )

    kind = models.CharField(max_length=1, choices=KINDS, default='s')

    rubric = models.ForeignKey('Rubric', null=True, on_delete=models.PROTECT,
                               verbose_name='Рубрика'
                               # , related_name='entries'
                               )
    title = models.CharField(max_length=50, verbose_name='Товар',
                             validators=[
                                 validators.RegexValidator(
                                     regex='^.{4,}$',
                                     message='Слишком мало букавак!',
                                     code='invalid',
                                 )
                             ],
                             error_messages={'invalid': 'Неправильное название товара!'}
                             )  # primary_key=True
    # content = models.TextField(null=True, blank=True, verbose_name='Описание')
    content = BBCodeTextField(null=True, blank=True, verbose_name='Описание')
    # price = models.FloatField(  # default=0,
    #                           null=True, blank=True, verbose_name='Цена')
    price = models.DecimalField(max_digits=15, decimal_places=2,
                                null=True, blank=True, verbose_name='Цена',
                                # validators=[validate_even,
                                            # MinMaxValueValidator(100, 1_000_000)
                                            # ]
                                )
    published = models.DateTimeField(auto_now_add=True, db_index=True,
                                     verbose_name='Опубликовано')
    # is_active = models.BooleanField(  # default=True
    #                                 default=is_active_default
    #                                 )

    img = models.ImageField(verbose_name='Изображение', blank=True, upload_to=get_timestamp_path)

    # file = models.FileField(verbose_name='Документы', blank=True, upload_to=get_timestamp_path)

    objects = models.Manager()
    by_price = BbManager()

    is_hidden = models.BooleanField(default=False, verbose_name='Скрыть')

    def title_and_price(self):
        if self.price:
            return f'{self.title} ({self.price:.2f})'
        else:
            return self.title

    title_and_price.short_description = 'Название и цена'

    def __str__(self):
        return f'{self.title} ({self.price} тг.)'

    def clean(self):
        errors = {}
        if not self.content:
            errors['content'] = ValidationError('Укажите описание продаваемого товара')

        if self.price and self.price < 0:
            errors['price'] = ValidationError('Укажите неотрицательное значение цены')

        if errors:
            raise ValidationError(errors)

    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'
        ordering = ['-published', 'title']
        get_latest_by = 'published'


class Kiosk(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название киоска")
    location = models.CharField(max_length=200, verbose_name="Расположение")

    def __str__(self):
        return self.name


class IceCream(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название мороженого")
    flavor = models.CharField(max_length=100, verbose_name="Вкус")
    price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Цена")
    kiosk = models.ForeignKey(Kiosk, on_delete=models.CASCADE, related_name="ice_creams", verbose_name="Киоск")

    def __str__(self):
        return f"{self.name} ({self.flavor})"


class Parent(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя родителя")
    age = models.IntegerField(verbose_name="Возраст")

    def __str__(self):
        return self.name


class Child(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя ребёнка")
    age = models.IntegerField(verbose_name="Возраст")
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name="children", verbose_name="Родитель")

    def __str__(self):
        return self.name



