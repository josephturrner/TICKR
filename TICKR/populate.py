import psycopg2
from psycopg2.extras import execute_values
import environ
import requests
import time
import json

# Read environment variables
env = environ.Env()
environ.Env.read_env()

# DB connection
DB_NAME = env('DB_NAME')
DB_USER = env('DB_USER')
DB_PASSWORD = env('DB_PASSWORD')
DB_HOST = env('DB_HOST')
DB_PORT = env('DB_PORT')

# Hardcoded list to populate database
companies = [
    ('NVDA', 'NVIDIA Corporation', 'Technology', 'https://www.nvidia.com', 'NVIDIA specializes in graphics processing units (GPUs) and AI technologies, powering industries like gaming, data centers, and autonomous vehicles.', 'https://latestlogo.com/logos/nvidia/'),
    ('AAPL', 'Apple Inc.', 'Technology', 'https://www.apple.com', 'Apple is renowned for its innovative consumer electronics, including the iPhone, Mac, and Apple Watch, and its software ecosystem like iOS and macOS.', 'https://www.apple.com/ac/structured-data/images/open_graph_logo.png?202310180743'),
    ('MSFT', 'Microsoft Corporation', 'Technology', 'https://www.microsoft.com', 'Microsoft develops software like Windows, Office, and Azure cloud solutions, driving innovation in productivity and enterprise services.', 'https://logo.clearbit.com/microsoft.com'),
    ('AMZN', 'Amazon.com Inc.', 'Consumer Discretionary', 'https://www.amazon.com', 'Amazon is a global leader in e-commerce, cloud computing (AWS), and digital streaming services like Prime Video.', 'https://logo.clearbit.com/amazon.com'),
    ('GOOGL', 'Alphabet Inc. (Class A)', 'Communication Services', 'https://www.abc.xyz', 'Alphabet, the parent company of Google, leads in online advertising, search, cloud services, and technologies like Android and AI.', 'https://logo.clearbit.com/abc.xyz'),
    ('META', 'Meta Platforms, Inc.', 'Communication Services', 'https://www.meta.com', 'Meta connects people through platforms like Facebook, Instagram, and WhatsApp, focusing on virtual reality and the metaverse.', 'https://logo.clearbit.com/meta.com'),
    ('TSLA', 'Tesla, Inc.', 'Consumer Discretionary', 'https://www.tesla.com', 'Tesla is a pioneer in electric vehicles, clean energy solutions like solar panels, and battery storage technologies.', 'https://logo.clearbit.com/tesla.com'),
    ('BRK.B', 'Berkshire Hathaway Inc.', 'Financials', 'https://www.berkshirehathaway.com', 'Berkshire Hathaway is a multinational conglomerate holding company with investments in diverse industries like insurance, utilities, and transportation.', 'https://logo.clearbit.com/berkshirehathaway.com'),
    ('TSM', 'Taiwan Semiconductor Manufacturing Company Limited', 'Technology', 'https://www.tsmc.com', 'TSMC is the world’s leading semiconductor manufacturer, supplying chips for industries ranging from computing to automotive.', 'https://logo.clearbit.com/tsmc.com'),
    ('AVGO', 'Broadcom Inc.', 'Technology', 'https://www.broadcom.com', 'Broadcom designs and develops semiconductors and infrastructure software solutions for networking, storage, and wireless communications.', 'https://logo.clearbit.com/broadcom.com'),
    ('WMT', 'Walmart Inc.', 'Consumer Staples', 'https://www.walmart.com', 'Walmart operates a chain of hypermarkets, discount department stores, and grocery stores worldwide, emphasizing affordability.', 'https://logo.clearbit.com/walmart.com'),
    ('JPM', 'JPMorgan Chase & Co.', 'Financials', 'https://www.jpmorganchase.com', 'JPMorgan Chase is a global leader in investment banking, financial services, and wealth management solutions.', 'https://logo.clearbit.com/jpmorganchase.com'),
    ('LLY', 'Eli Lilly and Company', 'Health Care', 'https://www.lilly.com', 'Eli Lilly develops pharmaceuticals and health solutions for conditions like diabetes, oncology, and immunology.', 'https://logo.clearbit.com/lilly.com'),
    ('V', 'Visa Inc.', 'Financials', 'https://www.visa.com', 'Visa is a global payment technology company connecting consumers and businesses through secure electronic transactions.', 'https://logo.clearbit.com/visa.com'),
    ('UNH', 'UnitedHealth Group Incorporated', 'Health Care', 'https://www.unitedhealthgroup.com', 'UnitedHealth Group offers health care benefits and services through its Optum and UnitedHealthcare divisions.', 'https://logo.clearbit.com/unitedhealthgroup.com'),
    ('XOM', 'Exxon Mobil Corporation', 'Energy', 'https://www.exxonmobil.com', 'ExxonMobil is a multinational oil and gas corporation focusing on energy production, exploration, and chemical manufacturing.', 'https://logo.clearbit.com/exxonmobil.com'),
    ('ORCL', 'Oracle Corporation', 'Technology', 'https://www.oracle.com', 'Oracle develops database software, cloud solutions, and enterprise software to streamline business operations.', 'https://logo.clearbit.com/oracle.com'),
    ('MA', 'Mastercard Incorporated', 'Financials', 'https://www.mastercard.com', 'Mastercard is a global financial services company offering payment solutions for consumers, businesses, and governments.', 'https://logo.clearbit.com/mastercard.com'),
    ('NVO', 'Novo Nordisk A/S', 'Health Care', 'https://www.novonordisk.com', 'Novo Nordisk specializes in diabetes care, hormone replacement therapies, and obesity management solutions.', 'https://logo.clearbit.com/novonordisk.com'),
    ('COST', 'Costco Wholesale Corporation', 'Consumer Staples', 'https://www.costco.com', 'Costco operates membership-based warehouse clubs, offering discounted goods in bulk.', 'https://logo.clearbit.com/costco.com'),
    ('HD', 'The Home Depot, Inc.', 'Consumer Discretionary', 'https://www.homedepot.com', 'The Home Depot is a retailer specializing in home improvement products, tools, and services for homeowners and contractors.', 'https://logo.clearbit.com/homedepot.com'),
    ('PG', 'The Procter & Gamble Company', 'Consumer Staples', 'https://us.pg.com', 'Procter & Gamble produces consumer goods, including household cleaning, personal care, and health products.', 'https://logo.clearbit.com/pg.com'),
    ('NFLX', 'Netflix, Inc.', 'Communication Services', 'https://www.netflix.com', 'Netflix is a global streaming service offering original and licensed movies, TV shows, and documentaries.', 'https://logo.clearbit.com/netflix.com'),
    ('JNJ', 'Johnson & Johnson', 'Health Care', 'https://www.jnj.com', 'Johnson & Johnson develops pharmaceuticals, medical devices, and consumer health products.', 'https://logo.clearbit.com/jnj.com'),
    ('BAC', 'Bank of America Corporation', 'Financials', 'https://www.bankofamerica.com', 'Bank of America provides financial services, including banking, lending, and wealth management, to individuals and businesses.', 'https://logo.clearbit.com/bankofamerica.com'),
    ('CRM', 'Salesforce, Inc.', 'Technology', 'https://www.salesforce.com', 'Salesforce develops cloud-based software for customer relationship management (CRM) and enterprise applications.', 'https://logo.clearbit.com/salesforce.com'),
    ('ABBV', 'AbbVie Inc.', 'Health Care', 'https://www.abbvie.com', 'AbbVie develops innovative medicines and therapies, focusing on immunology, oncology, and neuroscience.', 'https://logo.clearbit.com/abbvie.com'),
    ('CVX', 'Chevron Corporation', 'Energy', 'https://www.chevron.com', 'Chevron is an integrated energy company engaged in exploration, production, refining, and distribution.', 'https://logo.clearbit.com/chevron.com'),
    ('TMUS', 'T-Mobile US, Inc.', 'Communication Services', 'https://www.t-mobile.com', 'T-Mobile offers wireless voice, messaging, and data services, leading innovations in 5G technology.', 'https://logo.clearbit.com/t-mobile.com'),
    ('KO', 'The Coca-Cola Company', 'Consumer Staples', 'https://www.coca-colacompany.com', 'The Coca-Cola Company is a leading beverage producer with a portfolio of sparkling and still brands.', 'https://logo.clearbit.com/coca-colacompany.com'),
    ('SAP', 'SAP SE', 'Technology', 'https://www.sap.com', 'SAP develops enterprise software solutions for managing business operations and customer relationships.', 'https://logo.clearbit.com/sap.com'),
    ('ASML', 'ASML Holding N.V.', 'Technology', 'https://www.asml.com', 'ASML manufactures photolithography systems used in semiconductor production for advanced chip technologies.', 'https://logo.clearbit.com/asml.com'),
    ('WFC', 'Wells Fargo & Company', 'Financials', 'https://www.wellsfargo.com', 'Wells Fargo provides banking, mortgage, and financial services to consumers and businesses.', 'https://logo.clearbit.com/wellsfargo.com'),
    ('MRK', 'Merck & Co., Inc.', 'Health Care', 'https://www.merck.com', 'Merck develops medicines and vaccines, focusing on oncology, infectious diseases, and animal health.', 'https://logo.clearbit.com/merck.com'),
    ('BX', 'Blackstone Inc.', 'Financials', 'https://www.blackstone.com', 'Blackstone is a global investment firm specializing in private equity, real estate, and alternative asset management.', 'https://logo.clearbit.com/blackstone.com'),
    ('CSCO', 'Cisco Systems, Inc.', 'Technology', 'https://www.cisco.com', 'Cisco provides networking hardware, software, and cybersecurity solutions for businesses and governments.', 'https://logo.clearbit.com/cisco.com'),
    ('TM', 'Toyota Motor Corporation', 'Consumer Discretionary', 'https://www.toyota-global.com', 'Toyota is a global automotive manufacturer known for its hybrid and electric vehicle innovations.', 'https://logo.clearbit.com/toyota-global.com'),
    ('ADBE', 'Adobe Inc.', 'Technology', 'https://www.adobe.com', 'Adobe is a leader in creative software, offering tools like Photoshop, Illustrator, and cloud-based solutions for content creation and digital marketing.', 'https://logo.clearbit.com/adobe.com'),
    ('AMD', 'Advanced Micro Devices, Inc.', 'Technology', 'https://www.amd.com', 'AMD develops high-performance processors and graphics solutions for gaming, data centers, and PCs.', 'https://logo.clearbit.com/amd.com'),
    ('ACN', 'Accenture plc', 'Information Technology Services', 'https://www.accenture.com', 'Accenture provides consulting and technology services, specializing in digital transformation and enterprise solutions.', 'https://logo.clearbit.com/accenture.com'),
    ('PEP', 'PepsiCo, Inc.', 'Consumer Staples', 'https://www.pepsico.com', 'PepsiCo produces and distributes beverages and snacks, with iconic brands like Pepsi, Lay’s, and Tropicana.', 'https://logo.clearbit.com/pepsico.com'),
    ('NOW', 'ServiceNow, Inc.', 'Technology', 'https://www.servicenow.com', 'ServiceNow provides cloud-based software solutions to manage enterprise workflows and IT operations.', 'https://logo.clearbit.com/servicenow.com'),
    ('MS', 'Morgan Stanley', 'Financials', 'https://www.morganstanley.com', 'Morgan Stanley is a global investment bank offering financial advisory, capital markets, and wealth management services.', 'https://logo.clearbit.com/morganstanley.com'),
    ('LIN', 'Linde plc', 'Materials', 'https://www.linde.com', 'Linde is a global leader in industrial gases and engineering, serving industries like manufacturing, health care, and electronics.', 'https://logo.clearbit.com/linde.com'),
    ('AXP', 'American Express Company', 'Financials', 'https://www.americanexpress.com', 'American Express provides payment services, credit cards, and travel-related offerings for consumers and businesses.', 'https://logo.clearbit.com/americanexpress.com'),
    ('DIS', 'The Walt Disney Company', 'Communication Services', 'https://www.thewaltdisneycompany.com', 'Disney is a global entertainment leader, known for its movies, theme parks, and streaming services like Disney+.', 'https://logo.clearbit.com/thewaltdisneycompany.com'),
    ('NVS', 'Novartis AG', 'Health Care', 'https://www.novartis.com', 'Novartis develops pharmaceuticals and therapies for treating diseases across oncology, neuroscience, and immunology.', 'https://logo.clearbit.com/novartis.com'),
    ('MCD', 'McDonald\'s Corporation', 'Consumer Discretionary', 'https://www.mcdonalds.com', 'McDonald’s operates a global network of fast-food restaurants, focusing on quality and convenience.', 'https://logo.clearbit.com/mcdonalds.com'),
    ('IBM', 'International Business Machines Corporation', 'Technology', 'https://www.ibm.com', 'IBM offers enterprise solutions in cloud computing, artificial intelligence, and IT infrastructure.', 'https://logo.clearbit.com/ibm.com'),
    ('ABT', 'Abbott Laboratories', 'Health Care', 'https://www.abbott.com', 'Abbott produces medical devices, diagnostics, and nutritional products to improve health and well-being.', 'https://logo.clearbit.com/abbott.com')
]

try:

    # Connect to db
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cursor = conn.cursor()

    # Populate database
    insert_query = '''
    INSERT INTO companies (symbol, name, sector, bio, website, logo)
    VALUES %s
    '''
    execute_values(cursor, insert_query, companies)

    # Commit 
    conn.commit()

# Catch error
except psycopg2.Error as e:
    print(f'Error: {e}')
finally:
    # Close the database connection regardless of error
    if cursor:
        cursor.close()
    if conn:
        conn.close()



for idx in range(len(companies)):
    symbol = companies[idx][0]

    # Storing the 1000 days leading up to one year ago
    # When a company is clicked it will populate the most recent year
    # This is for efficiency of api calls on the free tier

    # API call
    querystring = {
        'access_key': env('API_KEY'),
        'symbols': symbol,
        'limit': 1000
    }
    url = 'https://api.marketstack.com/v1/eod'
    response = requests.get(url, params=querystring)
    data = response.json()

    # Format data for insert query
    if 'data' in data:
        eod = data['data']
        records = []
        for report in eod:
            record = (
                report['symbol'],
                report['adj_high'],
                report['adj_low'],
                report['adj_close'],
                report['adj_open'],
                report['adj_volume'],
                report['split_factor'],
                report['dividend'],
                report['exchange'],
                report['date']
            )
            records.append(record)

        try:
            conn = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT
            )
            cursor = conn.cursor()

            insert_query = '''
            INSERT INTO stockrecords (symbol_id, adj_high, adj_low, adj_close, adj_open, adj_volume, split_factor, dividend, exchange, date)
            VALUES %s
            '''
            execute_values(cursor, insert_query, records)
            conn.commit()

        except psycopg2.Error as e:
            print(f'Error inserting data for {symbol} at index {idx}: {e}')
            raise Exception(f'Failed to insert data for {symbol} at index {idx}') from e
        finally:

            # Closing the connection each time because I am making additional api calls
            if cursor:
                cursor.close()
            if conn:
                conn.close()
            # Pause between requests
            time.sleep(5)
    else:
        print(f'No data found for company {symbol} at index {idx}.')
        raise Exception(f'No data found for {symbol} at index {idx}.')



# Used list of about 4000 companies found online to make searching possible without use of api calls
file_path = 'companies.txt'

with open(file_path, 'r') as file:
    companies_data = [line.strip() for line in file.readlines()]

records = []

for line in companies_data:
    symbol, name = line.split('|')
    symbol = symbol.strip()
    name = name.strip()
    records.append((symbol, name))

try:
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    
    # Create a cursor object to interact with the database
    cursor = conn.cursor()
    
    # SQL query to insert the data into the companies table
    insert_query = '''
    INSERT INTO companies (symbol, name)
    VALUES %s
    ON CONFLICT (symbol) DO NOTHING
    '''
    
    execute_values(cursor, insert_query, records)

    conn.commit()

    print(f'Successfully inserted {len(records)} records into the companies table.')
    
except psycopg2.Error as e:
    print(f'Error inserting data: {e}')
finally:
    # Close the cursor and connection
    if cursor:
        cursor.close()
    if conn:
        conn.close()