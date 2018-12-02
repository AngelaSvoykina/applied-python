import pymysql
import os


def create_db(host='localhost', login='tp_user', password='tp_password', db_name='sys_base',
              path_to_schema='./db/schema.sql'):
    if not os.path.isfile(path_to_schema):
        raise TypeError("Schema file doesn't exist!")

    with open(path_to_schema) as schema_file:
        commands = schema_file.read().replace('\n', '').split(';')

    commands = commands[:len(commands) - 1]
    db = pymysql.connect(host=host, user=login, password=password, db=db_name, charset='utf8mb4',
                         cursorclass=pymysql.cursors.DictCursor)

    with db.cursor() as cursor:
        for c in commands:
            cursor.execute(c)

    db.commit()
    db.close()


if __name__ == '__main__':
    create_db()
    create_db(path_to_schema='./db/indexes.sql')

