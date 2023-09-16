import mysql.connector
from faker import Faker
import random
from datetime import datetime, timedelta

# Connect to the MySQL Database (replace placeholders with your actual database credentials)
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="companyvizbot",
    auth_plugin='mysql_native_password'
)
cursor = db.cursor()

# Initialize Faker for generating fake data
fake = Faker()

# Define Tables for Library Management System
# Employees Table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        employee_id INT AUTO_INCREMENT PRIMARY KEY,
        first_name VARCHAR(50),
        last_name VARCHAR(50),
        department_id INT,
        hire_date DATE
    )
""")

# Departments Table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS departments (
        department_id INT AUTO_INCREMENT PRIMARY KEY,
        department_name VARCHAR(100)
    )
""")

# Projects Table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        project_id INT AUTO_INCREMENT PRIMARY KEY,
        project_name VARCHAR(100),
        start_date DATE,
        end_date DATE
    )
""")

# Customers Table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INT AUTO_INCREMENT PRIMARY KEY,
        first_name VARCHAR(50),
        last_name VARCHAR(50),
        email VARCHAR(100)
    )
""")

# Orders Table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id INT AUTO_INCREMENT PRIMARY KEY,
        customer_id INT,
        order_date DATE
    )
""")

# Products Table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        product_id INT AUTO_INCREMENT PRIMARY KEY,
        product_name VARCHAR(100),
        price DECIMAL(10, 2)
    )
""")

# Suppliers Table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS suppliers (
        supplier_id INT AUTO_INCREMENT PRIMARY KEY,
        supplier_name VARCHAR(100),
        contact VARCHAR(100)
    )
""")

# Products_Suppliers Table (for the relationship between products and suppliers)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS products_suppliers (
        product_id INT,
        supplier_id INT
    )
""")

# Insert Sample Data into Tables
departments = ["HR", "Finance", "IT", "Sales", "Marketing", "Engineering", "Operations"]
for department in departments:
    cursor.execute("INSERT INTO departments (department_name) VALUES (%s)", (department,))

for _ in range(3000):
    first_name = fake.first_name()
    last_name = fake.last_name()
    department_id = random.randint(1, 7)  # Assuming 7 departments
    hire_date = fake.date_between(start_date='-10y', end_date='today')
    cursor.execute("""
        INSERT INTO employees (first_name, last_name, department_id, hire_date)
        VALUES (%s, %s, %s, %s)
    """, (first_name, last_name, department_id, hire_date))

for _ in range(3000):
    project_name = fake.company_suffix()
    start_date = fake.date_between(start_date='-2y', end_date='today')
    end_date = start_date + timedelta(days=random.randint(30, 365))
    cursor.execute("""
        INSERT INTO projects (project_name, start_date, end_date)
        VALUES (%s, %s, %s)
    """, (project_name, start_date, end_date))

for _ in range(3000):
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = fake.email()
    cursor.execute("""
        INSERT INTO customers (first_name, last_name, email)
        VALUES (%s, %s, %s)
    """, (first_name, last_name, email))

for _ in range(3000):
    customer_id = random.randint(1, 3000)  # Assuming 3000 customers
    order_date = fake.date_between(start_date='-1y', end_date='today')
    cursor.execute("""
        INSERT INTO orders (customer_id, order_date)
        VALUES (%s, %s)
    """, (customer_id, order_date))

for _ in range(3000):
    product_name = fake.unique.company()
    price = round(random.uniform(5, 200), 2)
    cursor.execute("""
        INSERT INTO products (product_name, price)
        VALUES (%s, %s)
    """, (product_name, price))

for _ in range(3000):
    supplier_name = fake.unique.company()
    contact = fake.name()
    cursor.execute("""
        INSERT INTO suppliers (supplier_name, contact)
        VALUES (%s, %s)
    """, (supplier_name, contact))

for _ in range(3000):
    product_id = random.randint(1, 3000)  # Assuming 3000 products
    supplier_id = random.randint(1, 3000)  # Assuming 3000 suppliers
    cursor.execute("""
        INSERT INTO products_suppliers (product_id, supplier_id)
        VALUES (%s, %s)
    """, (product_id, supplier_id))

# Commit the changes
db.commit()

# Close Database Connection
cursor.close()
db.close()