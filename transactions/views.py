from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Q
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
import csv
from .forms import ExpenseForm

from .models import (
    Transaction, Customer, Payment,
    Expense, ExpenseName,ExpenseName
)
from .forms import (
    TransactionForm, CustomerForm,
    PaymentForm, ExpenseForm
)

# ---------------- Transactions ----------------

def transaction_list(request):
    from datetime import datetime
    q = request.GET.get('q', '').strip()
    location = request.GET.get('location') or ''
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    qs = Transaction.objects.all().order_by('-created_at')

    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            qs = qs.filter(date__gte=start)
        except:
            pass
    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            qs = qs.filter(date__lte=end)
        except:
            pass
    if not start_date and not end_date:
        qs = qs.filter(date=timezone.localdate())

    if location:
        qs = qs.filter(location_id=location)

    if q:
        qs = qs.filter(Q(notes__icontains=q))

    totals_raw = qs.aggregate(
        paid=Sum('paid'),
        customer_balance=Sum('customer_balance'),
        wholesale=Sum('wholesale'),
        debt=Sum('debt'),
        cash=Sum('cash'),
        accounts=Sum('accounts'),
        expenses=Sum('expenses'),
        opening_balance=Sum('opening_balance'),
    )
    for k, v in totals_raw.items():
        totals_raw[k] = v or 0

    totals = {
        "sales": totals_raw['paid'] + totals_raw['customer_balance'] + totals_raw['wholesale'],
        "cashout": totals_raw['debt'] + totals_raw['cash'] + totals_raw['accounts'] + totals_raw['expenses'],
    }
    totals["difference"] = totals["sales"] - totals["cashout"]
    totals["less_excess"] = totals["difference"] - totals_raw['opening_balance']

    try:
        from core.models import Location
        locations = Location.objects.all()
    except:
        locations = []

    return render(request, 'transactions/transaction_list.html', {
        'rows': qs,
        'totals': totals,
        'locations': locations,
        'selected_location': location,
        'start_date': start_date,
        'end_date': end_date,
    })


def transaction_add(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            t = form.save(commit=False)
            t.user = None
            t.save()
            return redirect('transactions:list')
    else:
        form = TransactionForm()
    return render(request, 'transactions/transaction_form.html', {'form': form, 'create': True})


def transaction_edit(request, pk):
    obj = get_object_or_404(Transaction, pk=pk)
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('transactions:list')
    else:
        form = TransactionForm(instance=obj)
    return render(request, 'transactions/transaction_form.html', {'form': form, 'create': False, 'obj': obj})


def transaction_delete(request, pk):
    obj = get_object_or_404(Transaction, pk=pk)
    if request.method == 'POST':
        obj.delete()
        return redirect('transactions:list')
    return render(request, 'transactions/transaction_confirm_delete.html', {'obj': obj})


def transaction_detail(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    return render(request, 'transactions/transaction_detail.html', {'transaction': transaction})


# ---------------- Customers ----------------

def customer_add(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('transactions:customers')
    else:
        form = CustomerForm()
    return render(request, 'transactions/customer_form.html', {'form': form})


def customer_edit(request, pk):
    obj = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('transactions:customers')
    else:
        form = CustomerForm(instance=obj)
    return render(request, 'transactions/customer_form.html', {'form': form, 'obj': obj})


def customer_delete(request, pk):
    obj = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        obj.delete()
        return redirect('transactions:customers')
    return render(request, 'transactions/customer_confirm_delete.html', {'obj': obj})

from django.db.models import Sum, Max
from datetime import datetime
from django.shortcuts import render
from .models import Customer, Transaction, Payment

def customers_list(request):
    customers = Customer.objects.all()

    # --- Filters ---
    name = request.GET.get('name')
    phone = request.GET.get('phone')
    tin = request.GET.get('tin')
    supply = request.GET.get('supply')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if name:
        customers = customers.filter(name__icontains=name)
    if phone:
        customers = customers.filter(phone__icontains=phone)
    if tin:
        customers = customers.filter(tin__icontains=tin)
    if supply:
        customers = customers.filter(supply__icontains=supply)

    # Annotate with latest payment date
    customers = customers.annotate(last_payment_date=Max('payments__date'))
    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            customers = customers.filter(last_payment_date__gte=start)
        except:
            pass
    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d")
            customers = customers.filter(last_payment_date__lte=end)
        except:
            pass

    # --- Totals after filtering ---
    total_supply = customers.aggregate(total_supply=Sum('supply'))['total_supply'] or 0
    total_payment = customers.aggregate(total_payment=Sum('payments__amount'))['total_payment'] or 0
    total_balance = sum(c.balance for c in customers)

    context = {
        'customers': customers,
        'total_supply': total_supply,
        'total_payment': total_payment,
        'total_balance': total_balance,
        'request': request,
    }
    return render(request, 'transactions/customers_list.html', context)



def customer_info(request, pk):
    try:
        c = Customer.objects.get(pk=pk)
        return JsonResponse({'ok': True, 'balance': str(c.balance), 'supply': str(c.supply), 'name': c.name})
    except Customer.DoesNotExist:
        return JsonResponse({'ok': False}, status=404)


from django.shortcuts import render, get_object_or_404
from .models import Customer, Transaction
from django.db.models import Max

from django.shortcuts import render, get_object_or_404
from .models import Customer, Transaction
from django.db.models import Sum

def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    # Transactions for this customer
    transactions = Transaction.objects.filter(customer=customer).order_by('-date')

    # Supply history
    supply_history = customer.supply_history.all().order_by('-date')

    # Last payment object
    last_payment = customer.last_payment  # Using property from Customer model

    # Totals
    total_paid = customer.total_payment  # Using property from Customer model
    total_supply = customer.total_supply  # Using property from Customer model

    context = {
        'customer': customer,
        'transactions': transactions,
        'supply_history': supply_history,
        'last_payment': last_payment,
        'total_paid': total_paid,
        'total_supply': total_supply,
    }
    return render(request, 'transactions/customer_detail.html', context)



# ---------------- Payments ----------------

def payment_add(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('transactions:customers')
    else:
        form = PaymentForm()
    return render(request, 'transactions/payment_form.html', {'form': form})


# ---------------- Expenses ----------------

from django.shortcuts import render, redirect
from django.db.models import Sum
from .forms import ExpenseForm
from .models import Expense, ExpenseName

def expense_add(request):
    last_name = request.session.get('last_expense_name', '')

    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save()
            request.session['last_expense_name'] = expense.name
            return redirect('transactions:expenses_list')
    else:
        initial_data = {}
        if last_name:
            initial_data['name'] = last_name
        form = ExpenseForm(initial=initial_data)

    return render(request, 'transactions/expense_form.html', {'form': form})

def expenses_list(request):
    qs = Expense.objects.all().order_by('-date')
    name_filter = request.GET.get('name', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    if name_filter:
        qs = qs.filter(name__icontains=name_filter)
    if start_date and end_date:
        qs = qs.filter(date__range=[start_date, end_date])

    total = qs.aggregate(total_amount=Sum('amount'))['total_amount'] or 0

    return render(request, 'transactions/expenses_list.html', {
        'expenses': qs,
        'expense_names': ExpenseName.objects.all(),
        'total': total,
        'name_filter': name_filter,
        'start_date': start_date,
        'end_date': end_date,
    })

from django.shortcuts import render, redirect, get_object_or_404
from .forms import ExpenseForm
from .models import Expense, ExpenseName

# --- Add Expense (already present) ---
# expense_add view from previous message

# --- Edit Expense ---
def expense_edit(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('transactions:expenses_list')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'transactions/expense_form.html', {'form': form, 'edit': True, 'expense': expense})

# --- Delete Expense ---
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        expense.delete()
        return redirect('transactions:expenses_list')
    return render(request, 'transactions/expense_confirm_delete.html', {'expense': expense})


# ---------------- Reports ----------------

def daily_report(request):
    query = request.GET.get('q', '')
    if query:
        transactions = Transaction.objects.filter(accounts__icontains=query).order_by('-id')
    else:
        transactions = Transaction.objects.all().order_by('-id')

    paginator = Paginator(transactions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'transactions/report_daily.html', {
        'transactions': page_obj,
        'query': query,
    })


def daily_export(request):
    date = request.GET.get('date') or timezone.localdate().isoformat()
    qs = Transaction.objects.filter(date=date)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="report_{date}.csv"'
    writer = csv.writer(response)
    writer.writerow(['id', 'date', 'location', 'total_sales', 'total_cashout', 'difference', 'less_excess'])
    for t in qs:
        writer.writerow([t.id, t.date, t.location.name if t.location else '',
                         t.total_sales, t.total_cashout, t.difference, t.less_excess])
    return response


def report_home(request):
    return render(request, 'transactions/report_home.html')


def customer_report(request):
    customers = Customer.objects.all()
    payments = Payment.objects.all()
    start = request.GET.get('start')
    end = request.GET.get('end')
    if start and end:
        payments = payments.filter(date__range=[parse_date(start), parse_date(end)])
    totals = payments.aggregate(total_paid=Sum('amount'))
    return render(request, 'transactions/customer_report.html', {
        'customers': customers,
        'payments': payments,
        'totals': totals
    })


def expense_report(request):
    expenses = Expense.objects.all()
    start = request.GET.get('start')
    end = request.GET.get('end')
    if start and end:
        expenses = expenses.filter(date__range=[parse_date(start), parse_date(end)])
    total = expenses.aggregate(total_expenses=Sum('amount'))
    return render(request, 'transactions/expense_report.html', {
        'expenses': expenses,
        'total': total
    })


def transaction_report(request):
    transactions = Transaction.objects.all()
    start = request.GET.get('start')
    end = request.GET.get('end')
    if start and end:
        transactions = transactions.filter(date__range=[parse_date(start), parse_date(end)])

    location = request.GET.get('location')
    try:
        from core.models import Location
        locations = Location.objects.all()
    except:
        locations = []
    if location:
        transactions = transactions.filter(location_id=location)

    totals = {
        'opening_balance': transactions.aggregate(Sum('opening_balance'))['opening_balance__sum'] or 0,
        'customer_balance': transactions.aggregate(Sum('customer_balance'))['customer_balance__sum'] or 0,
        'paid': transactions.aggregate(Sum('paid'))['paid__sum'] or 0,
        'wholesale': transactions.aggregate(Sum('wholesale'))['wholesale__sum'] or 0,
        'debt': transactions.aggregate(Sum('debt'))['debt__sum'] or 0,
        'accounts': transactions.aggregate(Sum('accounts'))['accounts__sum'] or 0,
        'expenses': transactions.aggregate(Sum('expenses'))['expenses__sum'] or 0,
        'cash': transactions.aggregate(Sum('cash'))['cash__sum'] or 0,
        'difference': sum([t.difference for t in transactions]),
        'less_excess': sum([t.less_excess for t in transactions]),
    }

    return render(request, 'transactions/transaction_report.html', {
        'transactions': transactions,
        'totals': totals,
        'locations': locations,
        'selected_location': location,
        'start': start,
        'end': end,
    })

# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Customer, SupplyHistory  # ✅ correct
from .forms import SupplyForm


@login_required
def add_supply(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)

    if request.method == "POST":
        form = SupplyForm(request.POST)
        if form.is_valid():
            supply = form.save(commit=False)
            supply.customer = customer
            supply.save()

           
            messages.success(request, f"Supply of {supply.amount} added for {customer.name}.")
            return redirect("transactions:customer_detail", pk=customer.id)
    else:
        form = SupplyForm()

    context = {
        "customer": customer,
        "form": form,
    }
    return render(request, "transactions/add_supply.html", context)


import csv
from django.http import HttpResponse
from .models import Customer

def export_customers_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="customers.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Phone', 'Email', 'TIN', 'Supply', 'Balance'])

    for customer in Customer.objects.all():
        writer.writerow([customer.name, customer.phone, customer.email, customer.tin, customer.supply, customer.balance])

    return response














# ---------------- Home ----------------
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    return render(request, "transactions/home.html")  # must include 'transactions/'!
