import django_filters
from django.db.models import Q
from .models import Product

class Product_filter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_by_all', label='Search')

    class Meta:
        model = Product
        fields = []

    def filter_by_all(self, queryset, name, value):
        return queryset.filter(
            Q(item_name__icontains=value) |
            Q(category_name__name__icontains=value)
        ).distinct()
