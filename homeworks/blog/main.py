import pymysql.cursors
import hashlib
from datetime import datetime


class Blog(object):
    def __init__(self):
        self.connection = None
        self.session = None
        pass

    def connect(self, login="tp_user", password="tp_password", db_name="sys_base", host='localhost'):
        self.connection = pymysql.connect(host=host, user=login, password=password, db=db_name, charset='utf8mb4',
                                          cursorclass=pymysql.cursors.DictCursor)

    def create_user(self, username, first_name, last_name, password):
        check_username_sql = "SELECT id FROM users WHERE username = '{}';".format(username)
        create_user_sql = "INSERT INTO users (username, f_name, l_name, password) VALUES ('{}', '{}', '{}', SHA256('{}'))". \
            format(username, first_name, last_name, password)

        with self.connection.cursor() as cursor:
            cursor.execute(check_username_sql)
            conflict_user = cursor.fetchone()

            if cursor.rowcount != 0:
                self.connection.rollback()
                return {"error": "409", "message": "User already exists", "data": conflict_user}

            cursor.execute(create_user_sql)

        self.connection.commit()
        return {"message": "OK"}

    def authorize(self, login, password):
        sql = "SELECT * FROM users WHERE username='{}' AND password=SHA256('{}')". \
            format(login, password)

        with self.connection.cursor() as cursor:
            cursor.execute(sql)
            authorize_user = cursor.fetchone()

            if cursor.rowcount == 0:
                self.connection.rollback()
                return {"error": "409", "message": "Password and login are not found", "data": authorize_user}

            sess = hashlib.sha256()
            sess.update(authorize_user.id)
            sess.update(datetime.now())
            sess = sess.hexdigest()

            create_session = "INSERT INTO sess (user_id, sess) VALUES ( '{}', '{}')". \
                format(authorize_user.id, sess)
            cursor.execute(create_session)

            self.connection.commit()
            return {"message": "OK", sess: sess}

    def get_authorized_user(self, session):
        get_auto_user_sql = "SELECT * FROM sess WHERE sess = {}". \
            format(session)

        with self.connection.cursor() as cursor:
            cursor.execute(get_auto_user_sql)
            user = cursor.fetchone()

            if cursor.rowcount == 0:
                self.connection.rollback()
                return None

            self.connection.commit()
            return user

    def get_users(self):
        """
        Получение всех пользователей
        """
        get_users_sql = "SELECT username, f_name, l_name FROM users;"

        # Подсоединяемся к базе
        with self.connection.cursor() as cursor:
            # Выполнение sql-запроса
            cursor.execute(get_users_sql)
            # Получение объектов, возвращаемых запросом
            users = cursor.fetchall()

        # записываем изменения
        self.connection.commit()
        # возвращается сообщение, что все ок
        return {"message": "OK", "data": users}

    def create_blog(self, author_id, title):
        check_user_sql = "SELECT id FROM users WHERE id = {};".format(author_id)
        create_blog_posts_sql = "INSERT INTO blog_posts (author_id) VALUES ({})".format(author_id)
        select_blog_posts_id = "SELECT LAST_INSERT_ID();"

        with self.connection.cursor() as cursor:
            cursor.execute(check_user_sql)

            if cursor.rowcount == 0:
                self.connection.rollback()
                return {"error": "404", "message": "User doesn't exist"}

            cursor.execute(create_blog_posts_sql)
            cursor.execute(select_blog_posts_id)
            blog_posts_id = cursor.fetchone()
            print(blog_posts_id)
            create_blog_sql = "INSERT INTO blogs (title, blog_posts_id) VALUES ('{}', {})". \
                format(title, blog_posts_id)

        self.connection.commit()
        return {"message": "OK"}

    # TODO
    def update_blog(self, blog_id, title):

        update_sql = "UPDATE blogs SET title = '{}' WHERE id = {} ". \
            format(title, blog_id)

        with self.connection.cursor() as cursor:
            # Выполнение sql-запроса
            cursor.execute(update_sql)
            # записываем изменения
        self.connection.commit()
        # возвращается сообщение, что все ок
        return {"message": "OK"}

    # TODO
    def delete_blog(self, blog_id):
        """
        Удалить блог
        """
        delete_sql = "DELETE FROM blogs WHERE id VALUES ({})". \
            format(blog_id)

        with self.connection.cursor() as cursor:
            # Выполнение sql-запроса
            cursor.execute(delete_sql)
            # записываем изменения
        self.connection.commit()
        # возвращается сообщение, что все ок
        return {"message": "OK"}

        # TODO

    def get_blogs(self, session=None):

        """
        Получить список не удаленных блогов
        или
        получить список не удаленных блогов созданный авторизованным пользователем
        """
        if session is None:
            get_sql = "SELECT * FROM blogs"
        else:
            user = self.get_authorized_user(session)

            if user is not None:
                get_sql = "SELECT * FROM blogs as b JOIN blog_posts as b_p ON b.blog_posts_id = b_p.id WHERE b_p.author_id = {}" \
                    .format(user.id)
            else:
                self.connection.rollback()
                return {"error": "404", "message": "User doesn't exist"}

        with self.connection.cursor() as cursor:
            cursor.execute(get_sql)
            blogs = cursor.fetchall()

        self.connection.commit()
        return {"message": "OK", "data": blogs}


def create_post(self, author_id, created, text, title, blogs):
    """
    Создать пост связанный с одним или несколькими блогами
    """
    # пост добавлю в посты(таблицв) для каждого блога в котором опубликован пост создаю запись в блоги пост,
    # которая связывает блогипост
    pass


def update_post(self, text=None, title=None, blogs=None):
    """
    Отредактировать пост, должна быть возможность изменить заголовки/текст/блоги в которых опубликован
    """
    update_post_sql = "UPDATE posts SET title = '{}',text = '{}'    "

    if text is None and title is None and blogs is None:
        return

    pass


def delete_post(self, post_id):

    delete_post_sql = "DELETE FROM posts WHERE id = {}".\
        format(post_id)
    
    pass


def create_comment(self, author_id, text, post_id=None, comment_id=None):
    """
    добавить комментарий если пользователь авторизован
    комментарии должны реализовывать поддержку веток комментариев ( комментарий можно оставить на пост или на другой комментарий )
    """

    if post_id is None and comment_id is None:
        return

    pass


def get_comments(self, author_id, post_id):
    """
    получить список всех комментариев пользователя к посту
    """
    pass


db = Blog()
db.connect()
# db.create_user('tp_username', 'Angela', 'Svoykina', 'password')
