from django.contrib import admin
from django.db.models import F

from bboard.models import Bb, Rubric


# def title_and_price(rec):
#     return f'{rec.title} ({rec.price})'


class PriceListFilter(admin.SimpleListFilter):
    title = 'Диапазон цен'
    parameter_name = 'price'

    # Функция фильтра цен
    # def lookups(self, request, model_admin):
    #     return (
    #         ('low', 'Низкаая цена'),
    #         ('mid', 'Средняя цена'),
    #         ('high', 'Высокая цена'),
    #     )
    #
    # def queryset(self, request, queryset):
    #     if self.value() == 'low':
    #         return queryset.filter(price__lt=500)
    #     elif self.value() == 'mid':
    #         return queryset.filter(price__gte=500, price__lte=5000)
    #     elif self.value() == 'high':
    #         return queryset.filter(price__gt=5000)


class BbAdmin(admin.ModelAdmin):
    list_display = ('title_and_price', 'content', 'price', 'published', 'rubric')
    # list_display_links = ('title', 'content')
    # search_fields = ('title', 'content')

    @admin.action(description='Скидка 25%')
    def discount(self, request, queryset):
        f = F('price')
        for rec in queryset:
            rec.price = f / 4
            rec.save()
        self.message_user(request, 'Выполнено')

    actions = (discount,)

    @admin.display(description='Название и цена', ordering='-title')
    def title_and_price(self, rec):
        return f'{rec.title} ({rec.price})'

    def get_list_display(self, request):
        ld = ['title', 'content', 'price']
        if request.user.is_superuser:
            ld += ['published', 'rubric']
        return ld

    list_display_links = ('title', 'content')

    # def get_list_display_links(self, request, list_display):
    #     return list_display

    list_editable = ('price',)

    # Фильтр цен
    # def get_queryset(self, request):
    #     qs = super().get_queryset(request)
    #     if request.user.is_superuser:
    #         return qs
    #     else:
    #         return qs.filter(is_hidden=False)
    #
    # search_fields = ('title', '^price', 'content')
    # list_filter = (PriceListFilter, 'title', 'rubric__name')
    list_filter = ('title', 'rubric__name')

    #Наборы полей внутри записи
    # fields = ('title', 'content', 'price')
    # exclude = ('rubric', 'kind')
    fields = (('title', 'price'), 'content')
    readonly_fields = ('published',)

    @admin.action(description='Скидка 25%')
    def discount(modeladmin, request, queryset):
        f = F('price')
        for rec in queryset:
            rec.price = f / 4
            rec.save()
        modeladmin.message_user(request, 'Выполнено')


class RubricAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'order')


admin.site.register(Bb, BbAdmin)
admin.site.register(Rubric, RubricAdmin)
