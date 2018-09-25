import sqlite3

def create_new_tables():
	conn = sqlite3.connect('msbot_tables_new.db')

	c = conn.cursor()
#	c.execute('''
#		DROP TABLE spoilers
#		''')
        c.execute('''
                DROP TABLE users
                ''')
#	c.execute('''
#		CREATE TABLE spoilers
#		(id varchar(250) NOT NULL, name varchar(250) NOT NULL, img varchar(250) NOT NULL, mana varchar(250) NOT NULL, type varchar(250) NOT NULL, text varchar(250) NOT NULL, power varchar(250), toughness varchar(250), link varchar(250) NOT NULL)
#		''')
	c.execute('''
	        CREATE TABLE users
	        (id varchar(250) NOT NULL, image int(1) NOT NULL, text int(1) NOT NULL, link int(1) NOT NULL, dump int(1) NOT NULL, tokens int(1) NOT NULL)
	        ''')
	conn.commit()
	conn.close()

create_new_tables()
