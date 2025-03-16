import sqlite3
# import datetime



# print(datetime.datetime.time())
db = sqlite3.connect('instance/quiz_master.db')



# # def add_chapter():
# #     db = None
# #     try:
# #         chap_name = 'anchor'
# #         chap_desc = 'links'
# #         subject_id = 'CSS'
# #         print(subject_id) 
# #         # Path to the database

# #         db = sqlite3.connect('instance/quiz_master.db')

# #         # Insert chapter with associated subject_id
# #         cur = db.cursor()
# #         chap_id = cur.execute('''
# #                 SELECT id 
# #                         FROM subjects
# #                               WHERE subject_name = (?)
# #         ''',(subject_id,)).fetchone()
# #         print(chap_id)
# #         cur.execute('''
# #             INSERT INTO chapters (chapter_name, chapter_description, subject_id)
# #             VALUES (?, ?, ?)
# #         ''', (chap_name, chap_desc, chap_id[0]))
# #         db.commit()

        

# #     except Exception as e:
        
# #         print(str(e))
        

# #     finally:
# #         if db:
# #             db.close()


# # add_chapter()



cur = db.cursor()
cur.execute('''
    DELETE FROM subjects
''')
db.commit()
db.close()
print("Succcessfully dropped!")


# # def list_of_subjects():
# #     db = None
# #     try:
        
# #         db = sqlite3.connect('instance/quiz_master.db')
# #         cur = db.cursor() 
# #         cur.execute('''
# #                 SELECT DISTINCT id,subject_name,subject_description 
# #                     FROM subjects 
# #             ''')
# #         data = cur.fetchall()
# #         # print(data)
# #         subjects = []
# #         for x in data:
# #             temp ={
# #                 "id":x[0],
# #                 "name":x[1],
# #                 "description":x[2]
# #             }
# #             subjects.append(temp)
# #         print(subjects)

# #     except Exception :
# #         print("sometiing")
# #     finally:
# #         if db is not None:
# #             db.close



# # list_of_subjects()