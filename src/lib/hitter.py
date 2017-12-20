import pymysql.cursors

class Person:
    def __init__(self, person_dict):
        self.name = person_dict['NAME']
        self.pcode = person_dict['PCODE']
        self.team = person_dict['TEAM']
        self.birth = person_dict['BIRTH']
        self.position = person_dict['POSITION']
        self.height = person_dict['HEIGHT']
        self.weight = person_dict['WEIGHT']
        self.hit_type = person_dict['HITTYPE']
        self.money = person_dict['MONEY']


class Hitter(Person):
    def __init__(self, pcode):
        self.host = 'localhost'
        self.user = 'root'
        self.password = 'lab2ai64'
        self.db = 'baseball'
        self.port = 3307
        Person.__init__(self.get_personal_dict(pcode))


    def get_personal_dict(self, pcode):
        conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password, db=self.db,
                               charset='utf8mb4')
        query = "SELECT NAME, TEAM, POSITION, BIRTH, HEIGHT, WEIGHT, HITTYPE, MONEY "\
                           "FROM baseball.person "\
                           "WHERE PCODE = %s " % pcode

        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            return result

    def get_today_record(self):
        conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password, db=self.db,
                               charset='utf8mb4')
        query = "SELECT NAME, TEAM, POSITION, BIRTH, HEIGHT, WEIGHT, HITTYPE, MONEY " \
                "FROM baseball.person " \
                "WHERE PCODE = %s " % Person.pcode

        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            return result

