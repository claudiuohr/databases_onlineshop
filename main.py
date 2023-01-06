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
    cursor.execute("""SELECT d.id_client,d.nume,d.prenume,d.adresa_email,d.nr_telefon,d.adresa,c.membership 
    FROM client c JOIN detalii_client d ON d.id_client=c.id_client""")
    customers = cursor.fetchall()
    return render_template('customers.html',customers=customers)

@app.route('/add_customer',methods=['GET','POST'])
def handle_add_customer():
    membership = request.form['membership']
    nume = request.form['nume']
    prenume = request.form['prenume']
    adresa_email = request.form['adresa_email']
    nr_telefon = request.form['nr_telefon']
    adresa = request.form['adresa']
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute(f"""INSERT INTO client (membership) VALUES ({membership})""")
    cursor.execute("""INSERT INTO detalii_client (adresa,adresa_email,nr_telefon,nume,prenume,id_client) VALUES (%s,%s,%s,%s,%s, LAST_INSERT_ID())""",(adresa,adresa_email,nr_telefon,nume,prenume))
    cursor.execute("COMMIT")
    return redirect('/customers')