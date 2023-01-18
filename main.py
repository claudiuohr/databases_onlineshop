from flask import Flask,render_template,request,redirect
from database_management import *

app=Flask(__name__)


id_comanda_details = None

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

    if membership != '':
        cursor.execute(f"""INSERT INTO client (membership) VALUES ({membership})""")
    else:
        cursor.execute(f"""INSERT INTO client (membership) VALUES (DEFAULT)""")

    if nume == '' or prenume == '' or adresa_email == '' or nr_telefon == '':
        return "Nu ati completat toate campurile obligatorii!"

    cursor.execute(f"""SELECT id_client FROM detalii_client WHERE adresa_email='{adresa_email}'""")
    id_client = cursor.fetchone()
    if id_client != None:
        return "Exista deja un client cu aceasta adresa de email!"

    cursor.execute(f"""SELECT id_client FROM detalii_client WHERE nr_telefon='{nr_telefon}'""")
    id_client = cursor.fetchone()
    if id_client != None:
        return "Exista deja un client cu acest numar de telefon!"
    
    cursor.execute("""INSERT INTO detalii_client (nume,prenume,adresa,adresa_email,nr_telefon,id_client) VALUES 
    (%s,%s,%s,%s,%s, LAST_INSERT_ID())""",(nume,prenume,adresa,adresa_email,nr_telefon))
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
    if id_client == '':
        return "Pentru a actualiza un client trebuie sa introduceti un id!"
    cursor.execute(f"""SELECT id_client FROM client WHERE id_client={id_client}""")
    id_client_real = cursor.fetchone()
    if id_client_real == None:
        return "Pentru a actualiza un client trebuie sa introduceti un id valid!"
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
    else:
        return "Nu ati introdus niciun camp pentru a actualiza!"
    return redirect('/customers')

@app.route('/delete_customer',methods=['GET','POST'])
def handle_delete_customer():
    id_client = request.form['id_client']
    conn = connect_to_database()
    cursor = conn.cursor()
    if id_client == '':
        return "Pentru a actualiza un client trebuie sa introduceti un id!"
    cursor.execute(f"""SELECT id_client FROM client WHERE id_client={id_client}""")
    id_client_real = cursor.fetchone()
    if id_client_real == None:
        return "Pentru a actualiza un client trebuie sa introduceti un id valid!"
    cursor.execute(f"""DELETE FROM detalii_client WHERE id_client={id_client}""")
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
    if denumire == '' or pret == '' or cantitate == '':
        return "Nu ati completat toate campurile obligatorii!"
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
    if id_produs == '':
        return "Nu ati niciun id pentru a actualiza un produs!"
    cursor.execute(f"""SELECT id_produs FROM produs WHERE id_produs={id_produs} and disponibilitate=1""")
    if cursor.fetchone() is None:
        return "Nu exista produsul cu acest id!"
    if denumire != '':
        cursor.execute(""" UPDATE produs SET denumire=%s WHERE id_produs=%s""",(denumire,id_produs))
    if pret != '':
        cursor.execute(""" UPDATE produs SET pret=%s WHERE id_produs=%s""",(pret,id_produs))
    if cantitate != '':
        cursor.execute(""" UPDATE produs SET cantitate=%s WHERE id_produs=%s""",(cantitate,id_produs))
    if pret == '' and cantitate == '' and denumire == '':
        return "Nu ati introdus niciun camp pentru a actualiza!"    
    cursor.execute("COMMIT")
    return redirect('/products')

@app.route('/delete_product',methods=['GET','POST'])
def handle_delete_product():
    id_produs=request.form['id_produs']
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute(f"""SELECT id_produs FROM produs WHERE id_produs={id_produs} and disponibilitate=1""")
    if cursor.fetchone() is None:
        return "Nu exista produsul cu acest id!"
    cursor.execute(f"""UPDATE produs SET disponibilitate=0 WHERE id_produs={id_produs}""")
    cursor.execute("COMMIT")
    return redirect('/products')

@app.route('/add_to_order',methods=['GET','POST'])
def handle_add_to_order():
    id_comanda=request.form['id_comanda']
    id_produs=request.form['id_produs']
    nr_prd=request.form['cantitate']
    conn = connect_to_database()
    cursor = conn.cursor()
    if id_produs == '' or nr_prd == '' or id_comanda == '':
        return "Nu ati completat toate campurile obligatorii!"
    cursor.execute(f"""select id_produs from produs where id_produs={id_produs} and disponibilitate=1""")
    if cursor.fetchone() is None:
        return "Produsul nu exista!"
    cursor.execute(f"""select id_comanda from comanda where id_comanda={id_comanda}""")
    if cursor.fetchone() is None:
        return "Comanda nu exista!"
    if int(nr_prd) <= 0:
        return "Cantitatea trebuie sa fie mai mare decat 0!"
    cursor.execute(""" select id_produs from detalii_comanda where id_produs=%s and id_comanda=%s""",(id_produs,id_comanda))
    id_produs_in_comanda = cursor.fetchone()
    cursor.execute(f"""select pret from produs where id_produs={id_produs}""")
    pret = cursor.fetchone()[0]
    if id_produs_in_comanda != None:
        cursor.execute("""select nr_prd from detalii_comanda where id_produs=%s and id_comanda=%s""",(id_produs,id_comanda))
        nr_prd_adaugat = cursor.fetchone()[0]
        nr_prd = int(nr_prd) + int(nr_prd_adaugat)
        cursor.execute("""UPDATE detalii_comanda SET nr_prd=%s,pret_la_unitate=%s WHERE id_produs=%s and id_comanda=%s""",(nr_prd,pret,id_produs,id_comanda))
    else:
        cursor.execute("""INSERT INTO detalii_comanda (id_produs,nr_prd,id_comanda,pret_la_unitate) VALUES (%s,%s,%s,%s)""",(id_produs,nr_prd,id_comanda,pret))
    
    cursor.execute("""select id_produs,pret from produs p """)
    produs_nou=cursor.fetchall()
    cursor.execute(f"""select id_produs from detalii_comanda where id_comanda={id_comanda}""")
    produse_comanda=cursor.fetchall()
    for j in produse_comanda:
        for i in produs_nou:
            if i[0] == j[0]:
                cursor.execute("""UPDATE detalii_comanda SET pret_la_unitate=%s WHERE id_produs=%s and id_comanda=%s""",(i[1],i[0],id_comanda))
    cursor.execute("COMMIT")
    return redirect('/products')

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
    if id_comanda == '':
        return "Nu ati introdus id-ul comenzii!"
    cursor.execute(f"""SELECT id_comanda FROM comanda WHERE id_comanda={id_comanda}""")
    if cursor.fetchone() is None:
        return "Nu exista comanda cu acest id!"
    cursor.execute(f"""DELETE FROM detalii_comanda WHERE id_comanda={id_comanda}""")
    cursor.execute(f"""DELETE FROM comanda WHERE id_comanda={id_comanda}""")
    cursor.execute("COMMIT")
    return redirect('/orders')

@app.route('/add_order',methods=['GET','POST'])
def handle_add_order():
    id_client=request.form['id_client']
    metoda_plata=request.form['metoda_plata']
    adresa_livrare=request.form['adresa_livrare']
    conn = connect_to_database()
    cursor = conn.cursor()
    if id_client == '' or adresa_livrare == '':
        return "Nu ati introdus toate datele necesare!"
    cursor.execute("""INSERT INTO comanda (id_client,pret_total,metoda_plata,adresa_livrare,status) VALUES (%s,%s,%s,%s,%s)""",(id_client,0,metoda_plata,adresa_livrare,'in_curs_de_procesare'))
    cursor.execute("COMMIT")
    return redirect('/orders')

@app.route('/modify_order',methods=['GET','POST'])
def handle_modify_order():
    global id_comanda_details
    metoda_plata=request.form['metoda_plata']
    adresa_livrare=request.form['adresa_livrare']
    status=request.form['status']
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute(f"""SELECT id_comanda FROM comanda WHERE id_comanda={id_comanda_details}""")
    if cursor.fetchone() == None:
        return "Nu exista o comanda cu acest id!"
    if metoda_plata == '' and adresa_livrare == '' and status == '':
        return "Nu ati introdus nici o modificare!"
    if metoda_plata != '':
        cursor.execute("""UPDATE comanda SET metoda_plata=%s WHERE id_comanda=%s""",(metoda_plata,id_comanda_details))
    if adresa_livrare != '':
        cursor.execute("""UPDATE comanda SET adresa_livrare=%s WHERE id_comanda=%s""",(adresa_livrare,id_comanda_details))
    if status != '':
        cursor.execute("""UPDATE comanda SET status=%s WHERE id_comanda=%s""",(status,id_comanda_details))
    cursor.execute("COMMIT")
    return redirect('/details_orders')

@app.route('/modify_quantity',methods=['GET','POST'])
def handle_modify_quantity():
    global id_comanda_details
    id_produs=request.form['id_produs']
    nr_prd=request.form['nr_prd']
    conn = connect_to_database()
    cursor = conn.cursor()
    if id_comanda_details == '':
        return "Nu ati selectat o comanda!"
    cursor.execute("""SELECT id_produs FROM detalii_comanda WHERE id_produs=%s and id_comanda=%s""",(id_produs,id_comanda_details))
    if cursor.fetchone() == None:
        return "Nu exista un produs cu acest id in aceasta comanda!"
    if nr_prd == '':
        return "Nu ati introdus nici o modificare!"
    cursor.execute("""select id_produs,pret from produs p """)
    produs_nou=cursor.fetchall()
    cursor.execute(f"""select id_produs from detalii_comanda where id_comanda={id_comanda_details}""")
    produse_comanda=cursor.fetchall()
    for j in produse_comanda:
        for i in produs_nou:
            if i[0] == j[0]:
                cursor.execute("""UPDATE detalii_comanda SET pret_la_unitate=%s WHERE id_produs=%s and id_comanda=%s""",(i[1],i[0],id_comanda_details))
    cursor.execute("""UPDATE detalii_comanda SET nr_prd=%s WHERE id_comanda=%s AND id_produs=%s""",(nr_prd,id_comanda_details,id_produs))
    cursor.execute("COMMIT")
    return redirect('/details_orders')

@app.route('/details_order_btn',methods=['GET','POST'])
def handle_details_order_btn():
    global id_comanda_details
    id_comanda_details=request.form['id_comanda']
    conn = connect_to_database()
    cursor = conn.cursor()
    if id_comanda_details == '':
        return "Nu ati introdus toate datele necesare!"
    cursor.execute(f"""select id_comanda from comanda where id_comanda={id_comanda_details}""")
    if cursor.fetchone() == None :
        return "Nu exista o comanda cu acest id!"
    cursor.execute("COMMIT")
    return redirect(f'/details_orders')

@app.route('/details_orders',methods=['GET'])
def handle_details_order():
    global id_comanda_details
    if id_comanda_details:   
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute(f"""SELECT d.id_comanda,d.id_produs,p.denumire,d.nr_prd,d.pret_la_unitate FROM detalii_comanda d join produs p on d.id_produs=p.id_produs 
        where id_comanda={id_comanda_details}""")
        details_orders = cursor.fetchall()
        cursor.execute(f"""SELECT * from comanda where id_comanda={id_comanda_details}""")
        details = cursor.fetchall()
        return render_template('details_orders.html',details_orders=details_orders,details=details)
    else:
        return "No id_comanda provided"