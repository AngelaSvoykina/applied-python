import names
import random
import time

from datetime import datetime

from blog import Blog


class FillBlog(object):
    def __init__(self):
        self.db = Blog()
        self.db.connect()
        self.users = []
        self.posts = []
        self.comments = []

    def create_users(self):
        print("Creating users...")
        start = time.time()
        for i in range(1000):
            f_name = names.get_first_name()
            l_name = names.get_last_name()
            username = f_name.lower() + str(i)
            password = f_name + l_name
            data_id = self.db.create_user(username=username, first_name=f_name, last_name=l_name, password=password)
            session_response = self.db.authorize(username, password)
            self.users.append({'username': username,
                               'f_name': f_name, 'l_name': l_name,
                               'password': f_name + l_name, 'id': data_id['data'],
                               'sess': session_response['sess']})
        finish = time.time()
        print("Finished in {}".format(finish - start))

    def create_blogs(self):
        print("Creating blogs...")
        start = time.time()

        for i in range(100):
            res = self.db.create_blog(self.users[i]['id'], self.users[i]['f_name'] + ' blog')
            self.users[i]['blogs'] = [res["data"]["id"]]

        finish = time.time()
        print("Finished in {}".format(finish - start))

    def create_posts(self):
        print("Creating posts...")
        start = time.time()
        for i in range(10000):
            random_user = self.users[random.randint(0, 99)]
            ts = time.time()
            timestamp = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            data_id = self.db.create_post(random_user['id'], timestamp, 'Description',
                                          random_user['f_name'] + ' description' + str(i),
                                          random_user['blogs'])
            self.posts.append(data_id['data']['id'])

        finish = time.time()
        print("Finished in {}".format(finish - start))

    def create_comments(self):
        print("Creating comments...")
        start = time.time()

        ts = time.time()
        timestamp = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        res = self.db.create_comment(self.users[0]['sess'], self.users[0]['f_name'] + ' super duper!!!',
                                     timestamp, self.posts[random.randint(0, len(self.posts) - 1)])
        self.comments.append(res['data']['id'])

        for i in range(9999):
            ts = time.time()
            timestamp = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            random_user = self.users[random.randint(0, len(self.users) - 1)]
            post_comment = random.randint(0, 1)
            if post_comment:
                res = self.db.create_comment(random_user['sess'], random_user['f_name'] + ' super duper!!!',
                                       timestamp, self.posts[random.randint(0, len(self.posts) - 1)])
                self.comments.append(res['data']['id'])
            else:
                res = self.db.create_comment(random_user['sess'], random_user['f_name'] + ' super duper!!!',
                                       timestamp, None, self.comments[random.randint(0, len(self.comments) - 1)])
                self.comments.append(res['data']['id'])

        finish = time.time()
        print("Finished in {}".format(finish - start))


if __name__ == '__main__':
    fill = FillBlog()
    fill.create_users()
    fill.create_blogs()
    fill.create_posts()
    fill.create_comments()