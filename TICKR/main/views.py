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
            
            # Search database using django ORM
            company_data = (
                Companies.objects.filter(name__icontains=search_term) | 
                Companies.objects.filter(symbol__icontains=search_term)
            )

            # Limit 50
            company_data = company_data[:50]
            # Empty form
            search_form = CompanySearchForm()
            return render(request, 'home.html', {'company_data': company_data, 'search_form': search_form})
    else:
        # Front page has only companies with logos (only 50 for now for development reasons)
        company_data = Companies.objects.exclude(logo__isnull=True)[:50]
        # Empty form
        search_form = CompanySearchForm()
        return render(request, 'home.html', {'company_data': company_data, 'search_form': search_form})

def insights(request, symbol):

    # Fetch company and record data using django ORM
    company = Companies.objects.filter(symbol=symbol)[0] # Only 1 item will return
    records = StockRecords.objects.filter(symbol_id=symbol).order_by('date')[:1000] # Limit 1000

    # Transfer to frontend-safe object
    company_data = {
        'symbol': company.symbol,
        'name': company.name,
        'sector': company.sector,
        'bio': company.bio,
        'website': company.website,
        'logo': company.logo
    }

    # Preprocess for dataframe
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

    # Make sure date is datetime type
    df['date'] = pd.to_datetime(df['date'])

    # Chart to display
    fig = line(df, x='date', y='close', title=f'{symbol}')
    

    # --prim: #e2e2e2;
    # --sec: #2e2e2e;
    # --col: #558e79;

    fig.update_layout(
        plot_bgcolor='#2e2e2e',
        paper_bgcolor='black',
        font_color='#e2e2e2',
        margin=dict(l=0, r=0, t=32, b=0),
        hovermode='x unified',
        xaxis=dict(title=None, gridcolor='black'),
        yaxis=dict(title=None, gridcolor='black', tickprefix='$'),
        title=dict(
            text='CLOSING PRICE',
            font=dict(size=20),
            x=0.5,
            xanchor='center'
        )
    )

    fig.update_traces(
        line=dict(color='#558e79'),
        hovertemplate=(
            "<b>Date: </b> %{x}<br>" 
            "<b>Open: </b> %{customdata[0]:.2f} USD<br>"
            "<b>Close: </b> %{y:.2f} USD<br>"
            "<b>High: </b> %{customdata[1]:.2f} USD<br>"
            "<b>Low: </b> %{customdata[2]:.2f} USD<br>"
            "<b>Volume: </b> %{customdata[3]:,} Shares<br>"
            "<b>Dividend: </b> %{customdata[4]}<br>"
            "<b>Split Factor: </b> %{customdata[5]}<br>"
        ),
        customdata=df[['open', 'high', 'low', 'volume', 'dividend', 'split_factor']].values 
    )

    # Create frontend-safe type for plotly js to process
    chart = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # Empty form to send
    search_form = CompanySearchForm()

    return render(request, 'insights.html', {'search_form': search_form, 'currentSymbol': symbol, 'chart': chart, 'company': company_data})