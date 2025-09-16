
from django.shortcuts import render, redirect
from .models import Location
from django import forms
from django.views.decorators.http import require_POST
from django.http import JsonResponse
class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['name','address']
def location_list(request):
    return render(request,'core/location_list.html', {'locations': Location.objects.all()})
def location_add(request):
    if request.method=='POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            form.save(); return redirect('core:location_list')
    else:
        form = LocationForm()
    return render(request,'core/location_form.html', {'form':form})
@require_POST
def location_create_api(request):
    name = request.POST.get('name'); address = request.POST.get('address','')
    if not name:
        return JsonResponse({'ok':False,'error':'name required'}, status=400)
    loc = Location.objects.create(name=name,address=address)
    return JsonResponse({'ok':True,'id':loc.id,'name':loc.name})
