from django import forms

class CompanySearchForm(forms.Form):
    search_term = forms.CharField(
        label='', 
        max_length=25, 
        widget=forms.TextInput(
            attrs={
                'class': 'nav-form-search',
                'placeholder': 'Search for stock...'
            }
        )
    )

