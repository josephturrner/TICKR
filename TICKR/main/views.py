from django.shortcuts import render
import psycopg2
from .models import Companies
from .forms import CompanySearchForm

def home(request):

    if request.method == 'POST':
        search_form = CompanySearchForm(request.POST)
        if search_form.is_valid():
            search_term = search_form.cleaned_data['search_term']
            
            # Fetch records using Django ORM
            company_data = Companies.objects.filter(
                name__icontains=search_term  # Case-insensitive search for name
            ) | Companies.objects.filter(
                symbol__icontains=search_term  # Case-insensitive search for symbol
            )

            # Limit the number of records returned (first 50)
            company_data = company_data[:50]
            search_form = CompanySearchForm()
            return render(request, 'home.html', {'company_data': company_data, 'search_form': search_form})
    else:
        company_data = Companies.objects.exclude(logo__isnull=True)[:50]
        search_form = CompanySearchForm()
        return render(request, 'home.html', {'company_data': company_data, 'search_form': search_form})