import pymysql.cursors

import names
import random
import time

from datetime import datetime


class FillBlog(object):
    def __init__(self):
        self.connection = None
        self.users = []
        self.posts = []
        self.comments = []
        self.lastid_sql = "SELECT LAST_INSERT_ID() as id;"

    def connect(self, login="tp_user", password="tp_password", db_name="sys_base", host='localhost'):
        self.connection = pymysql.connect(host=host, user=login, password=password, db=db_name, charset='utf8mb4',
                                          cursorclass=pymysql.cursors.DictCursor)

    def create_users(self):
        print("Creating users...")
        start = time.time()

        create_users_sql = "INSERT INTO users (username, f_name, l_name, password) VALUES "
        user_sql = "('{}', '{}', '{}', SHA1('{}'))"

        for i in range(1000):
            f_name = names.get_first_name()
            l_name = names.get_last_name()
            username = f_name.lower() + str(i)
            password = f_name + l_name

            create_users_sql += user_sql.format(username, f_name, l_name, password)
            if i != 999:
                create_users_sql += ', '
            else:
                create_users_sql += ';'

            self.users.append({'username': username,
                               'f_name': f_name, 'l_name': l_name,
                               'password': f_name + l_name})

        with self.connection.cursor() as cursor:
            cursor.execute(create_users_sql)

            cursor.execute(self.lastid_sql)
            lastid = cursor.fetchone()['id']

        for i, u in enumerate(self.users):
            u['id'] = lastid + i

        self.connection.commit()
        finish = time.time()
        print("Finished in {} s".format(finish - start))

    def create_blogs(self):
        print("Creating blogs...")
        start = time.time()

        create_blogs_sql = "INSERT INTO blogs (title, author_id) VALUES "
        blog_sql = "('{}', {})"

        for i in range(100):
            create_blogs_sql += blog_sql.format(self.users[i]['f_name'] + ' blog', self.users[i]['id'])

            if i != 99:
                create_blogs_sql += ', '
            else:
                create_blogs_sql += ';'

        with self.connection.cursor() as cursor:
            cursor.execute(create_blogs_sql)

            cursor.execute(self.lastid_sql)
            lastid = cursor.fetchone()['id']

        for i, u in enumerate(self.users):
            u['blogs'] = lastid + i

        self.connection.commit()
        finish = time.time()
        print("Finished in {}".format(finish - start))

    def create_posts(self):
        print("Creating posts...")
        start = time.time()

        create_posts_sql = "INSERT INTO posts (title, text, created, author_id) VALUES "
        post_sql = "('{}', '{}', '{}', {})"

        create_blog_posts_sql = "INSERT INTO blog_posts (post_id, blog_id) VALUES "
        blog_post_sql = "({}, {})"

        post_users = []

        for i in range(10000):
            random_user = self.users[random.randint(0, 99)]
            ts = time.time()
            timestamp = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

            create_posts_sql += post_sql.format(random_user['f_name'] + ' description' + str(i),
                                                'Description', timestamp, random_user['id'])

            post_users.append(random_user['id'])

            if i != 9999:
                create_posts_sql += ', '
            else:
                create_posts_sql += ';'

        with self.connection.cursor() as cursor:
            cursor.execute(create_posts_sql)

            cursor.execute(self.lastid_sql)
            lastid = cursor.fetchone()['id']

        for i in range(10000):
            self.posts.append(lastid + i)

            create_blog_posts_sql += blog_post_sql.format(lastid + i, post_users[i])

            if i != 9999:
                create_blog_posts_sql += ', '
            else:
                create_blog_posts_sql += ';'

        with self.connection.cursor() as cursor:
            cursor.execute(create_blog_posts_sql)

        self.connection.commit()
        finish = time.time()
        print("Finished in {}".format(finish - start))

    def create_comments(self):
        print("Creating comments...")
        start = time.time()

        create_comments_sql = "INSERT INTO comments (text, created, author_id, comment_id, post_id) VALUES "
        comment_sql = "('{}', '{}', {}, {}, {})"

        com_posts = []

        # половину к постам
        for i in range(5000):
            ts = time.time()
            timestamp = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            random_user = self.users[random.randint(0, len(self.users) - 1)]
            post_id = self.posts[random.randint(0, len(self.posts) - 1)]
            com_posts.append(post_id)

            create_comments_sql += comment_sql.format(random_user['f_name'] + ' super duper!!!',
                                                      timestamp, random_user['id'], 'NULL',
                                                      post_id)
            if i != 4999:
                create_comments_sql += ', '
            else:
                create_comments_sql += ';'

        with self.connection.cursor() as cursor:
            cursor.execute(create_comments_sql)

            cursor.execute(self.lastid_sql)
            lastid = cursor.fetchone()['id']

        for i in range(5000):
            self.comments.append(lastid + i)

        # половину к комментариям
        create_comments_sql = "INSERT INTO comments (text, created, author_id, comment_id, post_id) VALUES "
        for i in range(5000, 7500):
            ts = time.time()
            timestamp = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            random_user = self.users[random.randint(0, len(self.users) - 1)]
            com_index = random.randint(0, len(self.comments) - 1)

            com_posts.append(com_posts[com_index])

            create_comments_sql += comment_sql.format(random_user['f_name'] + ' super duper!!!',
                                                      timestamp, random_user['id'],
                                                      self.comments[com_index],
                                                      com_posts[com_index])

            if i != 7499:
                create_comments_sql += ', '
            else:
                create_comments_sql += ';'

        with self.connection.cursor() as cursor:
            cursor.execute(create_comments_sql)

            cursor.execute(self.lastid_sql)
            lastid = cursor.fetchone()['id']

        for i in range(2500):
            self.comments.append(lastid + i)

        # Оставшиеся к комментариям комментариев
        # половину к комментариям
        create_comments_sql = "INSERT INTO comments (text, created, author_id, comment_id, post_id) VALUES "
        for i in range(7500, 10000):
            ts = time.time()
            timestamp = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            random_user = self.users[random.randint(0, len(self.users) - 1)]
            com_index = random.randint(0, len(self.comments) - 1)

            create_comments_sql += comment_sql.format(random_user['f_name'] + ' super duper!!!',
                                                      timestamp, random_user['id'],
                                                      self.comments[com_index],
                                                      com_posts[com_index])

            if i != 9999:
                create_comments_sql += ', '
            else:
                create_comments_sql += ';'

        with self.connection.cursor() as cursor:
            cursor.execute(create_comments_sql)

        self.connection.commit()
        finish = time.time()
        print("Finished in {}".format(finish - start))


if __name__ == '__main__':
    fill = FillBlog()
    fill.connect()
    fill.create_users()
    fill.create_blogs()
    fill.create_posts()
    fill.create_comments()

