import django_filters
from .models import Category,Product

 # Creating a class to filter objects from our models


class Product_filter(django_filters.FilterSet):
    # class meta is used to alter(manipulate)the content of other classes
    name = django_filters.CharFilter(field_name='item_name', lookup_expr='icontains')  # case-insensitive contains
    class Meta:
        model = Product
        fields = ['name']

# class Category_filter(django_filters.FilterSet):
#     class Meta:
#         model = Category
#         fields = ['name']