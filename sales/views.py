from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.http import HttpResponse
from django.db.models import Sum, Q
from .models import SaleEntry
from .forms import SaleEntryForm
import csv

class OwnerQuerysetMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)

class SaleListView(LoginRequiredMixin, OwnerQuerysetMixin, ListView):
    model = SaleEntry
    template_name = 'sales/sale_list.html'
    context_object_name = 'rows'
    paginate_by = 30

    def get_queryset(self):
        qs = super().get_queryset().order_by('-date')
        start = self.request.GET.get('start')
        end = self.request.GET.get('end')
        q = self.request.GET.get('q')
        if start:
            qs = qs.filter(date__gte=start)
        if end:
            qs = qs.filter(date__lte=end)
        if q:
            q = q.strip()
            qs = qs.filter(
                Q(opening_cash__icontains=q) | Q(customer_balance__icontains=q) |
                Q(wholesale__icontains=q) | Q(retail_sale__icontains=q) |
                Q(expenses__icontains=q) | Q(bank_deposit__icontains=q) |
                Q(date__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = ctx['rows']
        agg = qs.aggregate(
            total_daily=Sum('daily_total'),
            total_diff=Sum('cash_difference'),
            total_customer_balance=Sum('customer_balance'),
            total_wholesale=Sum('wholesale'),
            total_retail=Sum('retail_sale'),
            total_expenses=Sum('expenses'),
            total_deposits=Sum('bank_deposit'),
        )
        # Monthly stats for current month
        from django.utils import timezone
        now = timezone.localdate()
        month_qs = self.get_queryset().filter(date__year=now.year, date__month=now.month)
        month_agg = month_qs.aggregate(month_sales=Sum('daily_total'))
        total_entries = qs.count()
        avg_daily = (agg['total_daily'] or 0) / total_entries if total_entries else 0

        ctx.update({
            'agg': agg,
            'month_sales': month_agg['month_sales'] or 0,
            'avg_daily': avg_daily,
            'record_count': total_entries,
            'params': {
                'start': self.request.GET.get('start', ''),
                'end': self.request.GET.get('end', ''),
                'q': self.request.GET.get('q', ''),
            }
        })
        return ctx

class OwnerFormMixin:
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class SaleCreateView(LoginRequiredMixin, OwnerFormMixin, CreateView):
    model = SaleEntry
    form_class = SaleEntryForm
    template_name = 'sales/sale_form.html'
    success_url = reverse_lazy('sales:list')

class SaleUpdateView(LoginRequiredMixin, OwnerQuerysetMixin, OwnerFormMixin, UpdateView):
    model = SaleEntry
    form_class = SaleEntryForm
    template_name = 'sales/sale_form.html'
    success_url = reverse_lazy('sales:list')

class SaleDeleteView(LoginRequiredMixin, OwnerQuerysetMixin, DeleteView):
    model = SaleEntry
    template_name = 'sales/sale_confirm_delete.html'
    success_url = reverse_lazy('sales:list')

def export_csv(request):
    if not request.user.is_authenticated:
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(request.get_full_path())

    qs = SaleEntry.objects.filter(user=request.user).order_by('date', 'id')
    start = request.GET.get('start')
    end = request.GET.get('end')
    q = request.GET.get('q')
    if start:
        qs = qs.filter(date__gte=start)
    if end:
        qs = qs.filter(date__lte=end)
    if q:
        qs = qs.filter(
            Q(opening_cash__icontains=q) | Q(customer_balance__icontains=q) |
            Q(wholesale__icontains=q) | Q(retail_sale__icontains=q) |
            Q(expenses__icontains=q) | Q(bank_deposit__icontains=q) |
            Q(date__icontains=q)
        )

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="teba_sales.csv"'
    writer = csv.writer(response)
    writer.writerow(["Date","Opening Cash","Customer Balance","Wholesale","Retail Sale","Expenses","Bank Deposit","Cash Difference","Daily Total","Net Cash After Deposit"])
    for r in qs:
        writer.writerow([
            r.date, f"{r.opening_cash:.2f}", f"{r.customer_balance:.2f}", f"{r.wholesale:.2f}",
            f"{r.retail_sale:.2f}", f"{r.expenses:.2f}", f"{r.bank_deposit:.2f}",
            f"{r.cash_difference:.2f}", f"{r.daily_total:.2f}", f"{r.net_cash_after_deposit:.2f}"
        ])
    return response

def clear_all(request):
    if not request.user.is_authenticated:
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(request.get_full_path())
    SaleEntry.objects.filter(user=request.user).delete()
    return redirect('sales:list')

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from .models import Location
from django.db.models import Sum

def is_staff(user):
    return user.is_superuser or user.is_staff

@login_required
def locations_list(request):
    q = request.GET.get('q','').strip()
    qs = Location.objects.all()
    if q:
        qs = qs.filter(name__icontains=q)
    return render(request, 'sales/locations.html', {'locations': qs, 'q': q})

@login_required
def location_create(request):
    if request.method == 'POST':
        name = request.POST.get('name','').strip()
        address = request.POST.get('address','').strip()
        if name:
            Location.objects.create(name=name, address=address)
            return redirect('sales:locations')
    return render(request, 'sales/location_form.html', {'create': True})

@login_required
def location_edit(request, pk):
    obj = get_object_or_404(Location, pk=pk)
    if request.method == 'POST':
        obj.name = request.POST.get('name', obj.name)
        obj.address = request.POST.get('address', obj.address)
        obj.save()
        return redirect('sales:locations')
    return render(request, 'sales/location_form.html', {'create': False, 'obj': obj})

@login_required
def location_delete(request, pk):
    obj = get_object_or_404(Location, pk=pk)
    if request.method == 'POST':
        obj.delete()
        return redirect('sales:locations')
    return render(request, 'sales/location_confirm_delete.html', {'obj': obj})

@login_required
def reports_view(request):
    start = request.GET.get('start')
    end = request.GET.get('end')
    loc_id = request.GET.get('location')
    entries = SaleEntry.objects.filter(user=request.user)
    if start:
        entries = entries.filter(date__gte=start)
    if end:
        entries = entries.filter(date__lte=end)
    if loc_id:
        entries = entries.filter(location_id=loc_id)

    agg = entries.aggregate(
        total_wholesale=Sum('wholesale'),
        total_retail=Sum('retail_sale'),
        total_expenses=Sum('expenses'),
        total_deposits=Sum('bank_deposit'),
        total_daily=Sum('daily_total'),
    )
    locations = Location.objects.all()
    return render(request, 'sales/reports.html', {'agg': agg, 'locations': locations, 'params': {'start': start or '', 'end': end or '', 'location': int(loc_id) if loc_id else ''}})
