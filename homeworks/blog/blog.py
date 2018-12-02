import pymysql.cursors
import hashlib
from datetime import datetime


class Blog(object):
    def __init__(self):
        self.connection = None

    def __get_authorized_user(self, session):
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

    def connect(self, login="tp_user", password="tp_password", db_name="sys_base", host='localhost'):
        self.connection = pymysql.connect(host=host, user=login, password=password, db=db_name, charset='utf8mb4',
                                          cursorclass=pymysql.cursors.DictCursor)

    def disconnect(self):
        self.connection.close()

    def create_user(self, username, first_name, last_name, password):
        """
        Добавление пользователя
        :return: возвращается id пользователя в качестве data
        """
        check_username_sql = "SELECT id FROM users WHERE username = '{}';".format(username)
        create_user_sql = "INSERT INTO users (username, f_name, l_name, password) VALUES ('{}', '{}', '{}', SHA1('{}'))". \
            format(username, first_name, last_name, password)
        select_last_id = "SELECT LAST_INSERT_ID();"

        with self.connection.cursor() as cursor:
            cursor.execute(check_username_sql)
            conflict_user = cursor.fetchone()

            if cursor.rowcount != 0:
                self.connection.rollback()
                return {"error": "409", "message": "User already exists", "data": conflict_user}

            cursor.execute(create_user_sql)
            id = cursor.execute(select_last_id)
            id = cursor.fetchone()['LAST_INSERT_ID()']

        self.connection.commit()
        return {"message": "OK", "data": id}

    def authorize(self, login, password):
        """
        Авторизация пользователя по логину + паролю
        :return: строка сессии
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

    def get_users(self):
        """
        Получение всех пользователей
        """
        get_users_sql = "SELECT id, username, f_name, l_name FROM users;"

        with self.connection.cursor() as cursor:
            cursor.execute(get_users_sql)
            users = cursor.fetchall()

        self.connection.commit()
        return {"message": "OK", "data": users}

    def create_blog(self, author_id, title):
        """
        Создать блог
        :return: Данные созданного блога
        """
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
        """
        Редактировать блог
        """
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

        return {"message": "OK"}

    def get_blogs(self, session=None):
        """
        Получить список не удаленных блогов
        или
        получить список не удаленных блогов созданный авторизованным пользователем
        """
        if session is None:
            get_sql = "SELECT id, title FROM blogs"
        else:
            user = self.__get_authorized_user(session)
            if user is not None:
                get_sql = "SELECT id, title FROM blogs WHERE blogs.author_id = {}" \
                    .format(user['user_id'])
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
        :param author_id: id автора
        :param created: строка времени создания в формате '%Y-%m-%d %H:%M:%S'
        :param text: содержание поста
        :param title: заголовок поста
        :param blogs: массив из id блогов
        :return: данные поста, включая его id
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
        Отредактировать пост, есть возможность изменить заголовки/текст/блоги в которых опубликован
        :param post_id: id поста
        :param text: если задан, меняется содержимое поста
        :param title: если задан, меняется заголовок поста
        :param blogs: массив из id блогов, если задан - меняются блоги, в которых опубликован пост
        :return: обновленные данные поста
        """
        if text is None and title is None and blogs is None:
            return {"error": "404", "message": "Editable element not provided"}

        with self.connection.cursor() as cursor:
            if text is not None:
                update_text_sql = "UPDATE posts SET text = '{}' WHERE id = {}".format(text, post_id)
                cursor.execute(update_text_sql)

            if title is not None:
                update_title_sql = "UPDATE posts SET title = '{}' WHERE id = {}".format(title, post_id)
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
        """
        Удалить пост по id
        """
        delete_post_sql = "DELETE FROM posts WHERE id = {}". \
            format(post_id)

        with self.connection.cursor() as cursor:
            cursor.execute(delete_post_sql)

        self.connection.commit()
        return {"message": "OK"}

    def create_comment(self, session, text, created, post_id=None, comment_id=None):
        """
        Добавить комментарий если пользователь авторизован
        Есть поддержка веток комментариев (комментарий можно оставить на пост или на другой комментарий)

        :param session: сессия пользователя
        :param text: содержимое комментария
        :param created: строка времени создания в формате '%Y-%m-%d %H:%M:%S'
        :param post_id: id поста, если комментарий к посту
        :param comment_id: id комментария, если комментарий оставлен на другой комментарий
        :return: данные созданного комментария, включая id
        """
        if post_id is None and comment_id is None:
            return {"error": "404", "message": "Parent element not provided"}

        user = self.__get_authorized_user(session)

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

            cursor.execute(create_comment_sql.format(text, created, user['user_id'], comment_id, post_id))
            cursor.execute(select_last_id)
            insert_comment_id = cursor.fetchone()['LAST_INSERT_ID()']

        self.connection.commit()
        return {"message": "OK", "data": {"id": insert_comment_id, "created": created,
                                          "text": text, "author_id": user['id'],
                                          "post_id": post_id, "comment_id": comment_id}}

    def get_comments(self, author_id, post_id):
        """
        Получить список всех комментариев пользователя к посту
        :param author_id: id пользователя
        :param post_id: id поста
        """
        select_comments_sql = "SELECT text, created FROM comments WHERE author_id = {} AND post_id = {} ORDER BY id".format(
            author_id, post_id)

        with self.connection.cursor() as cursor:
            cursor.execute(select_comments_sql)
            comments = cursor.fetchall()

        self.connection.commit()
        return {"message": "OK", "data": comments}

    def get_thread_comments(self, comment_id):
        """
        Получения ветки комментариев начиная с заданного
        """
        select_comment_sql = "SELECT * from comments WHERE id={}".format(comment_id)
        # select_post_comments_sql = "SELECT * from comments WHERE blog_id={}"
        select_child_comment_sql = "SELECT id, text, created, comment_id, post_id FROM comments WHERE post_id={} AND comment_id={}"

        with self.connection.cursor() as cursor:
            cursor.execute(select_comment_sql)
            root_comment = cursor.fetchone()

            comments = [{"id": root_comment['id'], "text": root_comment['text'],
                         "created": root_comment['created'], "comment_id": root_comment['comment_id'],
                         "post_id": root_comment['post_id']}]
            parent_ids = [root_comment['id']]

            while len(parent_ids) != 0:
                parent_id = parent_ids[0]
                cursor.execute(select_child_comment_sql.format(root_comment['post_id'], parent_id))
                parent_ids.remove(parent_id)
                childs = cursor.fetchall()
                comments += childs
                parent_ids += [x["id"] for x in childs]

        self.connection.commit()
        return {"message": "OK", "data": comments}

    def get_users_comments(self, users_id, blog_id):
        """
        Получение всех комментариев для 1 или нескольких указанных пользователей из указанного блога
        :param users_id: массив из id пользователей
        :param blog_id: id блога
        """
        if len(users_id) == 0:
            return {"error": "409", "message": "Users data incorrect"}

        select_users_comments_sql = "SELECT c.text, c.created, c.author_id, c.post_id, c.comment_id FROM comments AS c" \
                                    " JOIN posts  AS p ON c.post_id = p.id " \
                                    "JOIN blog_posts AS b_p ON p.id = b_p.post_id " \
                                    "WHERE blog_id = {} AND ({}) ORDER BY c.id"

        users_condition = ''
        for i, user in enumerate(users_id):
            if i != 0:
                users_condition += ' OR '
            users_condition += 'c.author_id={}'.format(user)

        with self.connection.cursor() as cursor:
            cursor.execute(select_users_comments_sql.format(blog_id, users_condition))
            comments = cursor.fetchall()

        self.connection.commit()
        return {"message": "OK", "data": comments}


if __name__ == '__main__':
    db = Blog()
    db.connect()
    res = db.get_thread_comments(10413)
    print(res)

