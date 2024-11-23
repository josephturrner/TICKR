from django.db import models

# CREATE TABLE company (
#     symbol VARCHAR(10) PRIMARY KEY,
#     name VARCHAR(255) NOT NULL,
#     website VARCHAR(255),   
#     logo VARCHAR(255)         
# );

# CREATE TABLE stock_record (    
#     symbol VARCHAR(10) NOT NULL,    
#     adj_high NUMERIC NOT NULL,      
#     adj_low NUMERIC NOT NULL,     
#     adj_close NUMERIC NOT NULL,     
#     adj_open NUMERIC NOT NULL,  
#     adj_volume NUMERIC NOT NULL,    
#     split_factor NUMERIC NOT NULL, 
#     dividend NUMERIC NOT NULL, 
#     exchange VARCHAR(10),  
#     date DATE NOT NULL,
#     PRIMARY KEY (symbol, date),

#     FOREIGN KEY (symbol) REFERENCES company(symbol) ON DELETE CASCADE
# );

class Company(models.Model):
    symbol = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=255)
    website = models.URLField(max_length=255, blank=True, null=True)
    logo = models.URLField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name 

class StockRecord(models.Model):
    symbol = models.ForeignKey(Company, on_delete=models.CASCADE)
    adj_high = models.DecimalField(max_digits=15, decimal_places=2)
    adj_low = models.DecimalField(max_digits=15, decimal_places=2)
    adj_close = models.DecimalField(max_digits=15, decimal_places=2)
    adj_open = models.DecimalField(max_digits=15, decimal_places=2)
    adj_volume = models.DecimalField(max_digits=20, decimal_places=0)
    split_factor = models.DecimalField(max_digits=10, decimal_places=2)
    dividend = models.DecimalField(max_digits=15, decimal_places=2)
    exchange = models.CharField(max_length=10, blank=True, null=True)
    date = models.DateField()

    class Meta:
        unique_together = ('symbol', 'date')
        verbose_name_plural = "Stock Records"

    def __str__(self):
        return f"{self.symbol.symbol} - {self.date}"