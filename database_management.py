import mysql.connector

def connect_to_database():
    conn=mysql.connector.connect(
        user='root',
        password='123456789',
        database='onlineshop'
    )
    return conn

def create():
    conn=connect_to_database()
    cursor=conn.cursor()

    cursor.execute('''
        CREATE TABLE client (
            id_client  INT NOT NULL AUTO_INCREMENT,
            membership CHAR(1) DEFAULT '0' NOT NULL,
            PRIMARY KEY (id_client)
        )
    '''
    )

    cursor.execute(''' 
        CREATE TABLE comanda (
            id_comanda     INT NOT NULL AUTO_INCREMENT,
            pret_total     INT DEFAULT '0',
            adresa_livrare VARCHAR(40) NOT NULL,
            status         VARCHAR(20) NOT NULL,
            id_client      INT NOT NULL,
            PRIMARY KEY (id_comanda),
            FOREIGN KEY (id_client) REFERENCES client(id_client),
            constraint comanda_pret_total CHECK (pret_total >= 0),
            constraint comanda_status CHECK (status IN ('finalizata', 'in_desfasurare'))
        ) 
    '''
    )

    cursor.execute(''' 
        CREATE TABLE detalii_client (
            adresa       VARCHAR(40),
            adresa_email VARCHAR(40) NOT NULL,
            nr_telefon   CHAR(10) NOT NULL,
            nume         VARCHAR(25) NOT NULL,
            prenume      VARCHAR(25) NOT NULL,
            id_client    INT NOT NULL,
            constraint detalii_comanda_email CHECK (adresa_email REGEXP '[a-z0-9._%-]+@[a-z0-9._%-]+\.[a-z]{2,4}'),
            constraint detalii_comanda_nr_telefon CHECK (nr_telefon REGEXP '^[0][:7:3:2][0-9 ]*$'),
            constraint detalii_comanda_nume CHECK (nume REGEXP '[A-Za-z]*'),
            constraint detalii_comanda_prenume CHECK (prenume REGEXP '[A-Za-z]*'),
            PRIMARY KEY (id_client),
            FOREIGN KEY (id_client) REFERENCES client(id_client)
        )
    '''
    )

    cursor.execute(''' 
        CREATE TABLE metoda_de_plata (
            cash       CHAR(1) DEFAULT '0' NOT NULL,
            card       CHAR(1) DEFAULT '1' NOT NULL,
            id_comanda INT NOT NULL,
            CHECK (cash <> card),
            PRIMARY KEY (id_comanda),
            FOREIGN KEY (id_comanda) REFERENCES comanda(id_comanda)
        )
    '''
    )

    cursor.execute(''' 
        CREATE TABLE produs (
            id_produs INT NOT NULL AUTO_INCREMENT,
            denumire   VARCHAR(30) NOT NULL,
            pret       INT NOT NULL,
            disponibilitate INT NOT NULL,
            PRIMARY KEY (id_produs),
            CHECK (disponibilitate > 0),
            CHECK (pret > 0)
        )
    '''
    )

    cursor.execute(''' 
        CREATE TABLE detalii_comanda (
            id_produs INT NOT NULL,
            id_comanda INT NOT NULL,
            nr_prd     INT NOT NULL,
            PRIMARY KEY (id_comanda,id_produs),
            FOREIGN KEY (id_comanda) REFERENCES comanda(id_comanda),
            FOREIGN KEY (id_produs) REFERENCES produs(id_produs)
        )
    '''
    )
    cursor.execute("COMMIT")

def delete_tables():
    conn = connect_to_database()
    cursor = conn.cursor()

    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()

    for table in tables:
        table_name = table[0]
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    cursor.execute("COMMIT")