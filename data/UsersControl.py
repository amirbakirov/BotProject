import sqlite3
import random

filePath = "data/Users.db"


class SqlController:
    def New_User(self, tg_id, name, city, sex, pref_sex, description, alias):
        con = sqlite3.connect(filePath)
        cur = con.cursor()
        cur.execute(f"""INSERT INTO UsersDB VALUES(Null, ?, ?, ?, ?, ?, ?, ?)""",
                    (tg_id, name, city, sex, pref_sex, description, alias))
        con.commit()
        con.close()

    def Find_User(self, current_user_tg_id):
        con = sqlite3.connect(filePath)
        cur = con.cursor()
        count = len(cur.execute(f"""SELECT * FROM UsersDB""").fetchall())
        random_user_id = random.randint(1, count)
        if count > 1:
            while cur.execute(f"""SELECT tg_id FROM UsersDB WHERE id={random_user_id}""").fetchall()[0][0] == \
                    current_user_tg_id:
                random_user_id = random.randint(1, count)
        result = cur.execute(f"""SELECT * FROM UsersDB WHERE id={random_user_id}""").fetchall()
        con.close()
        return result[0]

    def Get_User_ID_By_Chat_ID(self, _id):
        con = sqlite3.connect(filePath)
        cur = con.cursor()
        user = cur.execute(f"""SELECT * FROM UsersDB WHERE tg_id={_id}""").fetchall()
        con.close()
        return user[0]

    def is_user_was_here_before(self, _id):
        con = sqlite3.connect(filePath)
        cur = con.cursor()
        user = cur.execute(f"""SELECT * FROM UsersDB WHERE tg_id={_id}""").fetchall()
        con.close()
        return len(user)

    def Rate_User(self, first_id, second_id):  # first_id - id юзера которого оценили; second_id - id юзера кто оценил
        con = sqlite3.connect(filePath)
        cur = con.cursor()
        to_check = cur.execute(f"""SELECT * FROM RatedUsers WHERE UserWhoWasRatedID={first_id}""").fetchall()
        b = True
        for elem in to_check:
            if elem[1] == second_id:
                b = False
                break
        if b:
            cur.execute(f"""INSERT INTO RatedUsers VALUES(?, ?)""", (first_id, second_id))
            con.commit()
        con.close()

    def Get_Rated_Users(self, _id):
        con = sqlite3.connect(filePath)
        cur = con.cursor()
        # users = cur.execute(
        #     f"""SELECT * FROM UsersDB INNER JOIN RatedUsers ON UsersDB.id = RatedUsers.UserWhoWasRatedID WHERE tg_id={tg_id}""").fetchall()
        us = cur.execute(f"""SELECT UserWhoRated FROM RatedUsers WHERE UserWhoWasRatedID={_id}""").fetchall()
        cur.execute(f"""DELETE FROM RatedUsers WHERE UserWhoWasRatedID={_id}""")
        con.commit()
        users = []
        for user in us:
            users.append(cur.execute(f"""SELECT * FROM UsersDB WHERE id={user[0]}""").fetchall())
        con.close()
        # print(users)
        return users

    def Chnage_User_Name(self, tg_id, new_name):
        con = sqlite3.connect(filePath)
        cur = con.cursor()
        cur.execute(f"""UPDATE UsersDB SET name=? WHERE tg_id=?""", (new_name, tg_id))
        con.commit()
        con.close()

    def Chnage_User_City(self, tg_id, new_city):
        con = sqlite3.connect(filePath)
        cur = con.cursor()
        cur.execute(f"""UPDATE UsersDB SET city=? WHERE tg_id=?""", (new_city, tg_id))
        con.commit()
        con.close()

    def Chnage_User_Description(self, tg_id, new_description):
        con = sqlite3.connect(filePath)
        cur = con.cursor()
        cur.execute(f"""UPDATE UsersDB SET description=? WHERE tg_id=?""", (new_description, tg_id))
        con.commit()
        con.close()

    def Get_User_by_Chat_id(self, tg_id):
        con = sqlite3.connect(filePath)
        cur = con.cursor()
        user = cur.execute(f"""SELECT * FROM UsersDB WHERE tg_id={tg_id}""").fetchall()
        con.close()
        return user[0]

    def Get_User_by_Id(self, _id):
        con = sqlite3.connect(filePath)
        cur = con.cursor()
        user = cur.execute(f"""SELECT * FROM UsersDB WHERE id={_id}""").fetchall()
        con.close()
        return user[0]
