import sqlite3

db = sqlite3.connect('instance/quiz_master.db')
cur = db.cursor()
cur.execute('''
    DELETE FROM users
''')
db.commit()
db.close()
print("Succcessfully dropped!")