from flask import Flask,render_template,request,redirect
from database_management import *

app=Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/create_tables',methods=['POST'])
def handle_create_tables():
    create_tables()
    return redirect('/')    


@app.route('/insert_data',methods=['POST'])
def handle_insert_data():
    insert_data()
    return redirect('/')    

@app.route('/delete_tables',methods=['POST'])
def handle_delete_tables():
    delete_tables()
    return redirect('/')

@app.route('/customers',methods=['GET'])
def handle_customers():
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("""SELECT d.id_client,d.nume,d.prenume,d.adresa,d.adresa_email,d.nr_telefon,c.membership 
    FROM client c JOIN detalii_client d ON d.id_client=c.id_client""")
    customers = cursor.fetchall()
    return render_template('customers.html',customers=customers)

@app.route('/add_customer',methods=['GET','POST'])
def handle_add_customer():
    membership = request.form['membership']
    nume = request.form['nume']
    prenume = request.form['prenume']
    adresa = request.form['adresa']
    adresa_email = request.form['adresa_email']
    nr_telefon = request.form['nr_telefon']
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute(f"""INSERT INTO client (membership) VALUES ({membership})""")
    cursor.execute("""INSERT INTO detalii_client (nume,prenume,adresa,adresa_email,nr_telefon,id_client) VALUES (%s,%s,%s,%s,%s, LAST_INSERT_ID())""",(nume,prenume,adresa,adresa_email,nr_telefon))
    cursor.execute("COMMIT")
    return redirect('/customers')

@app.route('/products',methods=['GET'])
def handle_products():
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("""SELECT p.id_produs,p.denumire,p.pret,p.disponibilitate FROM produs p""")
    products = cursor.fetchall()
    return render_template('products.html',products=products)

@app.route('/add_product',methods=['GET','POST'])
def handle_add_product():
    denumire=request.form['denumire']
    pret=request.form['pret']
    disponibilitate=request.form['disponibilitate']
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute(""" INSERT INTO produs (denumire,pret,disponibilitate) VALUES (%s,%s,%s)""",(denumire,pret,disponibilitate))
    cursor.execute("COMMIT")
    return redirect('/products')

@app.route('/update_product',methods=['GET','POST'])
def handle_update_product():
    id_produs=request.form['id_produs']
    pret=request.form['pret']
    disponibilitate=request.form['disponibilitate']
    conn = connect_to_database()
    cursor = conn.cursor()

    if pret != '':
        cursor.execute(""" UPDATE produs 
        SET pret=%s
        WHERE id_produs=%s""",(pret,id_produs))
    if disponibilitate != '':
        cursor.execute(""" UPDATE produs 
        SET disponibilitate=%s
        WHERE id_produs=%s""",(disponibilitate,id_produs))

    cursor.execute("COMMIT")
    return redirect('/products')

@app.route('/orders',methods=['GET'])
def handle_orders():
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("""SELECT o.id_comanda,o.id_client,d.id_produs,d.nr_prd,o.pret_total,o.adresa_livrare,o.status FROM comanda o JOIN detalii_comanda d ON o.id_comanda=d.id_comanda""")
    orders = cursor.fetchall()
    return render_template('orders.html',orders=orders)

@app.route('/add_order',methods=['GET','POST'])
def handle_add_order():
    id_client=request.form['id_client']
    id_produs=request.form['id_produs']
    nr_prd=request.form['nr_prd']
    adresa_livrare=request.form['adresa_livrare']
    status=request.form['status']
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO comanda (id_client,adresa_livrare,status) VALUES (%s,%s,%s)""",(id_client,adresa_livrare,status))
    cursor.execute("""INSERT INTO detalii_comanda (id_produs,nr_prd,id_comanda) VALUES (%s,%s,LAST_INSERT_ID())""",(id_produs,nr_prd))
    cursor.execute("COMMIT")
    return redirect('/orders')

@app.route('/paying_methods',methods=['GET'])
def handle_paying_methods():
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute('SELECT id_comanda,cash,card FROM metoda_de_plata')
    paying_methods = cursor.fetchall()
    return render_template('paying_methods.html',paying_methods=paying_methods)

@app.route('/add_paying_method',methods=['GET','POST'])
def handle_add_paying_method():
    id_comanda=request.form['id_comanda']
    cash=request.form['cash']
    card=request.form['card']
    conn = connect_to_database()
    cursor=conn.cursor()
    cursor.execute("""INSERT INTO metoda_de_plata (id_comanda,cash,card) VALUES (%s,%s,%s)""",(id_comanda,cash,card))
    cursor.execute("COMMIT")
    return redirect('/paying_methods')

@app.route('/update_paying_method',methods=['GET','POST'])
def handle_update_paying_method():
    id_comanda=request.form['id_comanda']
    cash=request.form['cash']
    card=request.form['card']
    conn = connect_to_database()
    cursor=conn.cursor()
    if cash != '' and card != '':
        cursor.execute("""UPDATE metoda_de_plata SET cash=%s,card=%s WHERE id_comanda=%s""",(cash,card,id_comanda))
    cursor.execute("COMMIT")
    return redirect('/paying_methods')