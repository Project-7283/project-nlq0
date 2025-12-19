
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from faker import Faker
import os

# Initialize Faker for realistic data generation
fake = Faker()
np.random.seed(42)
random.seed(42)

# Create output directory
output_dir = "enterprise_dataset_csv"
os.makedirs(output_dir, exist_ok=True)

print("Generating Enterprise Dataset CSV Files...")
print("=" * 50)

# 1. DEPARTMENTS TABLE
print("Generating departments.csv...")
departments_data = {
    'department_id': range(1, 21),
    'department_name': [
        'Human Resources', 'Finance', 'Sales', 'Marketing', 'IT',
        'Operations', 'Customer Service', 'Legal', 'Procurement', 'Quality',
        'Research & Development', 'Manufacturing', 'Logistics', 'Compliance',
        'Business Development', 'Product Management', 'Data Analytics', 
        'Security', 'Training', 'Administration'
    ],
    'department_head': [fake.name() for _ in range(20)],
    'budget': np.random.randint(500000, 5000000, 20),
    'location': [fake.city() for _ in range(20)],
    'created_date': [fake.date_between(start_date='-5y', end_date='today') for _ in range(20)]
}
pd.DataFrame(departments_data).to_csv(f"{output_dir}/departments.csv", index=False)

# 2. EMPLOYEES TABLE
print("Generating employees.csv...")
n_employees = 5000
departments = list(range(1, 21))
positions = ['Manager', 'Senior', 'Junior', 'Lead', 'Specialist', 'Coordinator', 'Analyst', 'Associate']

employees_data = {
    'employee_id': range(1, n_employees + 1),
    'first_name': [fake.first_name() for _ in range(n_employees)],
    'last_name': [fake.last_name() for _ in range(n_employees)],
    'email': [fake.email() for _ in range(n_employees)],
    'phone': [fake.phone_number() for _ in range(n_employees)],
    'department_id': np.random.choice(departments, n_employees),
    'position': np.random.choice(positions, n_employees),
    'salary': np.random.randint(35000, 200000, n_employees),
    'hire_date': [fake.date_between(start_date='-10y', end_date='today') for _ in range(n_employees)],
    'manager_id': np.random.choice([None] + list(range(1, min(500, n_employees))), n_employees),
    'status': np.random.choice(['Active', 'Inactive', 'On Leave'], n_employees, p=[0.85, 0.1, 0.05]),
    'address': [fake.address().replace('\n', ', ') for _ in range(n_employees)],
    'birth_date': [fake.date_of_birth(minimum_age=22, maximum_age=65) for _ in range(n_employees)]
}
pd.DataFrame(employees_data).to_csv(f"{output_dir}/employees.csv", index=False)

# 3. CUSTOMERS TABLE
print("Generating customers.csv...")
n_customers = 10000
customer_types = ['Individual', 'Small Business', 'Enterprise', 'Government']
customer_segments = ['Premium', 'Standard', 'Basic', 'VIP']

customers_data = {
    'customer_id': range(1, n_customers + 1),
    'customer_name': [fake.company() if random.random() > 0.3 else fake.name() for _ in range(n_customers)],
    'customer_type': np.random.choice(customer_types, n_customers),
    'customer_segment': np.random.choice(customer_segments, n_customers),
    'email': [fake.email() for _ in range(n_customers)],
    'phone': [fake.phone_number() for _ in range(n_customers)],
    'address': [fake.address().replace('\n', ', ') for _ in range(n_customers)],
    'city': [fake.city() for _ in range(n_customers)],
    'state': [fake.state() for _ in range(n_customers)],
    'country': [fake.country() for _ in range(n_customers)],
    'postal_code': [fake.postcode() for _ in range(n_customers)],
    'registration_date': [fake.date_between(start_date='-5y', end_date='today') for _ in range(n_customers)],
    'credit_limit': np.random.randint(1000, 100000, n_customers),
    'account_manager_id': np.random.choice(range(1, min(200, n_employees)), n_customers),
    'status': np.random.choice(['Active', 'Inactive', 'Suspended'], n_customers, p=[0.8, 0.15, 0.05])
}
pd.DataFrame(customers_data).to_csv(f"{output_dir}/customers.csv", index=False)

# 4. PRODUCTS TABLE
print("Generating products.csv...")
n_products = 2000
categories = ['Electronics', 'Software', 'Hardware', 'Services', 'Accessories', 'Training', 'Support']
brands = ['TechCorp', 'InnovatePro', 'DataSystems', 'CloudTech', 'SmartSolutions', 'Enterprise+']

products_data = {
    'product_id': range(1, n_products + 1),
    'product_name': [f"{fake.catch_phrase()} {fake.word().title()}" for _ in range(n_products)],
    'product_code': [f"PRD-{i:06d}" for i in range(1, n_products + 1)],
    'category': np.random.choice(categories, n_products),
    'brand': np.random.choice(brands, n_products),
    'description': [fake.text(max_nb_chars=200) for _ in range(n_products)],
    'unit_price': np.round(np.random.uniform(10, 5000, n_products), 2),
    'cost_price': lambda prices: np.round(prices * np.random.uniform(0.4, 0.8, n_products), 2),
    'weight_kg': np.round(np.random.uniform(0.1, 50, n_products), 2),
    'dimensions': [f"{np.random.randint(5,50)}x{np.random.randint(5,50)}x{np.random.randint(2,20)} cm" for _ in range(n_products)],
    'supplier_id': np.random.choice(range(1, 101), n_products),
    'reorder_point': np.random.randint(10, 500, n_products),
    'status': np.random.choice(['Active', 'Discontinued', 'Coming Soon'], n_products, p=[0.8, 0.15, 0.05]),
    'launch_date': [fake.date_between(start_date='-3y', end_date='today') for _ in range(n_products)]
}
# Calculate cost price based on unit price
unit_prices = products_data['unit_price']
products_data['cost_price'] = np.round(unit_prices * np.random.uniform(0.4, 0.8, n_products), 2)
pd.DataFrame(products_data).to_csv(f"{output_dir}/products.csv", index=False)

# 5. ORDERS TABLE
print("Generating orders.csv...")
n_orders = 50000
order_statuses = ['Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled', 'Returned']

orders_data = {
    'order_id': range(1, n_orders + 1),
    'customer_id': np.random.choice(range(1, n_customers + 1), n_orders),
    'employee_id': np.random.choice(range(1, min(500, n_employees)), n_orders),
    'order_date': [fake.date_between(start_date='-2y', end_date='today') for _ in range(n_orders)],
    'required_date': [fake.date_between(start_date='today', end_date='+1y') for _ in range(n_orders)],
    'shipped_date': [fake.date_between(start_date='-2y', end_date='today') if random.random() > 0.2 else None for _ in range(n_orders)],
    'ship_via': np.random.choice(['FedEx', 'UPS', 'DHL', 'USPS', 'Local Delivery'], n_orders),
    'freight': np.round(np.random.uniform(5, 500, n_orders), 2),
    'status': np.random.choice(order_statuses, n_orders, p=[0.1, 0.15, 0.25, 0.35, 0.1, 0.05]),
    'total_amount': np.round(np.random.uniform(50, 50000, n_orders), 2),
    'discount_percentage': np.random.choice([0, 5, 10, 15, 20], n_orders, p=[0.4, 0.25, 0.2, 0.1, 0.05]),
    'tax_amount': lambda total: np.round(total * 0.08, 2),  # 8% tax
    'notes': [fake.text(max_nb_chars=100) if random.random() > 0.7 else None for _ in range(n_orders)]
}
# Calculate tax based on total amount
total_amounts = orders_data['total_amount']
orders_data['tax_amount'] = np.round(total_amounts * 0.08, 2)
pd.DataFrame(orders_data).to_csv(f"{output_dir}/orders.csv", index=False)

# 6. ORDER_LINE_ITEMS TABLE
print("Generating order_line_items.csv...")
n_line_items = 150000  # Average 3 items per order

line_items_data = {
    'line_item_id': range(1, n_line_items + 1),
    'order_id': np.random.choice(range(1, n_orders + 1), n_line_items),
    'product_id': np.random.choice(range(1, n_products + 1), n_line_items),
    'quantity': np.random.randint(1, 20, n_line_items),
    'unit_price': np.round(np.random.uniform(10, 5000, n_line_items), 2),
    'discount': np.round(np.random.uniform(0, 50, n_line_items), 2),
    'line_total': lambda qty, price, disc: np.round(qty * price - disc, 2)
}
# Calculate line total
quantities = line_items_data['quantity']
unit_prices = line_items_data['unit_price']
discounts = line_items_data['discount']
line_items_data['line_total'] = np.round(quantities * unit_prices - discounts, 2)
pd.DataFrame(line_items_data).to_csv(f"{output_dir}/order_line_items.csv", index=False)

# 7. SUPPLIERS TABLE
print("Generating suppliers.csv...")
n_suppliers = 500
supplier_types = ['Manufacturer', 'Distributor', 'Service Provider', 'Consultant']

suppliers_data = {
    'supplier_id': range(1, n_suppliers + 1),
    'supplier_name': [fake.company() for _ in range(n_suppliers)],
    'supplier_type': np.random.choice(supplier_types, n_suppliers),
    'contact_person': [fake.name() for _ in range(n_suppliers)],
    'email': [fake.email() for _ in range(n_suppliers)],
    'phone': [fake.phone_number() for _ in range(n_suppliers)],
    'address': [fake.address().replace('\n', ', ') for _ in range(n_suppliers)],
    'city': [fake.city() for _ in range(n_suppliers)],
    'country': [fake.country() for _ in range(n_suppliers)],
    'payment_terms': np.random.choice(['Net 30', 'Net 60', 'COD', '2/10 Net 30', 'Net 15'], n_suppliers),
    'rating': np.round(np.random.uniform(1, 5, n_suppliers), 1),
    'status': np.random.choice(['Active', 'Inactive', 'Under Review'], n_suppliers, p=[0.8, 0.15, 0.05]),
    'contract_start': [fake.date_between(start_date='-3y', end_date='today') for _ in range(n_suppliers)],
    'contract_end': [fake.date_between(start_date='today', end_date='+2y') for _ in range(n_suppliers)]
}
pd.DataFrame(suppliers_data).to_csv(f"{output_dir}/suppliers.csv", index=False)

# 8. INVENTORY TRANSACTIONS TABLE
print("Generating inventory_transactions.csv...")
n_transactions = 100000
transaction_types = ['Purchase', 'Sale', 'Adjustment', 'Transfer', 'Return']

inventory_data = {
    'transaction_id': range(1, n_transactions + 1),
    'product_id': np.random.choice(range(1, n_products + 1), n_transactions),
    'transaction_type': np.random.choice(transaction_types, n_transactions),
    'transaction_date': [fake.date_between(start_date='-1y', end_date='today') for _ in range(n_transactions)],
    'quantity': np.random.randint(-100, 100, n_transactions),  # Negative for outbound
    'unit_cost': np.round(np.random.uniform(5, 1000, n_transactions), 2),
    'total_cost': lambda qty, cost: np.round(abs(qty) * cost, 2),
    'location': np.random.choice(['Warehouse A', 'Warehouse B', 'Store 1', 'Store 2', 'Online'], n_transactions),
    'reference_id': [f"REF-{i:08d}" for i in range(1, n_transactions + 1)],
    'notes': [fake.sentence() if random.random() > 0.8 else None for _ in range(n_transactions)]
}
# Calculate total cost
quantities = inventory_data['quantity']
unit_costs = inventory_data['unit_cost']
inventory_data['total_cost'] = np.round(np.abs(quantities) * unit_costs, 2)
pd.DataFrame(inventory_data).to_csv(f"{output_dir}/inventory_transactions.csv", index=False)

# 9. SALES PERFORMANCE TABLE
print("Generating sales_performance.csv...")
n_sales_records = 12000  # Monthly records for employees over 2 years

sales_performance_data = {
    'record_id': range(1, n_sales_records + 1),
    'employee_id': np.random.choice(range(1, min(500, n_employees)), n_sales_records),
    'month_year': [fake.date_between(start_date='-2y', end_date='today').strftime('%Y-%m') for _ in range(n_sales_records)],
    'sales_target': np.random.randint(10000, 500000, n_sales_records),
    'actual_sales': np.random.randint(5000, 600000, n_sales_records),
    'leads_generated': np.random.randint(5, 200, n_sales_records),
    'leads_converted': np.random.randint(1, 50, n_sales_records),
    'calls_made': np.random.randint(50, 500, n_sales_records),
    'meetings_held': np.random.randint(10, 100, n_sales_records),
    'commission_earned': np.round(np.random.uniform(500, 50000, n_sales_records), 2),
    'region': np.random.choice(['North', 'South', 'East', 'West', 'Central'], n_sales_records)
}
pd.DataFrame(sales_performance_data).to_csv(f"{output_dir}/sales_performance.csv", index=False)

# 10. CUSTOMER SERVICE CASES TABLE
print("Generating service_cases.csv...")
n_cases = 25000
case_categories = ['Technical Support', 'Billing Issue', 'Product Inquiry', 'Complaint', 'Feature Request']
priorities = ['Low', 'Medium', 'High', 'Critical']
statuses = ['Open', 'In Progress', 'Resolved', 'Closed', 'Escalated']

service_cases_data = {
    'case_id': range(1, n_cases + 1),
    'customer_id': np.random.choice(range(1, n_customers + 1), n_cases),
    'assigned_agent_id': np.random.choice(range(1, min(200, n_employees)), n_cases),
    'category': np.random.choice(case_categories, n_cases),
    'priority': np.random.choice(priorities, n_cases, p=[0.4, 0.3, 0.25, 0.05]),
    'status': np.random.choice(statuses, n_cases, p=[0.15, 0.20, 0.35, 0.25, 0.05]),
    'subject': [fake.sentence() for _ in range(n_cases)],
    'description': [fake.text(max_nb_chars=300) for _ in range(n_cases)],
    'created_date': [fake.date_between(start_date='-1y', end_date='today') for _ in range(n_cases)],
    'resolved_date': [fake.date_between(start_date='-1y', end_date='today') if random.random() > 0.3 else None for _ in range(n_cases)],
    'satisfaction_score': np.random.choice([1, 2, 3, 4, 5], n_cases, p=[0.05, 0.1, 0.2, 0.4, 0.25]),
    'resolution_time_hours': np.random.randint(1, 168, n_cases)  # Up to 1 week
}
pd.DataFrame(service_cases_data).to_csv(f"{output_dir}/service_cases.csv", index=False)

# 11. FINANCIAL TRANSACTIONS TABLE
print("Generating financial_transactions.csv...")
n_financial = 200000
transaction_types = ['Revenue', 'Expense', 'Asset Purchase', 'Liability', 'Equity']
account_codes = [f"ACC-{i:04d}" for i in range(1000, 9999, 100)]

financial_data = {
    'transaction_id': range(1, n_financial + 1),
    'transaction_date': [fake.date_between(start_date='-2y', end_date='today') for _ in range(n_financial)],
    'account_code': np.random.choice(account_codes, n_financial),
    'transaction_type': np.random.choice(transaction_types, n_financial),
    'description': [fake.sentence() for _ in range(n_financial)],
    'debit_amount': np.round(np.random.uniform(0, 100000, n_financial), 2),
    'credit_amount': np.round(np.random.uniform(0, 100000, n_financial), 2),
    'reference_id': [f"TXN-{i:08d}" for i in range(1, n_financial + 1)],
    'department_id': np.random.choice(range(1, 21), n_financial),
    'approved_by': np.random.choice(range(1, min(100, n_employees)), n_financial),
    'status': np.random.choice(['Posted', 'Pending', 'Cancelled'], n_financial, p=[0.85, 0.12, 0.03])
}
pd.DataFrame(financial_data).to_csv(f"{output_dir}/financial_transactions.csv", index=False)

# 12. MARKETING CAMPAIGNS TABLE
print("Generating marketing_campaigns.csv...")
n_campaigns = 500
campaign_types = ['Email', 'Social Media', 'Print', 'Radio', 'TV', 'Online Display', 'Webinar']
channels = ['Facebook', 'Google Ads', 'LinkedIn', 'Email Newsletter', 'Direct Mail', 'Trade Show']

campaigns_data = {
    'campaign_id': range(1, n_campaigns + 1),
    'campaign_name': [f"{fake.catch_phrase()} Campaign" for _ in range(n_campaigns)],
    'campaign_type': np.random.choice(campaign_types, n_campaigns),
    'channel': np.random.choice(channels, n_campaigns),
    'start_date': [fake.date_between(start_date='-2y', end_date='today') for _ in range(n_campaigns)],
    'end_date': [fake.date_between(start_date='today', end_date='+1y') for _ in range(n_campaigns)],
    'budget': np.round(np.random.uniform(1000, 500000, n_campaigns), 2),
    'actual_spend': np.round(np.random.uniform(800, 450000, n_campaigns), 2),
    'target_audience': [fake.job() for _ in range(n_campaigns)],
    'impressions': np.random.randint(1000, 1000000, n_campaigns),
    'clicks': np.random.randint(10, 50000, n_campaigns),
    'conversions': np.random.randint(1, 5000, n_campaigns),
    'manager_id': np.random.choice(range(1, min(50, n_employees)), n_campaigns),
    'status': np.random.choice(['Active', 'Completed', 'Paused', 'Cancelled'], n_campaigns, p=[0.3, 0.4, 0.2, 0.1])
}
pd.DataFrame(campaigns_data).to_csv(f"{output_dir}/marketing_campaigns.csv", index=False)

# Generate additional relationship tables
print("Generating additional relationship tables...")

# Employee Skills
n_skills = 100
skills_list = ['Python', 'SQL', 'Project Management', 'Sales', 'Marketing', 'Finance', 'Leadership', 'Communication']
employee_skills_data = {
    'record_id': range(1, 5001),
    'employee_id': np.random.choice(range(1, n_employees + 1), 5000),
    'skill_name': np.random.choice(skills_list * 12, 5000),  # Expand skill list
    'proficiency_level': np.random.choice(['Beginner', 'Intermediate', 'Advanced', 'Expert'], 5000),
    'certified': np.random.choice([True, False], 5000, p=[0.3, 0.7]),
    'last_updated': [fake.date_between(start_date='-2y', end_date='today') for _ in range(5000)]
}
pd.DataFrame(employee_skills_data).to_csv(f"{output_dir}/employee_skills.csv", index=False)

# Regional Sales Data
regions_data = {
    'region_id': range(1, 11),
    'region_name': ['North America', 'South America', 'Europe', 'Asia-Pacific', 'Middle East', 
                   'Africa', 'Oceania', 'Central America', 'Eastern Europe', 'Southeast Asia'],
    'region_manager': [fake.name() for _ in range(10)],
    'headquarters': [fake.city() for _ in range(10)],
    'established_date': [fake.date_between(start_date='-10y', end_date='-1y') for _ in range(10)]
}
pd.DataFrame(regions_data).to_csv(f"{output_dir}/regions.csv", index=False)

print("\nDataset Generation Complete!")
print("=" * 50)
print(f"Generated {len(os.listdir(output_dir))} CSV files in '{output_dir}' directory:")
for file in sorted(os.listdir(output_dir)):
    if file.endswith('.csv'):
        df = pd.read_csv(f"{output_dir}/{file}")
        print(f"  {file}: {len(df)} rows, {len(df.columns)} columns")

print("\nKey Statistics:")
print(f"  Total Employees: {n_employees:,}")
print(f"  Total Customers: {n_customers:,}")
print(f"  Total Products: {n_products:,}")
print(f"  Total Orders: {n_orders:,}")
print(f"  Total Transactions: {n_financial:,}")
print(f"  Date Range: 2019 - 2025")
print(f"  Geographic Coverage: Global")

print("\nSample NLQ Test Queries:")
print("1. 'Show me top 10 employees by sales performance this year'")
print("2. 'Which customers have the highest order volumes in Electronics category?'")
print("3. 'Compare marketing campaign ROI across different channels'")
print("4. 'Analyze service case resolution times by priority level'")
print("5. 'Show inventory turnover rates by product category and location'")

print("\nDataset ready for NLQ system testing!")
