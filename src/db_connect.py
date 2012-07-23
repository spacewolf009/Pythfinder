import sqlite3
conn = sqlite3.connect('items.db')

c = conn.cursor()

#####################################################################################

for row in c.execute('''SELECT * from weapon_base GROUP BY name'''):
	print row[0] + ' ' + bin(row[8])