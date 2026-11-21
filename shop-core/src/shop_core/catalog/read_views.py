"""Reusable catalog read views. Models are injected by the client project."""

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render


def core_category_products(request, slug, *, category_model, product_model):

    category = get_object_or_404(
        category_model,
        store=request.store,
        slug=slug,
        is_active=True
    )

    products = (
        product_model.objects
        .filter(
            store=request.store,
            category=category,
            is_active=True
        )
        .exclude(slug__isnull=True)
        .exclude(slug='')
    )

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(
        request.GET.get('page')
    )

    context = {
        'category': category,
        'page_obj': page_obj
    }

    return render(
        request,
        'products/category_products.html',
        context
    )


def core_brand_products(request, slug, *, brand_model, product_model):

    brand = get_object_or_404(
        brand_model,
        store=request.store,
        slug=slug,
        is_active=True
    )

    products = (
        product_model.objects
        .filter(
            store=request.store,
            brand=brand,
            is_active=True
        )
        .exclude(slug__isnull=True)
        .exclude(slug='')
    )

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(
        request.GET.get('page')
    )

    context = {
        'brand': brand,
        'page_obj': page_obj
    }

    return render(
        request,
        'products/brand_products.html',
        context
    )


def core_search_products(request, *, product_model):

    query = request.GET.get('q', '')

    products = (
        product_model.objects
        .filter(
            store=request.store,
            is_active=True
        )
        .exclude(slug__isnull=True)
        .exclude(slug='')
    )

    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(short_description__icontains=query)
            | Q(category__name__icontains=query)
            | Q(brand__name__icontains=query)
            | Q(tags__name__icontains=query)
        )

    paginator = Paginator(products, 12)

    page_obj = paginator.get_page(
        request.GET.get('page')
    )

    context = {
        'query': query,
        'page_obj': page_obj,
        'count': products.count()
    }

    return render(
        request,
        'products/search_results.html',
        context
    )


def core_best_sellers(request, *, product_model):

    products = (
        product_model.objects
        .filter(
            store=request.store,
            is_active=True,
            is_best_seller=True
        )
        .exclude(slug__isnull=True)
        .exclude(slug='')
        .order_by('-sales_count')
    )

    paginator = Paginator(products, 12)

    page_obj = paginator.get_page(
        request.GET.get('page')
    )

    context = {
        'page_obj': page_obj,
        'title': 'پرفروش‌ترین محصولات',
        'icon': 'fa-crown',
        'description': 'محصولاتی که بیشترین فروش را داشته‌اند',
        'bg_gradient': 'from-yellow-400 to-orange-500'
    }

    return render(
        request,
        'products/best_sellers.html',
        context
    )