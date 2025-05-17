from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Product, Sale, Category
# including  filters from the filters file
from .filters import Product_filter
from django.db.models import Sum, F

# including model forms created in the forms file
from .forms import AddForm, SaleForm

#Handling redirection after deletion
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse 


# Create your views here.

def home(request):
    products = Product.objects.all().order_by('-id')
    product_filter = Product_filter(request.GET, queryset=products)
    products = product_filter.qs
    return render(request,'products/index.html', {'products':products,'product_filter':product_filter})

@login_required
def index(request):
    return render(request, 'products/aboutDrkali.html')



# View for product_detail
# @login_required is a decorator, it comes before a function

@login_required
def product_detail(request, product_id):
    product = Product.objects.get(id = product_id)
    return render(request, 'products/products_detail.html', {'product': product})

@login_required
def issue_item(request, pk):
    issued_item = Product.objects.get(id = pk)
    sales_form = SaleForm(request.POST)

    if request.method == 'POST':
        #check if required input is as is supposed to be
        if sales_form.is_valid():
            new_sales = sales_form.save(commit = False)
            new_sales.item = issued_item
            new_sales.unit_price = issued_item.unit_price
            new_sales.save()
            #to keep track of remainding stock aftr sale
            issued_quantity = int(request.POST['quantity'])
            issued_item.total_quantity -= issued_quantity
            issued_item.save()
            print(issued_item.item_name)
            print(request.POST['quantity'])
            print(issued_item.total_quantity)

            return redirect('reciept')
    return render(request, 'products/issue_item.html', {'sales_form':sales_form})

@login_required
def all_sales(request):
    sales = Sale.objects.all()
    total = sum([items.amount_received for items in sales])
    change = sum([items.get_change() for items in sales])
    net = total - change
    return render(request, 'products/all_sales.html', {
        'sales':sales,
        'total':total,
        'net':net,
        'change':change,
    })


@login_required
def reciept(request):
    sales = Sale.objects.all().order_by('-id')
    return render(request, 'products/reciept.html', {'sales': sales})





@login_required
def add_to_stock(request, pk):
    issued_item = Product.objects.get(id = pk)
    form = AddForm(request.POST)

    if request.method == 'POST':
        if form.is_valid():
            added_quantity = int(request.POST['received_quantity'])
            issued_item.total_quantity += added_quantity
            issued_item.save()

            #To add to the remaining stock quantity is reducing
            print(added_quantity)
            print (issued_item.total_quantity)
            return redirect('index')

    return render (request, 'products/add_to_stock.html', {'form': form})

@login_required
def reciept_detail(request, reciept_id):
    reciept = Sale.objects.get(id=reciept_id)
    return render(request,'products/reciept_detail.html', {'reciept':reciept})


@login_required
def delete_item(request, product_id):
    delete = Product.objects.get(id=product_id)
    delete.delete()
    return HttpResponseRedirect(reverse('index'))


# Dashboard view
@login_required
def dashboard(request):
    # 1. Key aggregates
    total_categories = Category.objects.count()
    total_products   = Product.objects.count()
    total_stock      = Product.objects.aggregate(
        remaining=Sum('total_quantity')
    )['remaining'] or 0
    total_sales_amt  = Sale.objects.aggregate(
        amt=Sum(F('quantity') * F('unit_price'))
    )['amt'] or 0

    # 2. Top 5 best sellers
    top_products = (
        Sale.objects
        .values('item__item_name')
        .annotate(total_sold=Sum('quantity'))
        .order_by('-total_sold')[:5]
    )

    # 3. Sales by category
    sales_by_cat = (
        Sale.objects
        .values('item__category_name__name')
        .annotate(total=Sum(F('quantity') * F('unit_price')))
        .order_by('item__category_name__name')
    )

    context = {
        'total_categories': total_categories,
        'total_products': total_products,
        'total_stock': total_stock,
        'total_sales_amt': total_sales_amt,
        'top_products': top_products,
        'sales_by_cat': sales_by_cat,
    }
    return render(request, 'products/dashboard.html', context)

