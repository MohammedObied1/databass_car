
from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = '478520'  


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",    
        user="root",        
        password="478520",
        database="project"   
    )


def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))  
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password1']

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s AND password1 = %s", (email, password))
        user = cursor.fetchone()
        cursor.close()
        connection.close()

        if user:
            session['user_id'] = user['user_id']
            session['email'] = user['email']
            session['sname'] = user['sname']
            session['role'] = user['role']  

            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))  
            elif user['role'] == 'employee':
                return redirect(url_for('employee_dashboard'))  
            elif user['role'] == 'customer':
                return redirect(url_for('user_page'))  
            else:
                return "Role not recognized, please contact support."
        else:
            return "Invalid email or password, please try again."
    session.clear()
    return render_template('login.html')



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password1']
        sname = request.form['sname']
        role = request.form['role'] 

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            return "Email already exists, please choose another one."

        cursor.execute("INSERT INTO users (email, password1, sname, role) VALUES (%s, %s, %s, %s)",
                       (email, password, sname, role))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('login'))

    return render_template('signup.html')













@app.route('/employee_dashboard')
def employee_dashboard():
    if 'role' not in session or session['role'] != 'employee':
        return redirect(url_for('login'))  
    return render_template('employee_dashboard.html')

@app.route('/employee')
def employee_redirect():
    return redirect(url_for('employee_dashboard.html'))



@app.route('/employee_view_reports', methods=['GET'])
def employee_view_reports():
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = "SELECT * FROM Reposts WHERE 1=1"
    params = []

    if start_date:
        query += " AND start_Date >= %s"
        params.append(start_date)
    if end_date:
        query += " AND end_date <= %s"
        params.append(end_date)

    cursor.execute(query, params)
    reports = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('employee_view_reports.html', reports=reports, start_date=start_date, end_date=end_date)




@app.route('/employee_view_payments', methods=['GET'])
def employee_view_payments():
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    method_filter = request.args.get('method', '')

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT 
            p.Payments_ID,
            p.adate,
            p.Amount,
            p.method,
            t.transaction_Type AS transaction_info, 
            b.Address AS branch_info
        FROM Payments p
        LEFT JOIN transaction1 t ON p.transaction_ID = t.transaction_ID
        LEFT JOIN Branch b ON p.Branch_ID = b.Branch_ID
        WHERE 1=1
    """
    params = []

    if start_date:
        query += " AND p.adate >= %s"
        params.append(start_date)
    if end_date:
        query += " AND p.adate <= %s"
        params.append(end_date)
    if method_filter:
        query += " AND p.method = %s"
        params.append(method_filter)

    cursor.execute(query, params)
    payments = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('employee_view_payments.html', payments=payments, start_date=start_date, end_date=end_date, method_filter=method_filter)


@app.route('/view_inventory', methods=['GET'])
def view_inventory():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT 
            ci.car_ID,
            ci.price,
            ci.model_year,
            ci.fuel_type,
            ci.color,
            ci.motor_size,
            ci.mator_infarmation,
            ci.modal,
            ci.make,
            ci.vin,
            b.Address AS branch_address
        FROM care_inventory ci
        LEFT JOIN Branch b ON ci.Branch_ID = b.Branch_ID
    """

    cursor.execute(query)
    inventory = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('view_inventory.html', inventory=inventory)





@app.route('/manage_centers', methods=['GET'])
def manage_centers():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Branch")
    branches = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('manage_centers.html', branches=branches)


@app.route('/add_center', methods=['GET', 'POST'])
def add_center():
    if request.method == 'POST':
        branch_id = request.form['branch_ID']
        address = request.form['address']
        company_id = request.form['company_ID']

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO Branch (Branch_ID, Address, company_ID) 
            VALUES (%s, %s, %s)
        """, (branch_id, address, company_id))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('manage_centers'))
    return render_template('add_center.html')


@app.route('/edit_center/<int:branch_id>', methods=['GET', 'POST'])
def edit_center(branch_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    if request.method == 'POST':
        address = request.form['address']
        company_id = request.form['company_ID']

        cursor.execute("""
            UPDATE Branch
            SET Address = %s, company_ID = %s
            WHERE Branch_ID = %s
        """, (address, company_id, branch_id))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('manage_centers'))

    cursor.execute("SELECT * FROM Branch WHERE Branch_ID = %s", (branch_id,))
    branch = cursor.fetchone()
    cursor.close()
    connection.close()

    return render_template('edit_center.html', branch=branch)


@app.route('/delete_center/<int:branch_id>')
def delete_center(branch_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM Branch WHERE Branch_ID = %s", (branch_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return redirect(url_for('manage_centers'))




@app.route('/employee_manage_suppliers', methods=['GET'])
def employee_manage_suppliers():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Supplier")
    suppliers = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('employee_manage_suppliers.html', suppliers=suppliers)


@app.route('/employee_add_supplier', methods=['GET', 'POST'])
def employee_add_supplier():
    if request.method == 'POST':
        supplier_id = request.form['supplier_id']
        sname = request.form['sname']
        phone_number = request.form['phone_number']
        address = request.form['address']
        rating = request.form['rating']
        car_id = request.form['car_id']

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO Supplier (supplier_id, sname, phone_number, address, rating, car_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (supplier_id, sname, phone_number, address, rating, car_id))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('employee_manage_suppliers'))
    return render_template('employee_add_supplier.html')


@app.route('/employee_edit_supplier/<int:supplier_id>', methods=['GET', 'POST'])
def employee_edit_supplier(supplier_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    if request.method == 'POST':
        sname = request.form['sname']
        phone_number = request.form['phone_number']
        address = request.form['address']
        rating = request.form['rating']
        car_id = request.form['car_id']

        cursor.execute("""
            UPDATE Supplier
            SET sname = %s, phone_number = %s, address = %s, rating = %s, car_id = %s
            WHERE supplier_id = %s
        """, (sname, phone_number, address, rating, car_id, supplier_id))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('employee_manage_suppliers'))

    cursor.execute("SELECT * FROM Supplier WHERE supplier_id = %s", (supplier_id,))
    supplier = cursor.fetchone()
    cursor.close()
    connection.close()

    return render_template('employee_edit_supplier.html', supplier=supplier)


@app.route('/employee_delete_supplier/<int:supplier_id>')
def employee_delete_supplier(supplier_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM Supplier WHERE supplier_id = %s", (supplier_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return redirect(url_for('employee_manage_suppliers'))



@app.route('/employee_manage_customers', methods=['GET'])
def employee_manage_customers():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Customer")
    customers = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('employee_manage_customers.html', customers=customers)


@app.route('/employee_add_customer', methods=['GET', 'POST'])
def employee_add_customer():
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        phone_number = request.form['phone_number']
        address = request.form['address']

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO Customer (sname, phone_number, address)
            VALUES (%s, %s, %s)
        """, (customer_name, phone_number, address))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('employee_manage_customers'))
    return render_template('employee_add_customer.html')


@app.route('/employee_edit_customer/<int:customer_id>', methods=['GET', 'POST'])
def employee_edit_customer(customer_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    if request.method == 'POST':
        customer_name = request.form['customer_name']
        phone_number = request.form['phone_number']
        address = request.form['address']

        cursor.execute("""
            UPDATE Customer
            SET sname = %s, phone_number = %s, address = %s
            WHERE customer_id = %s
        """, (customer_name, phone_number, address, customer_id))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('employee_manage_customers'))

    cursor.execute("SELECT * FROM Customer WHERE customer_id = %s", (customer_id,))
    customer = cursor.fetchone()
    cursor.close()
    connection.close()

    return render_template('employee_edit_customer.html', customer=customer)


@app.route('/employee_delete_customer/<int:customer_id>')
def employee_delete_customer(customer_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM Customer WHERE customer_id = %s", (customer_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return redirect(url_for('employee_manage_customers'))



@app.route('/employee_manage_orders', methods=['GET'])
def employee_manage_orders():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT o.orders_id, o.sname, o.phone_number, o.address, c.sname AS customer_name 
        FROM orders o 
        JOIN Customer c ON o.Customer_id = c.Customer_id
    """)
    orders = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('employee_manage_orders.html', orders=orders)


@app.route('/employee_add_order', methods=['GET', 'POST'])
def employee_add_order():
    if request.method == 'POST':
        order_name = request.form['order_name']
        phone_number = request.form['phone_number']
        address = request.form['address']
        customer_id = request.form['customer_id']

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO orders (sname, phone_number, address, Customer_id)
            VALUES (%s, %s, %s, %s)
        """, (order_name, phone_number, address, customer_id))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('employee_manage_orders'))

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT Customer_id, sname FROM Customer")
    customers = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('employee_add_order.html', customers=customers)


@app.route('/employee_edit_order/<int:order_id>', methods=['GET', 'POST'])
def employee_edit_order(order_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    if request.method == 'POST':
        order_name = request.form['order_name']
        phone_number = request.form['phone_number']
        address = request.form['address']
        customer_id = request.form['customer_id']

        cursor.execute("""
            UPDATE orders 
            SET sname = %s, phone_number = %s, address = %s, Customer_id = %s
            WHERE orders_id = %s
        """, (order_name, phone_number, address, customer_id, order_id))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('employee_manage_orders'))

    cursor.execute("SELECT * FROM orders WHERE orders_id = %s", (order_id,))
    order = cursor.fetchone()

    cursor.execute("SELECT Customer_id, sname FROM Customer")
    customers = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('employee_edit_order.html', order=order, customers=customers)


@app.route('/employee_delete_order/<int:order_id>')
def employee_delete_order(order_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM orders WHERE orders_id = %s", (order_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return redirect(url_for('employee_manage_orders'))









































@app.route('/user_page', methods=['GET', 'POST'])

def user_page():
    if 'role' not in session or session['role'] != 'customer':
        return redirect(url_for('login'))

    make_query = request.args.get('make', '')
    price_query = request.args.get('price', '')
    color_query = request.args.get('color', '')
    modal_query = request.args.get('modal', '')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = 'SELECT * FROM care_inventory WHERE 1=1'
    params = []

    if make_query:
        query += ' AND make LIKE %s'
        params.append('%' + make_query + '%')
    if price_query:
        query += ' AND price LIKE %s'
        params.append('%' + price_query + '%')
    if color_query:
        query += ' AND color LIKE %s'
        params.append('%' + color_query + '%')
    if modal_query:
        query += ' AND modal LIKE %s'
        params.append('%' + modal_query + '%')

    cursor.execute(query, params)
    cars = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('user.html', cars=cars,
                           make_query=make_query,
                           price_query=price_query,
                           color_query=color_query,
                           modal_query=modal_query)



@app.route('/order/<int:car_id>', methods=['GET', 'POST'])
def order_car(car_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        customer_name = request.form.get('customer_name')
        phone_number = request.form.get('phone_number')
        address = request.form.get('address')

        if not customer_name or not phone_number or not address:
            return redirect(url_for('car_details', car_id=car_id, message="Please fill out all customer details."))

        cursor.execute('SELECT Customer_id FROM Customer WHERE sname = %s AND phone_Number = %s AND address = %s',
                       (customer_name, phone_number, address))
        customer = cursor.fetchone()

        if cursor.rowcount > 0:
            cursor.fetchall()

        if not customer:
            cursor.execute(''' 
                INSERT INTO Customer (sname, phone_Number, address) 
                VALUES (%s, %s, %s)
            ''', (customer_name, phone_number, address))
            conn.commit()
            customer_id = cursor.lastrowid
        else:
            customer_id = customer['Customer_id']

        cursor.execute(''' 
            INSERT INTO orders (sname, phone_Number, address, Customer_id) 
            VALUES (%s, %s, %s, %s)
        ''', (customer_name, phone_number, address, customer_id))
        conn.commit()
        order_id = cursor.lastrowid

        cursor.execute(''' 
            INSERT INTO order_car (orders_id, car_ID) 
            VALUES (%s, %s)
        ''', (order_id, car_id))
        conn.commit()

        cursor.execute(''' 
            UPDATE care_inventory 
            SET orders_id = %s 
            WHERE car_ID = %s
        ''', (order_id, car_id))
        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for('car_details', car_id=car_id, message="Order placed successfully!"))

    cursor.execute('SELECT make, modal FROM care_inventory WHERE car_ID = %s', (car_id,))
    car = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template('register_order.html', car=car)






@app.route('/car_details/<int:car_id>')
def car_details(car_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT * FROM care_inventory WHERE car_id = %s', (car_id,))
    car = cursor.fetchone()

    cursor.close()
    conn.close()

    message = request.args.get('message')

    return render_template('car_details.html', car=car, message=message)




@app.route('/admin_dashboard')
def admin_dashboard():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    return render_template('tables.html')

@app.route('/tables')
def tables():
    return render_template('tables.html')

@app.route('/add_company', methods=['GET', 'POST'])
def add_company():
    if request.method == 'POST':
        company_ID = request.form['company_ID']
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO company (company_ID) VALUES (%s)", (company_ID,))
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for('companies'))
    return render_template('add_company.html')

@app.route('/delete_company/<int:company_id>')
def delete_company(company_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM company WHERE company_ID = %s", (company_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return redirect(url_for('companies'))

@app.route('/edit_company/<int:company_id>', methods=['GET', 'POST'])
def edit_company(company_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    if request.method == 'POST':
        company_ID = request.form['company_ID']  
        cursor.execute("UPDATE company SET company_ID = %s WHERE company_ID = %s", (company_ID, company_id))
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for('companies')) 

    cursor.execute("SELECT * FROM company WHERE company_ID = %s", (company_id,))
    company = cursor.fetchone()
    cursor.close()
    connection.close()

    return render_template('update_company.html', company=company)

@app.route('/companies')
def companies():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM company")
    companies = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('companies.html', companies=companies)

@app.route('/reposts', methods=['GET', 'POST'])
def reposts():
    connection = get_db_connection()
    cursor = connection.cursor()

    start_date_filter = request.args.get('start_date', '')
    end_date_filter = request.args.get('end_date', '')
    company_id_filter = request.args.get('company_id', '')

    query = "SELECT * FROM Reposts WHERE 1=1"
    total_sales_query = "SELECT SUM(total_sales) FROM Reposts WHERE 1=1"
    params = []

    if start_date_filter:
        query += " AND start_Date >= %s"
        total_sales_query += " AND start_Date >= %s"
        params.append(start_date_filter)

    if end_date_filter:
        query += " AND end_date <= %s"
        total_sales_query += " AND end_date <= %s"
        params.append(end_date_filter)

    if company_id_filter:
        query += " AND company_ID = %s"
        total_sales_query += " AND company_ID = %s"
        params.append(company_id_filter)

    cursor.execute(query, params)
    reposts = cursor.fetchall()

    cursor.execute(total_sales_query, params)
    total_sales = cursor.fetchone()[0]
    total_sales = total_sales if total_sales is not None else 0  

    cursor.close()
    connection.close()

    return render_template(
        'reposts.html',
        reposts=reposts,
        start_date_filter=start_date_filter,
        end_date_filter=end_date_filter,
        company_id_filter=company_id_filter,
        total_sales=total_sales
    )

@app.route('/add_repost', methods=['GET', 'POST'])
def add_repost():
    if request.method == 'POST':
        report_ID = request.form['report_ID']
        start_Date = request.form['start_Date']
        end_Date = request.form['end_Date']
        total_sales = request.form['total_sales']
        company_ID = request.form['company_ID']

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO Reposts (Report_ID, start_Date, end_date, total_sales, company_ID)
            VALUES (%s, %s, %s, %s, %s)
        """, (report_ID, start_Date, end_Date, total_sales, company_ID))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('reposts')) 
    return render_template('add_repost.html')


@app.route('/edit_repost/<int:report_id>', methods=['GET', 'POST'])
def edit_repost(report_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    if request.method == 'POST':
        report_ID = request.form['report_ID']
        start_Date = request.form['start_Date']
        end_Date = request.form['end_Date']
        total_sales = request.form['total_sales']
        company_ID = request.form['company_ID']

        cursor.execute("""
            UPDATE Reposts
            SET Report_ID = %s, start_Date = %s, end_date = %s, total_sales = %s, company_ID = %s
            WHERE Report_ID = %s
        """, (report_ID, start_Date, end_Date, total_sales, company_ID, report_id))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('reposts')) 

    cursor.execute("SELECT * FROM Reposts WHERE Report_ID = %s", (report_id,))
    repost = cursor.fetchone()
    cursor.close()
    connection.close()

    return render_template('edit_repost.html', repost=repost)

@app.route('/delete_repost/<int:report_id>')
def delete_repost(report_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM Reposts WHERE Report_ID = %s", (report_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return redirect(url_for('reposts'))

@app.route('/Branch')
def branch():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Branch")
    branches = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('branch.html', branches=branches)

@app.route('/add_branch', methods=['GET', 'POST'])
def add_branch():
    if request.method == 'POST':
        branch_id = request.form['branch_ID']
        address = request.form['address']
        company_id = request.form['company_ID']

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO Branch (Branch_ID, Address, company_ID) 
            VALUES (%s, %s, %s)
        """, (branch_id, address, company_id))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('branch'))
    return render_template('add_branch.html')

@app.route('/edit_branch/<int:branch_id>', methods=['GET', 'POST'])
def edit_branch(branch_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    if request.method == 'POST':
        address = request.form['address']
        company_id = request.form['company_ID']

        cursor.execute("""
            UPDATE Branch
            SET Address = %s, company_ID = %s
            WHERE Branch_ID = %s
        """, (address, company_id, branch_id))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('branch'))

    cursor.execute("SELECT * FROM Branch WHERE Branch_ID = %s", (branch_id,))
    branch = cursor.fetchone()
    cursor.close()
    connection.close()

    return render_template('edit_branch.html', branch=branch)

@app.route('/delete_branch/<int:branch_id>')
def delete_branch(branch_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM Branch WHERE Branch_ID = %s", (branch_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return redirect(url_for('branch'))

@app.route('/Employea')
def employea():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Employea")
    employees = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('employea.html', employees=employees)

@app.route('/add_employea', methods=['GET', 'POST'])
def add_employea():
    if request.method == 'POST':
        employea_id = request.form['Employea_ID']
        sname = request.form['sname']
        address = request.form['Address']
        phone_number = request.form['phone_Number']
        srole = request.form['sRole']
        salary = request.form['Salary']
        branch_id = request.form['Branch_ID']

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO Employea (Employea_ID, sname, Address, phone_Number, sRole, Salary, Branch_ID) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (employea_id, sname, address, phone_number, srole, salary, branch_id))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('employea'))
    return render_template('add_employea.html')

@app.route('/edit_employea/<int:employea_id>', methods=['GET', 'POST'])
def edit_employea(employea_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    if request.method == 'POST':
        sname = request.form['sname']
        address = request.form['Address']
        phone_number = request.form['phone_Number']
        srole = request.form['sRole']
        salary = request.form['Salary']
        branch_id = request.form['Branch_ID']

        cursor.execute("""
            UPDATE Employea
            SET sname = %s, Address = %s, phone_Number = %s, sRole = %s, Salary = %s, Branch_ID = %s
            WHERE Employea_ID = %s
        """, (sname, address, phone_number, srole, salary, branch_id, employea_id))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('employea'))

    cursor.execute("SELECT * FROM Employea WHERE Employea_ID = %s", (employea_id,))
    employea = cursor.fetchone()
    cursor.close()
    connection.close()

    return render_template('edit_employea.html', employea=employea)

@app.route('/delete_employea/<int:employea_id>')
def delete_employea(employea_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM Employea WHERE Employea_ID = %s", (employea_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return redirect(url_for('employea'))

@app.route('/Payments')
def payments():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Payments")
    payments = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('payments.html', payments=payments)

@app.route('/add_payment', methods=['GET', 'POST'])
def add_payment():
    if request.method == 'POST':
        payment_id = request.form['Payments_ID']
        adate = request.form['adate']
        amount = request.form['Amount']
        method = request.form['method']
        transaction_id = request.form['transaction_ID']
        branch_id = request.form['Branch_ID']

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO Payments (Payments_ID, adate, Amount, method, transaction_ID, Branch_ID)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (payment_id, adate, amount, method, transaction_id, branch_id))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('payments'))
    return render_template('add_payment.html')

@app.route('/edit_payment/<int:payment_id>', methods=['GET', 'POST'])
def edit_payment(payment_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    if request.method == 'POST':
        adate = request.form['adate']
        amount = request.form['Amount']
        method = request.form['method']
        transaction_id = request.form['transaction_ID']
        branch_id = request.form['Branch_ID']

        cursor.execute("""
            UPDATE Payments
            SET adate = %s, Amount = %s, method = %s, transaction_ID = %s, Branch_ID = %s
            WHERE Payments_ID = %s
        """, (adate, amount, method, transaction_id, branch_id, payment_id))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('payments'))

    cursor.execute("SELECT * FROM Payments WHERE Payments_ID = %s", (payment_id,))
    payment = cursor.fetchone()
    cursor.close()
    connection.close()

    return render_template('edit_payment.html', payment=payment)

@app.route('/delete_payment/<int:payment_id>')
def delete_payment(payment_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM Payments WHERE Payments_ID = %s", (payment_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return redirect(url_for('payments'))


@app.route('/care_inventory')
def care_inventory():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM care_inventory")
    inventory = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('care_inventory.html', inventory=inventory)


@app.route('/add_car_inventory', methods=['GET', 'POST'])
def add_car_inventory():
    if request.method == 'POST':
        car_id = request.form['car_ID']
        price = request.form['price']
        model_year = request.form['model_year']
        fuel_type = request.form['fuel_type']
        color = request.form['color']
        motor_size = request.form['motor_size']
        motor_information = request.form['mator_infarmation']
        model = request.form['modal']
        make = request.form['make']
        vin = request.form['vin']
        branch_id = request.form['Branch_ID']

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO care_inventory (car_ID, price, model_year, fuel_type, color, motor_size, mator_infarmation, modal, make, vin, Branch_ID)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (car_id, price, model_year, fuel_type, color, motor_size, motor_information, model, make, vin, branch_id))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('care_inventory'))
    return render_template('add_car_inventory.html')


@app.route('/edit_car_inventory/<int:car_id>', methods=['GET', 'POST'])
def edit_car_inventory(car_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    if request.method == 'POST':
        price = request.form['price']
        model_year = request.form['model_year']
        fuel_type = request.form['fuel_type']
        color = request.form['color']
        motor_size = request.form['motor_size']
        motor_information = request.form['mator_infarmation']
        model = request.form['modal']
        make = request.form['make']
        vin = request.form['vin']
        branch_id = request.form['Branch_ID']
        orders_id = request.form['orders_id'] 

        cursor.execute("""
            UPDATE care_inventory
            SET price = %s, model_year = %s, fuel_type = %s, color = %s, motor_size = %s, mator_infarmation = %s, modal = %s, make = %s, vin = %s, Branch_ID = %s, orders_id = %s
            WHERE car_ID = %s
        """, (price, model_year, fuel_type, color, motor_size, motor_information, model, make, vin, branch_id, orders_id, car_id))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('care_inventory'))

    cursor.execute("SELECT * FROM care_inventory WHERE car_ID = %s", (car_id,))
    car = cursor.fetchone()
    cursor.close()
    connection.close()

    return render_template('edit_car_inventory.html', car=car)

@app.route('/delete_car_inventory/<int:car_id>')
def delete_car_inventory(car_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM care_inventory WHERE car_ID = %s", (car_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return redirect(url_for('care_inventory'))


@app.route('/supplier', methods=['GET'])
def supplier():
    name_filter = request.args.get('name', '').strip()
    rating_filter = request.args.get('rating', '').strip()

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = "SELECT * FROM supplier WHERE 1=1"
    params = []

    if name_filter:
        query += " AND sname LIKE %s"
        params.append(f"%{name_filter}%")

    if rating_filter:
        query += " AND Rating = %s"
        params.append(rating_filter)

    cursor.execute(query, params)
    suppliers = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        'supplier.html', 
        suppliers=suppliers, 
        name_filter=name_filter, 
        rating_filter=rating_filter
    )


@app.route('/add_supplier', methods=['GET', 'POST'])
def add_supplier():
    if request.method == 'POST':
        supplier_id = request.form['supplier_id']
        sname = request.form['sname']
        phone_number = request.form['phone_Number']
        address = request.form['Address']
        rating = request.form['Rating']
        car_id = request.form['car_ID']

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO supplier (supplier_id, sname, phone_Number, Address, Rating, car_ID)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (supplier_id, sname, phone_number, address, rating, car_id))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('supplier'))
    return render_template('add_supplier.html')

@app.route('/edit_supplier/<int:supplier_id>', methods=['GET', 'POST'])
def edit_supplier(supplier_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    if request.method == 'POST':
        sname = request.form['sname']
        phone_number = request.form['phone_Number']
        address = request.form['Address']
        rating = request.form['Rating']
        car_id = request.form['car_ID']

        cursor.execute("""
            UPDATE supplier
            SET sname = %s, phone_Number = %s, Address = %s, Rating = %s, car_ID = %s
            WHERE supplier_id = %s
        """, (sname, phone_number, address, rating, car_id, supplier_id))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('supplier'))

    cursor.execute("SELECT * FROM supplier WHERE supplier_id = %s", (supplier_id,))
    supplier = cursor.fetchone()
    cursor.close()
    connection.close()

    return render_template('edit_supplier.html', supplier=supplier)

@app.route('/delete_supplier/<int:supplier_id>')
def delete_supplier(supplier_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM supplier WHERE supplier_id = %s", (supplier_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return redirect(url_for('supplier'))

@app.route('/Customer', methods=['GET'])
def customer():
    connection = get_db_connection()
    cursor = connection.cursor()

    name_filter = request.args.get('name', '').strip()
    phone_filter = request.args.get('phone', '').strip()
    address_filter = request.args.get('address', '').strip()

    query = "SELECT * FROM Customer WHERE 1=1"
    params = []

    if name_filter:
        query += " AND sname LIKE %s"
        params.append(f"%{name_filter}%")
    if phone_filter:
        query += " AND phone_Number LIKE %s"
        params.append(f"%{phone_filter}%")
    if address_filter:
        query += " AND address LIKE %s"
        params.append(f"%{address_filter}%")

    cursor.execute(query, params)
    customers = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('customer.html', customers=customers, name_filter=name_filter, phone_filter=phone_filter, address_filter=address_filter)


@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        sname = request.form['sname']
        phone_number = request.form['phone_Number']
        address = request.form['address']

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO Customer (Customer_id, sname, phone_Number, address)
            VALUES (%s, %s, %s, %s)
        """, (customer_id, sname, phone_number, address))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('customer'))
    return render_template('add_customer.html')

@app.route('/edit_customer/<int:customer_id>', methods=['GET', 'POST'])
def edit_customer(customer_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    if request.method == 'POST':
        sname = request.form['sname']
        phone_number = request.form['phone_Number']
        address = request.form['address']

        cursor.execute("""
            UPDATE Customer
            SET sname = %s, phone_Number = %s, address = %s
            WHERE Customer_id = %s
        """, (sname, phone_number, address, customer_id))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('customer'))

    cursor.execute("SELECT * FROM Customer WHERE Customer_id = %s", (customer_id,))
    customer = cursor.fetchone()
    cursor.close()
    connection.close()

    return render_template('edit_customer.html', customer=customer)

@app.route('/delete_customer/<int:customer_id>')
def delete_customer(customer_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM Customer WHERE Customer_id = %s", (customer_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return redirect(url_for('customer'))



@app.route('/transaction1')
def transaction():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM transaction1")
    transactions = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('transaction1.html', transactions=transactions)

@app.route('/add_transaction', methods=['GET', 'POST'])
def add_transaction():
    if request.method == 'POST':
        try:
            transaction_id = request.form['transaction_ID']
            car_id = request.form['car_ID']
            customer_id = request.form['customar_ID']
            supplier_id = request.form['supplier_ID']
            transaction_type = request.form['transaction_Type']
            amount = request.form['Amount']
            company_id = request.form['company_ID']

            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute("""
                INSERT INTO transaction1 (transaction_ID, car_ID, customar_ID, supplier_ID, transaction_Type, Amount, company_ID)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (transaction_id, car_id, customer_id, supplier_id, transaction_type, amount, company_id))

            connection.commit()

        except Exception as e:
            connection.rollback()
            return f"An error occurred: {str(e)}"

        finally:
            cursor.close()
            connection.close()

        return redirect(url_for('transaction'))

    return render_template('add_transaction.html')


@app.route('/edit_transaction/<int:transaction_id>', methods=['GET', 'POST'])
def edit_transaction(transaction_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    if request.method == 'POST':
        car_id = request.form['car_ID']
        customer_id = request.form['customar_ID']
        supplier_id = request.form['supplier_ID']
        transaction_type = request.form['transaction_Type']
        amount = request.form['Amount']
        company_id = request.form['company_ID']

        cursor.execute("""
            UPDATE transaction1
            SET car_ID = %s, customar_ID = %s, supplier_ID = %s, transaction_Type = %s, Amount = %s, company_ID = %s
            WHERE transaction_ID = %s
        """, (car_id, customer_id, supplier_id, transaction_type, amount, company_id, transaction_id))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('transaction'))

    cursor.execute("SELECT * FROM transaction1 WHERE transaction_ID = %s", (transaction_id,))
    transaction = cursor.fetchone()
    cursor.close()
    connection.close()

    return render_template('edit_transaction.html', transaction=transaction)

@app.route('/delete_transaction/<int:transaction_id>')
def delete_transaction(transaction_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM transaction1 WHERE transaction_ID = %s", (transaction_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return redirect(url_for('transaction'))


@app.route('/orders')
def orders():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('orders.html', orders=orders)


@app.route('/delete_order/<int:order_id>', methods=['GET'])
def delete_order(order_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM orders WHERE orders_id = %s", (order_id,))
    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for('orders'))




@app.route('/edit_order/<int:order_id>', methods=['GET', 'POST'])
def edit_order(order_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == 'POST':
        sname = request.form['sname']
        phone_number = request.form['phone_Number']
        address = request.form['address']
        customer_id = request.form['Customer_id']

        cursor.execute("""
            UPDATE orders 
            SET sname = %s, phone_Number = %s, address = %s, Customer_id = %s
            WHERE orders_id = %s
        """, (sname, phone_number, address, customer_id, order_id))

        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('orders')) 

    cursor.execute("SELECT * FROM orders WHERE orders_id = %s", (order_id,))
    order = cursor.fetchone()
    cursor.close()
    connection.close()

    return render_template('edit_order.html', order=order)






@app.route('/orders_summary', methods=['GET'])
def orders_summary():
    connection = get_db_connection()  
    cursor = connection.cursor()

    customer_name = request.args.get('customer_name', '').strip()
    phone_number = request.args.get('phone_number', '').strip()
    address = request.args.get('address', '').strip()

    query = """
        SELECT o.orders_id, o.sname, o.phone_Number, o.address, SUM(ci.price) AS total_amount
        FROM orders o
        JOIN order_car oc ON o.orders_id = oc.orders_id
        JOIN care_inventory ci ON oc.car_ID = ci.car_ID
        WHERE 1=1
    """
    params = []

    if customer_name:
        query += " AND o.sname LIKE %s"
        params.append(f"%{customer_name}%")
    if phone_number:
        query += " AND o.phone_Number LIKE %s"
        params.append(f"%{phone_number}%")
    if address:
        query += " AND o.address LIKE %s"
        params.append(f"%{address}%")

    query += " GROUP BY o.orders_id, o.sname, o.phone_Number, o.address"
    cursor.execute(query, params)
    total_paid_per_order = cursor.fetchall()

    cursor.execute("""
        SELECT ci.make, ci.modal, COUNT(*) AS order_count
        FROM order_car oc
        JOIN care_inventory ci ON oc.car_ID = ci.car_ID
        GROUP BY ci.make, ci.modal
        ORDER BY order_count DESC
        LIMIT 1
    """)
    most_ordered = cursor.fetchone()

    cursor.execute("""
        SELECT o.orders_id, SUM(ci.price) AS total_paid
        FROM orders o
        JOIN order_car oc ON o.orders_id = oc.orders_id
        JOIN care_inventory ci ON oc.car_ID = ci.car_ID
        GROUP BY o.orders_id
    """)
    total_payment_per_order = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('orders_summary.html', 
                           total_paid_per_order=total_paid_per_order,
                           most_ordered=most_ordered,
                           total_payment_per_order=total_payment_per_order,
                           customer_name=customer_name,
                           phone_number=phone_number,
                           address=address)





@app.route('/order_details/<int:order_id>')
def order_details(order_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT o.orders_id, o.sname, o.phone_Number, o.address, 
               CONCAT(ci.make, ' ', ci.modal) AS car_name, 
               ci.price, ci.color, ci.fuel_type, ci.model_year
        FROM orders o
        JOIN order_car oc ON o.orders_id = oc.orders_id
        JOIN care_inventory ci ON oc.car_ID = ci.car_ID
        WHERE o.orders_id = %s
    """, (order_id,))
    order_details = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('order_details.html', order_details=order_details)





if __name__ == "__main__":
    app.run(debug=True)






















