import sqlite3
import flags

conn = sqlite3.connect('monster.db')

c = conn.cursor()
try:
	c.execute('''DROP TABLE monster''')
except:
	pass

c.execute('''CREATE TABLE monster(
	name varchar(30) PRIMARY KEY NOT NULL,
	display_char char(1) NOT NULL,
	colour varchar(10),
	ai varchar(20) NOT NULL,
	hp int, 
	bab int, 
	str int,
	dex int, 
	con int,
	ing int,
	wis int, 
	cha int,
	mon_type int,
	alignment int, 
	resist int,
	special int, 
	)''')



conn.commit()
