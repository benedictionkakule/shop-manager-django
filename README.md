# Shop Manager - Inventory and Sales System (Django)

A web application that helps a small shop manage its stock, customers and daily sales.
Built with Django for the Django Framework examination project.

## The problem it solves

Small shops often track stock and sales in notebooks, which leads to mistakes,
unnoticed stock-outs and no overview of how the business is doing. Shop Manager
records every sale, updates stock automatically, warns when a product is running
low and shows how the shop is performing.

## Features

Core CRUD (Create, Read, Update, Delete):

- Products: add, view, edit and delete, with image upload
- Categories, Suppliers and Customers: full CRUD
- Sales: record a sale with several items, view it, edit its customer/notes, delete it

Extra features:

- User authentication: every page requires login; each sale records who served it
- Dashboard: today's and monthly revenue, 7-day revenue chart, top sellers, recent sales
- Low-stock alerts when a product reaches its reorder level
- Automatic stock control: selling reduces stock, deleting a sale restores it
- Stock validation: a sale cannot exceed the stock available
- Search, category filter and pagination on the product list
- Sales report by date range with CSV download
- Protected deletes: a category with products, or a product already sold, cannot be removed
- Responsive Bootstrap interface

## Technologies

Python, Django, SQLite, Bootstrap 5, Chart.js

## Database design

Category -> Product <- Supplier. Customer -> Sale -> SaleItem -> Product.

SaleItem.unit_price stores the price at the time of sale, so old sales never change
when product prices are edited.

## How to run

Requires Python 3.12 or newer. Open a terminal in the project folder (the one
containing manage.py), then follow these steps.

### 1. Create and activate a virtual environment

    python -m venv venv
    venv\Scripts\activate

On Linux or Mac, activate with: source venv/bin/activate

### 2. Install the dependencies

    pip install -r requirements.txt

### 3. Create the database tables

    python manage.py migrate

### 4. Create an administrator account

    python manage.py createsuperuser

### 5. (Optional) Load demo data so the dashboard has something to show

    python manage.py seed_demo

### 6. Start the server

    python manage.py runserver

Open http://127.0.0.1:8000/ and log in with the account from step 4.
More staff accounts can be added in the admin site at http://127.0.0.1:8000/admin/

## Screenshots

See the docs/screenshots folder.

## Author

KAKULE SAAMOYA BENEDICTION - 25/058BIT/JP/C
