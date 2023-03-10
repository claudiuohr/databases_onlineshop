import mysql.connector

def connect_to_database():
    conn=mysql.connector.connect(
        user='root',
        password='123456789',
        database='onlineshop'
    )
    return conn

def create_tables():
    conn=connect_to_database()
    cursor=conn.cursor()

    cursor.execute('''
        CREATE TABLE client (
            id_client  INT NOT NULL AUTO_INCREMENT,
            membership CHAR(1) DEFAULT '0',
            constraint client_membership CHECK (membership IN ('1', '0')),
            PRIMARY KEY (id_client)
        )
    '''
    )

    cursor.execute(''' 
        CREATE TABLE detalii_client (
            id_client    INT         NOT NULL,
            nume         VARCHAR(25) NOT NULL,
            prenume      VARCHAR(25) NOT NULL,
            adresa       VARCHAR(40),
            adresa_email VARCHAR(40) UNIQUE NOT NULL,
            nr_telefon   CHAR(10)    UNIQUE NOT NULL,
            constraint detalii_comanda_email      CHECK (adresa_email REGEXP '[a-z0-9._%-]+@[a-z0-9._%-]+\.[a-z]{2,4}'),
            constraint detalii_comanda_nr_telefon CHECK (nr_telefon REGEXP '^[0][:7:3:2][0-9 ]*$'),
            constraint detalii_comanda_nume       CHECK (nume REGEXP '^[a-z ,.-]+$'),
            constraint detalii_comanda_prenume    CHECK (prenume REGEXP '^[a-z ,.-]+$'),
            PRIMARY KEY (id_client),
            FOREIGN KEY (id_client) REFERENCES client(id_client)
        )
    '''
    )

    cursor.execute(''' 
        CREATE TABLE comanda (
            id_comanda     INT NOT NULL AUTO_INCREMENT,
            id_client      INT NOT NULL,
            pret_total     INT DEFAULT '0',
            metoda_plata   VARCHAR(20) default 'cash',
            adresa_livrare VARCHAR(40) NOT NULL,
            status         VARCHAR(20) NOT NULL,
            PRIMARY KEY (id_comanda),
            FOREIGN KEY (id_client) REFERENCES client(id_client),
            constraint comanda_pret_total CHECK (pret_total >= 0),
            constraint comanda_status CHECK (status IN ('finalizata', 'in_desfasurare','in_curs_de_procesare')),
            constraint comanda_metoda_plata CHECK (metoda_plata IN ('cash', 'card'))
        ) 
    '''
    )

    cursor.execute(''' 
        CREATE TABLE produs (
            id_produs  INT NOT NULL AUTO_INCREMENT,
            denumire   VARCHAR(30) UNIQUE NOT NULL,
            pret       INT NOT NULL,
            cantitate  INT NOT NULL,
            disponibilitate CHAR(1) DEFAULT '1',
            PRIMARY KEY (id_produs),
            constraint produs_denumire      CHECK (denumire REGEXP '^[a-z ,.-]+$'),
            constraint produs_cantitate     CHECK (cantitate >= 0),
            constraint produs_pret          CHECK (pret > 0)
        )
    '''
    )

    cursor.execute(''' 
        CREATE TABLE detalii_comanda (
            id_comanda INT NOT NULL,
            id_produs INT NOT NULL,
            nr_prd     INT NOT NULL,
            pret_la_unitate INT NOT NULL,
            constraint detalii_comanda_pret CHECK (pret_la_unitate > 0),
            PRIMARY KEY (id_comanda,id_produs),
            FOREIGN KEY (id_comanda) REFERENCES comanda(id_comanda),
            FOREIGN KEY (id_produs) REFERENCES produs(id_produs)
        )
    '''
    )

    cursor.execute(''' 
        CREATE TRIGGER Trg_comanda_pret_total_insert
        BEFORE INSERT ON comanda
        FOR EACH ROW 
        BEGIN
            DECLARE aux_mem CHAR(1);
            SELECT client.membership INTO aux_mem
            FROM client
            WHERE client.id_client = NEW.id_client;

            IF (aux_mem = 1) THEN
                SET NEW.pret_total = NEW.pret_total * 0.9;
            ELSEIF (aux_mem = 0) THEN
                SET NEW.pret_total = NEW.pret_total;
            END IF;
        END;
    '''
    )

    cursor.execute(''' 
        CREATE TRIGGER Trg_comanda_pret_total_update
        BEFORE UPDATE ON comanda 
        FOR EACH ROW 
        BEGIN
            DECLARE aux_mem CHAR(1);

            SELECT client.membership INTO aux_mem
            FROM client
            WHERE client.id_client = NEW.id_client;

            IF (aux_mem = 1) THEN
                SET NEW.pret_total = NEW.pret_total * 0.9;
            ELSEIF (aux_mem = 0) THEN
                SET NEW.pret_total = NEW.pret_total;
            END IF;
        END;
    '''
    )

    cursor.execute(''' 
        CREATE TRIGGER Trg_update_prd_disp_insert
            AFTER INSERT ON detalii_comanda
            FOR EACH ROW
        BEGIN
                UPDATE produs
                SET cantitate = cantitate - NEW.nr_prd
                WHERE id_produs = NEW.id_produs;
        END;
    '''
    )

    cursor.execute(''' 
        CREATE TRIGGER Trg_update_prd_disp_update
            AFTER UPDATE ON detalii_comanda
            FOR EACH ROW
        BEGIN
                UPDATE produs
                SET cantitate = cantitate - (NEW.nr_prd-OLD.nr_prd)
                WHERE id_produs = NEW.id_produs;
        END;
    '''
    )

    cursor.execute(''' 
        CREATE TRIGGER Trg_update_total_price_insert
        AFTER INSERT ON detalii_comanda
        FOR EACH ROW
        BEGIN
            UPDATE comanda
            SET pret_total =(SELECT SUM(nr_prd * p.pret)
                            FROM detalii_comanda d, produs p
                            WHERE d.id_produs = p.id_produs AND d.id_comanda = comanda.id_comanda);
        END;
    '''
    )

    cursor.execute(''' 
        CREATE TRIGGER Trg_update_total_price_update
        AFTER UPDATE ON detalii_comanda
        FOR EACH ROW
        BEGIN
            UPDATE comanda
            SET pret_total =(SELECT SUM(nr_prd * p.pret)
                            FROM detalii_comanda d , produs p
                            WHERE d.id_produs = p.id_produs AND d.id_comanda = comanda.id_comanda);
        END;
    '''
    )

    cursor.execute(''' 
        CREATE TRIGGER TRG_detalii_com_nr_prd_disp
        BEFORE INSERT ON detalii_comanda
        FOR EACH ROW
        BEGIN
            DECLARE dis INT;
            SELECT cantitate INTO dis
            FROM produs
            WHERE id_produs = NEW.id_produs;
            
            IF (dis < NEW.nr_prd) THEN
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Insufficient availability for product with ID ';
            END IF;
        END;
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
    
    cursor.execute("SHOW TRIGGERS")
    triggers = cursor.fetchall()

    for trigger in triggers:
        stmt = f"DROP TRIGGER {trigger[0]}"
        cursor.execute(stmt)
    
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    cursor.execute("COMMIT")

def insert_data():
    conn = connect_to_database()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO client (membership) VALUES
        (0),
        (0),
        (1),
        (1),
        (1)
    """)

    cursor.execute("""
        INSERT INTO detalii_client (adresa,adresa_email,nr_telefon,nume,prenume,id_client) VALUES
        (null,'claudiuohr@gmail.com','0756412417','Ohriniuc','Claudiu',1),
        ('Bulevardul chimiei pe capat','csmctl@gmail.com','0755412417','Cosmin','Catalin',2),
        ('Botosani str Mihai Kogalniceanu nr2','marcelinooooo@yahoo.com','0226412417','Apetrei','Marcelino',3),
        ('Brasov str Frizerului nr28','mihaipiticu@yahoo.com','0796412417','Piticu','Mihaita',4),
        ('Hollywood','michaeljack@gmail.com','0356412417','Jackson','Michael',5)
    """)

    cursor.execute("""
        INSERT INTO comanda (id_client,pret_total,metoda_plata,adresa_livrare,status) VALUES
            (1,default,'cash','Bulevardul chimiei pe capat','finalizata'),
            (4,default,'card','Bulevardul chimiei pe capat','in_desfasurare'),
            (3,default,'cash','Botosani str Mihai Kogalniceanu nr2','finalizata'),
            (5,default,'card','Hollywood','finalizata'),
            (2,default,'card','Brasov str Frizerului nr28','in_desfasurare')
    """)

    cursor.execute("""
        INSERT INTO produs (denumire,pret,cantitate,disponibilitate) VALUES
        ('casti',379,15,1),
        ('mouse',189,14,1),
        ('monitor',1099,13,1),
        ('laptop',5099,16,1),
        ('tastatura',499,16,1)
    """)

    cursor.execute("""
        INSERT INTO detalii_comanda (nr_prd,id_produs,id_comanda,pret_la_unitate) VALUES
        (1,1,2,379),
        (1,1,1,379),
        (3,2,4,189),
        (4,3,5,1099),
        (5,4,3,5099)
    """)
    
    cursor.execute("COMMIT")