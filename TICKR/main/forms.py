from django import forms

class CompanySearchForm(forms.Form):
    company_symbol = forms.CharField(label='', max_length=4)