import pymysql.cursors
import hashlib
import time
from datetime import datetime


class Blog(object):
    def __init__(self):
        self.connection = None
        self.session = None
        pass

    def connect(self, login="tp_user", password="tp_password", db_name="sys_base", host='localhost'):
        self.connection = pymysql.connect(host=host, user=login, password=password, db=db_name, charset='utf8mb4',
                                          cursorclass=pymysql.cursors.DictCursor)

    def disconnect(self):
        self.connection.close()

    def create_user(self, username, first_name, last_name, password):
        check_username_sql = "SELECT id FROM users WHERE username = '{}';".format(username)
        create_user_sql = "INSERT INTO users (username, f_name, l_name, password) VALUES ('{}', '{}', '{}', SHA1('{}'))". \
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

    def delete_user(self, username):
        delete_sql = "DELETE FROM users WHERE username = '{}';".format(username)

        with self.connection.cursor() as cursor:
            cursor.execute(delete_sql)

        self.connection.commit()
        return {"message": "OK"}

    def authorize(self, login, password):
        """
        Авторизоваться пользователем по логину + паролю
        """
        sql = "SELECT * FROM users WHERE username='{}' AND password=SHA1('{}')". \
            format(login, password)

        get_user_id_sql = "SELECT id FROM users WHERE username='{}'". \
            format(login)
        check_sess_sql = "SELECT * FROM sess WHERE user_id='{}'"

        with self.connection.cursor() as cursor:
            cursor.execute(get_user_id_sql)
            user_id = cursor.fetchone()

            if cursor.rowcount == 0:
                return {"error": "404", "message": "User not found"}

            cursor.execute(check_sess_sql.format(user_id['id']))
            sess = cursor.fetchone()

            if cursor.rowcount > 0:
                return {"message": "Session already exists", "sess": sess['sess']}

            cursor.execute(sql)
            authorize_user = cursor.fetchone()
            if cursor.rowcount == 0:
                self.connection.rollback()
                return {"error": "409", "message": "Password and login are not found", "data": authorize_user}

            sess = hashlib.sha1()
            sess.update(str(authorize_user['id']).encode('utf-8'))
            sess.update(str(datetime.now()).encode('utf-8'))
            sess = sess.hexdigest()

            create_session = "INSERT INTO sess (user_id, sess) VALUES ( '{}', '{}')". \
                format(authorize_user['id'], sess)
            cursor.execute(create_session)

            self.connection.commit()
            return {"message": "OK", "sess": sess}

    def get_authorized_user(self, session):
        get_auto_user_sql = "SELECT * FROM sess WHERE sess = '{}'". \
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
        get_users_sql = "SELECT id, username, f_name, l_name FROM users;"

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

        create_blog_sql = "INSERT INTO blogs (title, author_id) VALUES ('{}', {})". \
            format(title, author_id)
        select_last_id = "SELECT LAST_INSERT_ID();"

        with self.connection.cursor() as cursor:
            cursor.execute(check_user_sql)

            if cursor.rowcount == 0:
                self.connection.rollback()
                return {"error": "404", "message": "User doesn't exist"}

            cursor.execute(create_blog_sql)
            cursor.execute(select_last_id)
            blog_id = cursor.fetchone()['LAST_INSERT_ID()']

        self.connection.commit()
        return {"message": "OK", "data": {"id": blog_id, "title": title}}

    def update_blog(self, blog_id, title):
        update_sql = "UPDATE blogs SET title = '{}' WHERE id = {} ". \
            format(title, blog_id)

        with self.connection.cursor() as cursor:
            cursor.execute(update_sql)

        self.connection.commit()
        return {"message": "OK"}

    def delete_blog(self, blog_id):
        """
        Удалить блог
        """
        delete_sql = "DELETE FROM blogs WHERE id = {}". \
            format(blog_id)

        delete_blog_posts_sql = "DELETE FROM blogs WHERE id = {}". \
            format(blog_id)

        with self.connection.cursor() as cursor:
            cursor.execute(delete_sql)

        self.connection.commit()

        return {"message": "OK", "data": blog_id}

    def get_blogs(self, session=None):
        """
        Получить список не удаленных блогов
        или
        получить список не удаленных блогов созданный авторизованным пользователем
        """
        if session is None:
            get_sql = "SELECT id, title FROM blogs"
        else:
            user = self.get_authorized_user(session)

            if user is not None:
                get_sql = "SELECT * FROM blogs WHERE blogs.author_id = {}" \
                    .format(user['id'])
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

        check_user_sql = "SELECT id FROM users WHERE id = {};".format(author_id)

        create_post_sql = "INSERT INTO posts (title, text, created, author_id) VALUES ('{}', '{}', '{}', {});". \
            format(title, text, created, author_id)

        select_last_id = "SELECT LAST_INSERT_ID();"

        create_blog_post_sql = "INSERT INTO blog_posts (post_id, blog_id) VALUES ({}, {});"

        with self.connection.cursor() as cursor:
            cursor.execute(check_user_sql)

            if cursor.rowcount == 0:
                self.connection.rollback()
                return {"error": "404", "message": "User doesn't exist"}

            cursor.execute(create_post_sql)
            cursor.execute(select_last_id)
            post_id = cursor.fetchone()['LAST_INSERT_ID()']

            for blog in blogs:
                cursor.execute(create_blog_post_sql.format(post_id, blog))

        self.connection.commit()
        return {"message": "OK", "data": {"id": post_id, "created": created,
                                          "text": text, "title": title}}

    def update_post(self, post_id, text=None, title=None, blogs=None):
        """
        Отредактировать пост, должна быть возможность изменить заголовки/текст/блоги в которых опубликован
        """
        if text is None and title is None and blogs is None:
            return {"error": "404", "message": "Editable element not provided"}

        with self.connection.cursor() as cursor:
            if text is not None:
                update_text_sql = "UPDATE posts SET text = '{}' WHERE post_id = {}".format(text, post_id)
                cursor.execute(update_text_sql)

            if title is not None:
                update_title_sql = "UPDATE posts SET title = '{}' WHERE post_id = {}".format(title, post_id)
                cursor.execute(update_title_sql)

            if blogs is not None:
                select_blogs_sql = "SELECT * from blog_posts WHERE post_id = {}".format(post_id)
                cursor.execute(select_blogs_sql)

                old_blogs = cursor.fetchall()
                old_blogs = [x['blog_id'] for x in old_blogs]

                # удаляем
                old_blogs = [x for x in old_blogs if x not in blogs]
                # добавляем
                blogs = [x for x in blogs if x not in old_blogs]

                delete_bp_sql = "DELETE FROM blog_posts WHERE post_id = {} AND blog_id = {}"
                add_bp_sql = "INSERT INTO blog_posts (post_id, blog_id) VALUES ({}, {});"

                for blog_id in old_blogs:
                    cursor.execute(delete_bp_sql.format(post_id, blog_id))

                for blog_id in blogs:
                    cursor.execute(add_bp_sql.format(post_id, blog_id))

        self.connection.commit()
        return {"message": "OK", "data": {"id": post_id, "text": text, "title": title}}

    def delete_post(self, post_id):
        delete_post_sql = "DELETE FROM posts WHERE id = {}". \
            format(post_id)

        with self.connection.cursor() as cursor:
            cursor.execute(delete_post_sql)

        self.connection.commit()
        return {"message": "OK", "data": post_id}

    def create_comment(self, session, text, created, post_id=None, comment_id=None):
        """
        добавить комментарий если пользователь авторизован
        комментарии должны реализовывать поддержку веток комментариев ( комментарий можно оставить на пост или на другой комментарий )
        """
        if post_id is None and comment_id is None:
            return {"error": "404", "message": "Parent element not provided"}

        user = self.get_authorized_user(session)

        if user is None:
            self.connection.rollback()
            return {"error": "404", "message": "User doesn't exist"}

        select_comment_sql = "SELECT post_id FROM comments WHERE id = {}"
        create_comment_sql = "INSERT INTO comments (text, created, author_id, comment_id, post_id) VALUES ('{}', '{}', {}, {}, {});"
        select_last_id = "SELECT LAST_INSERT_ID();"

        with self.connection.cursor() as cursor:
            if comment_id is not None:
                cursor.execute(select_comment_sql.format(comment_id))

                if cursor.rowcount == 0:
                    self.connection.rollback()
                    return {"error": "404", "message": "Comment doesn't exist"}

                post_id = cursor.fetchone()['post_id']
            else:
                comment_id = 'NULL'

            cursor.execute(create_comment_sql.format(text, created, user['id'], comment_id, post_id))
            cursor.execute(select_last_id)
            insert_comment_id = cursor.fetchone()['LAST_INSERT_ID()']

        self.connection.commit()
        return {"message": "OK", "data": {"id": insert_comment_id, "created": created,
                                          "text": text, "author_id": user['id'],
                                          "post_id": post_id, "comment_id": comment_id}}

    def get_comments(self, author_id, post_id):
        """
        получить список всех комментариев пользователя к посту
        """
        select_comments_sql = "SELECT text, created FROM comments WHERE author_id = {} AND post_id = {} ORDER BY created".format(
            author_id, post_id)

        with self.connection.cursor() as cursor:
            cursor.execute(select_comments_sql)
            comments = cursor.fetchall()

        self.connection.commit()
        return {"message": "OK", "data": comments}


db = Blog()
db.connect()
# db.create_user('tp_username', 'Angela', 'Svoykina', 'password')
# res = db.authorize('tp_username', 'password')
# print(res)

# res = db.get_users()
# print(res)

# res = db.create_blog(1, "Angelika blog")
# print(res)

# res = db.update_blog(1, "Angelika super blog")
# print(res)

# res = db.create_blog(1, "Angelika trash two blog")
# print(res)

# res = db.delete_blog(res["data"]["id"])
# print(res)

# res = db.get_blogs()
# print(res)

# res = db.get_blogs(session='578e9a838889f42d71f7ad705456da317f7ce2be')
# print(res)

# ts = time.time()
# timestamp = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
# res = db.create_post(1, timestamp, 'My first post', 'My first post', [1])
# print(res)

# ts = time.time()
# timestamp = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
# res = db.create_comment('578e9a838889f42d71f7ad705456da317f7ce2be', 'me first', timestamp, 1)
# print(res)
#
# ts = time.time()
# timestamp = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
# res = db.create_comment('578e9a838889f42d71f7ad705456da317f7ce2be', 'no me', timestamp, None, 1)
# print(res)

# res = db.get_comments(1, 1)
# print(res)

# db.create_user('tp_username2', 'Angela', 'Svoykina', 'password')
# res = db.authorize('tp_username2', 'password')
# print(res)

# ts = time.time()
# timestamp = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
# res = db.create_comment('c967668df612c92fbbdc57dfbbde2c819085ad46', 'no me!', timestamp, None, 2)
# print(res)

# res = db.create_blog(1, 'Second blog')
# print(res)

# res = db.update_post(1, None, None, [1,3])
# print(res)s