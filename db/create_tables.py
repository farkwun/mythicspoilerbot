import sqlite3

def create_new_tables():
	conn = sqlite3.connect('msbot_tables.db')

	c = conn.cursor()
	c.execute('''
		CREATE TABLE spoilers
		(date varchar(250) NOT NULL, img varchar(250) NOT NULL)
		''')
	c.execute('''
	        CREATE TABLE users
	        (id varchar(250) NOT NULL, last varchar(250) NOT NULL)
	        ''')
	conn.commit()
	conn.close()

create_new_tables()
