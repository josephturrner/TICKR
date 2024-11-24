from django.shortcuts import render
from .models import Companies

# Create your views here.

def home(request):
    company_data = Companies.objects.all()
    return render(request, 'home.html', {'company_data': company_data})