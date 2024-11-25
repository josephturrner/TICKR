from django.shortcuts import render
import psycopg2
import json
from .models import Companies, StockRecords
from .forms import CompanySearchForm
from plotly.express import line
import plotly
import pandas as pd

def home(request):

    if request.method == 'POST':
        search_form = CompanySearchForm(request.POST)
        if search_form.is_valid():
            search_term = search_form.cleaned_data['search_term']
            
            company_data = (
                Companies.objects.filter(name__icontains=search_term) | 
                Companies.objects.filter(symbol__icontains=search_term)
            )

            company_data = company_data[:50]
            search_form = CompanySearchForm()
            return render(request, 'home.html', {'company_data': company_data, 'search_form': search_form})
    else:
        company_data = Companies.objects.exclude(logo__isnull=True)[:50]
        search_form = CompanySearchForm()
        return render(request, 'home.html', {'company_data': company_data, 'search_form': search_form})

def insights(request, symbol):

    company = Companies.objects.filter(symbol=symbol)[0]
    records = StockRecords.objects.filter(symbol_id=symbol).order_by('date')[:1000]

    company_data = {
        'symbol': company.symbol,
        'name': company.name,
        'sector': company.sector,
        'bio': company.bio,
        'website': company.website,
        'logo': company.logo
    }
    data = [
        {
            'date': record.date,
            'open': record.adj_open,
            'close': record.adj_close,
            'dividend': record.dividend,
            'split_factor': record.split_factor,
            'volume': record.adj_volume,
            'high': record.adj_high,
            'low': record.adj_low
        }
        for record in records
    ]

    df = pd.DataFrame(data)

    df['date'] = pd.to_datetime(df['date'])

    fig = line(df, x='date', y='close', title=f'{symbol}', 
                hover_data={
                    'date': True,
                    'dividend': True,
                    'split_factor': True,
                    'volume': True,
                    'high': True,
                    'low': True,
                    'open': True
                })

    chart = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    search_form = CompanySearchForm()

    return render(request, 'insights.html', {'search_form': search_form, 'currentSymbol': symbol, 'chart': chart, 'company': company_data})