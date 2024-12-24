import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError, PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count
from django.forms import modelformset_factory
from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect, HttpResponseNotFound, \
Http404, StreamingHttpResponse, FileResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.template import loader
from django.template.loader import get_template, render_to_string
from django.urls import reverse_lazy, reverse
from django.views.decorators.http import require_http_methods
from django.views.generic.dates import ArchiveIndexView, DateDetailView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.base import TemplateView, RedirectView
from django.views.generic.edit import CreateView, FormView, UpdateView, DeleteView
from django.forms.formsets import ORDERING_FIELD_NAME
from precise_bbcode.bbcode import get_parser
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from bboard import models
from bboard.forms import BbForm, RubricFormSet, SearchForm
from bboard.models import Bb, Rubric

from bboard.serializers import RubricSerializer
from testapp.bboard.models import BbManager


def index(request):
    bbs = Bb.objects.order_by('-published')
    # rubrics = Rubric.objects.annotate(cnt=Count('bb')).filter(cnt__gt=0)
    # rubrics = Rubric.objects.all()
    # rubrics = Rubric.objects.order_by_bb_count()
    rubrics = Rubric.objects.all().order_by_bb_count()
    # rubrics = Rubric.bbs.all()

    paginator = Paginator(bbs, 6)

    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1

    page = paginator.get_page(page_num)

    # context = {'bbs': bbs, 'rubrics': rubrics}
    context = {'rubrics': rubrics, 'bbs': page.object_list, 'page': page}

    return render(request, 'bboard/index.html', context)


class BbIndexView(ArchiveIndexView):
    model = Bb
    date_field = 'published'
    date_list_period = 'year'
    template_name = 'bboard/index.html'
    context_object_name = 'bbs'
    allow_empty = True
    # allow_future = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rubrics'] = Rubric.objects.annotate(cnt=Count('bb')).filter(cnt__gt=0)
        return context


def by_rubric(request, rubric_id):
    rubrics = Rubric.objects.annotate(cnt=Count('bb')).filter(cnt__gt=0)
    current_rubric = Rubric.objects.get(pk=rubric_id)
    bbs = get_list_or_404(Bb, rubric=rubric_id)

    context = {'bbs': bbs, 'rubrics': rubrics, 'current_rubric': current_rubric}

    return render(request, 'bboard/by_rubric.html', context)


class BbByRubricView(ListView):
    template_name = 'bboard/by_rubric.html'
    context_object_name = 'bbs'

    def get_queryset(self):
        # return Bb.objects.filter(rubric=self.kwargs['rubric_id'])
        rubric = Rubric.objects.get(pk=self.kwargs['rubric_id'])
        # return rubric.bb_set.all()
        return rubric.bb_set(manager='by_price').all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rubrics'] = Rubric.objects.annotate(cnt=Count('bb')).filter(cnt__gt=0)
        context['current_rubric'] = Rubric.objects.get(pk=self.kwargs['rubric_id'])
        return context


class BbCreateView(LoginRequiredMixin, CreateView):
    template_name = 'bboard/create.html'
    form_class = BbForm
    # success_url = reverse_lazy('bboard:index')
    success_url = '/{rubric_id}'
    success_message = 'Объявление о продаже товара "%(title)s" создано'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rubrics'] = Rubric.objects.annotate(cnt=Count('bb')).filter(cnt__gt=0)
        return context


class BbEditView(UpdateView):
    model = Bb
    form_class = BbForm
    success_url = '/{rubric_id}'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rubrics'] = Rubric.objects.annotate(cnt=Count('bb')).filter(cnt__gt=0)
        return context


def commit_handler():
    print('Транзакция закоммичена')


# @transaction.non_atomic_requests
# @transaction.atomic
def edit(request, pk):
    bb = Bb.objects.get(pk=pk)

    if request.method == 'POST':
        bbf = BbForm(request.POST, request.FILES, instance=bb)
        if bbf.is_valid():
            if bbf.has_changed():
                bbf.save()
                messages.add_message(request, messages.SUCCESS, 'Объявление исправлено!',
                                     extra_tags='alert alert-success')
                messages.success(request, 'Объявление исправлено - 2!',
                                 extra_tags='alert alert-success')
            return HttpResponseRedirect(
                reverse('bboard:by_rubric',
                        kwargs={'rubric_id': bbf.cleaned_data['rubric'].pk}))
        else:
            context = {'form': bbf}
            return render(request, 'bboard/bb_form.html', context)
    else:
        bbf = BbForm(instance=bb)
        context = {'form': bbf}
        return render(request, 'bboard/bb_form.html', context)


class BbAddView(FormView):
    template_name = 'bboard/create.html'
    form_class = BbForm
    initial = {'price': 0.0}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rubrics'] = Rubric.objects.annotate(cnt=Count('bb')).filter(cnt__gt=0)
        return context

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_form(self, form_class=None):
        self.object = super().get_form(form_class)
        return self.object

    def get_success_url(self):
        return reverse('bboard:by_rubric',
                       kwargs={'rubric_id': self.object.cleaned_data['rubric'].pk})


@require_http_methods(['GET', 'POST'])
def add_and_save(request):
    if request.method == 'POST':
        bbf = BbForm(request.POST)

        if bbf.is_valid():
            bbf.save()
            # return HttpResponseRedirect(reverse('bboard:by_rubric',
            #     kwargs={'rubric_id': bbf.cleaned_data['rubric'].pk}))
            return redirect('bboard:by_rubric',
                            rubric_id=bbf.cleaned_data['rubric'].pk)
        else:
            context = {'form': bbf}
            return render(request, 'bboard/create.html', context)
    else:
        bbf = BbForm()
        context = {'form': bbf}
        return render(request, 'bboard/create.html', context)


def detail(request, bb_id):
    bb = get_object_or_404(Bb, pk=bb_id)

    parser = get_parser()
    bb = Bb.objects.get(pk=bb_id)
    parsed_content = parser.render(bb.content)

    rubrics = Rubric.objects.annotate(cnt=Count('bb')).filter(cnt__gt=0)
    context = {'bb': bb, 'rubrics': rubrics, 'parsed_content': parsed_content}

    return render(request, 'bboard/detail.html', context)


class BbDetailView(DetailView):
    model = Bb

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rubrics'] = Rubric.objects.annotate(cnt=Count('bb')).filter(cnt__gt=0)
        return context


# class BbDetailView(DateDetailView):
#     model = Bb
#     date_field = 'published'
#     month_format = '%m'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['rubrics'] = Rubric.objects.annotate(cnt=Count('bb')).filter(cnt__gt=0)
#         return context


class BbRedirectView(RedirectView):
    url = '/detail/%(pk)d'


class BbDeleteView(DeleteView):
    model = Bb
    success_url = reverse_lazy('bboard:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rubrics'] = Rubric.objects.annotate(cnt=Count('bb')).filter(cnt__gt=0)
        return context


@login_required(login_url='login')
def rubrics(request):
    rubs = Rubric.objects.annotate(cnt=Count('bb')).filter(cnt__gt=0)

    if request.method == 'POST':
        formset = RubricFormSet(request.POST)

        if formset.is_valid():

            formset.save(commit=False)

            for form in formset:
                if form.cleaned_data:
                    rubric = form.save(commit=False)
                    rubric.order = form.cleaned_data[ORDERING_FIELD_NAME]
                    rubric.save()

            for rubric in formset.deleted_objects:
                rubric.delete()

            # formset.save()
            return redirect('bboard:rubrics')
    else:
        formset = RubricFormSet()

    context = {'formset': formset, 'rubrics': rubs}
    return render(request, 'bboard/rubrics.html', context)


def search(request):
    if request.method == 'POST':
        sf = SearchForm(request.POST)
        if sf.is_valid():
            keyword = sf.cleaned_data['keyword']
            rubric_id = sf.cleaned_data['rubric'].pk
            # bbs = Bb.objects.filter(title__icontains=keyword,
            #                         rubric=rubric_id)
            bbs = Bb.objects.filter(title__iregex=keyword,
                                    rubric=rubric_id)

            context = {'bbs': bbs, 'form': sf}
            return render(request, 'bboard/search.html', context)
    else:
        sf = SearchForm()

    context = {'form': sf}

    return render(request, 'bboard/search.html', context)


@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated))
def api_rubrics(request):
    if request.method == 'GET':
        rubric = Rubric.objects.all()
        serializer = RubricSerializer(rubric)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = RubricSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def api_rubrics(request):
    rubrics = Rubric.objects.all()
    serializer = RubricSerializer(rubrics, many=True)
    return Response(serializer.data)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def api_rubric_detail(request, pk):
    rubric = Rubric.objects.get(pk=pk)

    if request.method == 'GET':
        serializer = RubricSerializer(rubric)
        return Response(serializer.data)
    elif request.method == 'PUT' or request.method == 'PATCH':
        serializer = RubricSerializer(rubric, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        rubric.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# НИЗКОУРОВНЕВЫЙ
# class APIRubrics(APIView):
#     def get(self, request):
#         rubrics = Rubric.objects.all()
#         serializer = RubricSerializer(rubrics, many=True)
#         return Response(serializer.data)
#
#     def post(self, request):
#         serializer = RubricSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)


class APIRubrics(generics.ListCreateAPIView):
    queryset = Rubric.objects.all()
    serializer_class = RubricSerializer


class APIRubricDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Rubric.objects.all()
    serializer_class = RubricSerializer


class APIRubricList(generics.ListAPIView):
    queryset = Rubric.objects.all()
    serializer_class = RubricSerializer


class APIRubricViewSet(ModelViewSet):
    queryset = Rubric.objects.all()
    serializer_class = RubricSerializer
    permission_classes = (IsAuthenticated,)


class APIRubricReadSet(ReadOnlyModelViewSet):
    queryset = Rubric.objects.all()
    serializer_class = RubricSerializer

#===============================================================


# class APIBboards(generics.ListCreateAPIView):
#     queryset = Bb.objects.all()
#     serializer_class = BbSerializer
#
#
# class APIBboardDetail(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Bb.objects.all()
#     serializer_class = BbSerializer
#
#
# class APIBboardList(generics.ListAPIView):
#     queryset = Bb.objects.all()
#     serializer_class = BbSerializer
#
#
# class APIBboardViewSet(ModelViewSet):
#     queryset = Bb.objects.all()
#     serializer_class = BbSerializer


def bb_detail(request, pk):
    bb = get_object_or_404(Bb, pk=pk)
    id_and_title = bb.id_and_title()
    sum_price = bb.sum_of_values(100)
    return render(request, 'bb_detail.html', {
        'bb': bb,
        'id_and_title': id_and_title,
        'sum_price': sum_price,
    })


def positive_or_zero(value):
    if value < 0:
        raise ValidationError(f"Значение {value} должно быть неотрицательным.")


def bb_list(request):
    bbs = Bb.objects.all()
    return render(request, 'bb_list.html', {'bbs': bbs})


def bb_edit(request, pk):
    bb = get_object_or_404(Bb, pk=pk)
    if request.method == "POST":
        bb.title = request.POST.get('title', bb.title)
        bb.description = request.POST.get('description', bb.description)
        bb.price = request.POST.get('price', bb.price)
        bb.save()
        return bb


logger = logging.getLogger('django')


def generate_logs(request):
    logger.debug('This is a DEBUG message.')

    logger.info('This is an INFO message.')

    logger.warning('This is a WARNING message.')

    try:
        1 / 0
    except ZeroDivisionError as e:
        logger.error(f'ZeroDivisionError occurred: {e}')
    try:
        raise PermissionDenied('You do not have access to this resource.')
    except PermissionDenied as e:
        logger.error(f'PermissionDenied exception: {e}')
        raise

    return HttpResponse("Logs generated. Check the log files.")