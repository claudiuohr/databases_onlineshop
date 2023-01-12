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

@app.route('/update_customer',methods=['GET','POST'])
def handle_update_customer():
    id_client = request.form['id_client']
    membership = request.form['membership']
    nume = request.form['nume']
    prenume = request.form['prenume']
    adresa = request.form['adresa']
    adresa_email = request.form['adresa_email']
    nr_telefon = request.form['nr_telefon']
    conn = connect_to_database()
    cursor = conn.cursor()
    if membership != '':
        cursor.execute(f"""UPDATE client SET membership={membership} WHERE id_client={id_client}""")
    if nume != '':
        cursor.execute(f"""UPDATE detalii_client SET nume='{nume}' WHERE id_client={id_client}""")
    if prenume != '':
        cursor.execute(f"""UPDATE detalii_client SET prenume='{prenume}' WHERE id_client={id_client}""")
    if adresa != '':
        cursor.execute(f"""UPDATE detalii_client SET adresa='{adresa}' WHERE id_client={id_client}""")
    if adresa_email != '':
        cursor.execute(f"""UPDATE detalii_client SET adresa_email='{adresa_email}' WHERE id_client={id_client}""")    
    if nr_telefon != '':
        cursor.execute(f"""UPDATE detalii_client SET nr_telefon='{nr_telefon}' WHERE id_client={id_client}""")
    if membership != '' or nume != '' or prenume != '' or adresa != '' or adresa_email != '' or nr_telefon != '':
        cursor.execute("COMMIT")
    
    return redirect('/customers')

@app.route('/delete_customer',methods=['GET','POST'])
def handle_delete_customer():
    id_client = request.form['id_client']
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute(f"""DELETE FROM detalii_client WHERE id_client={id_client}""")
    cursor.execute(f"""DELETE FROM metoda_de_plata WHERE id_comanda IN (SELECT id_comanda FROM comanda WHERE id_client={id_client})""")
    cursor.execute(f"""DELETE FROM detalii_comanda WHERE id_comanda IN (SELECT id_comanda FROM comanda WHERE id_client={id_client})""")
    cursor.execute(f"""DELETE FROM comanda WHERE id_client={id_client}""")
    cursor.execute(f"""DELETE FROM client WHERE id_client={id_client}""")
    cursor.execute("COMMIT")
    return redirect('/customers')

@app.route('/products',methods=['GET'])
def handle_products():
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("""SELECT p.id_produs,p.denumire,p.pret,p.cantitate FROM produs p WHERE p.disponibilitate=1""")
    products = cursor.fetchall()
    return render_template('products.html',products=products)

@app.route('/add_product',methods=['GET','POST'])
def handle_add_product():
    denumire=request.form['denumire']
    pret=request.form['pret']
    cantitate=request.form['cantitate']
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute(""" INSERT INTO produs (denumire,pret,cantitate) VALUES (%s,%s,%s)""",(denumire,pret,cantitate))
    cursor.execute("COMMIT")
    return redirect('/products')

@app.route('/update_product',methods=['GET','POST'])
def handle_update_product():
    id_produs=request.form['id_produs']
    denumire=request.form['denumire']
    pret=request.form['pret']
    cantitate=request.form['cantitate']
    conn = connect_to_database()
    cursor = conn.cursor()
    if denumire != '':
        cursor.execute(""" UPDATE produs SET denumire=%s WHERE id_produs=%s""",(denumire,id_produs))
    if pret != '':
        cursor.execute(""" UPDATE produs SET pret=%s WHERE id_produs=%s""",(pret,id_produs))
    if cantitate != '':
        cursor.execute(""" UPDATE produs SET cantitate=%s WHERE id_produs=%s""",(cantitate,id_produs))
    if pret != '' or cantitate != '' or denumire != '':
        cursor.execute("COMMIT")
    return redirect('/products')

@app.route('/delete_product',methods=['GET','POST'])
def handle_delete_product():
    id_produs=request.form['id_produs']
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute(f"""UPDATE produs SET disponibilitate=0 WHERE id_produs={id_produs}""")
    cursor.execute("COMMIT")
    return redirect('/products')

@app.route('/add_to_cart',methods=['GET','POST'])
def handle_add_to_cart():
    id_produs=request.form['id_produs']
    cantitate=request.form['cantitate']
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO cos (id_produs,cantitate) VALUES (%s,%s)""",(id_produs,cantitate))
    cursor.execute("COMMIT")
    return redirect('/products')

@app.route('/cart',methods=['GET'])
def handle_cart():
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("""SELECT c.id_produs,p.denumire,p.pret,c.cantitate FROM produs p JOIN cos c ON p.id_produs=c.id_produs""")
    cart = cursor.fetchall()
    return render_template('cart.html',cart=cart)

@app.route('/modify_cart',methods=['GET','POST'])
def handle_modify_cart():
    id_produs=request.form['id_produs']
    cantitate=request.form['cantitate']
    conn = connect_to_database()
    cursor = conn.cursor()
    if cantitate != '':
        cursor.execute("""UPDATE cos SET cantitate=%s WHERE id_produs=%s""",(cantitate,id_produs))
    if cantitate == '0':
        cursor.execute(f"""DELETE FROM cos WHERE id_produs={id_produs}""")
    cursor.execute("COMMIT")
    return redirect('/cart')

@app.route('/empty_cart',methods=['GET','POST'])
def handle_empty_cart():
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("""DELETE FROM cos""")
    cursor.execute("COMMIT")
    return redirect('/cart')

@app.route('/purchase',methods=['GET','POST'])
def handle_purchase():
    id_client=request.form['id_client']
    metoda_plata=request.form['metoda_plata']
    adresa_livrare=request.form['adresa_livrare']
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("""SELECT id_produs,cantitate FROM cos""")
    cart = cursor.fetchall()
    cursor.execute("""INSERT INTO comanda (id_client,pret_total,metoda_plata,adresa_livrare,status) VALUES (%s,%s,%s,%s,%s)""",(id_client,0,metoda_plata,adresa_livrare,'in_curs_de_procesare'))
    cursor.execute("COMMIT")
    for product in cart:
        cursor.execute("""INSERT INTO detalii_comanda (id_comanda,id_produs,nr_prd) VALUES (LAST_INSERT_ID(),%s,%s)""",(product[0],product[1]))
        cursor.execute("COMMIT")
    cursor.execute("""DELETE FROM cos""")
    cursor.execute("COMMIT")
    return redirect('/cart')

@app.route('/orders',methods=['GET'])
def handle_orders():
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("""SELECT o.id_comanda,o.id_client,o.pret_total,o.metoda_plata,o.adresa_livrare,o.status FROM comanda o""")
    orders = cursor.fetchall()
    return render_template('orders.html',orders=orders)

@app.route('/delete_order',methods=['GET','POST'])
def handle_delete_order():
    id_comanda=request.form['id_comanda']
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute(f"""DELETE FROM detalii_comanda WHERE id_comanda={id_comanda}""")
    cursor.execute(f"""DELETE FROM comanda WHERE id_comanda={id_comanda}""")
    cursor.execute("COMMIT")
    return redirect('/orders')

@app.route('/details_order_btn',methods=['GET','POST'])
def handle_details_order_btn():
    id_comanda=request.form['id_comanda']
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("COMMIT")
    return redirect(f'/details_orders?id_comanda={id_comanda}')

@app.route('/details_orders',methods=['GET'])
def handle_details_order():
    id_comanda = request.args.get('id_comanda')
    if id_comanda:   
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute(f"""SELECT id_comanda,id_produs,nr_prd FROM detalii_comanda where id_comanda={id_comanda}""")
        details_orders = cursor.fetchall()
        return render_template('details_orders.html',details_orders=details_orders)
    else:
        return "No id_comanda provided"