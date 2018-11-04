# -*- coding: utf-8 -*-
import argparse
import socket
import pickle
import time
import os
import threading


# TODO: Если задание взято на обработку и не отмечено как выполненное в течение 5 минут (еще один параметр запуска), оно должно вернуться в очередь
# TODO: Правильно обрабатывать Ctr+C

class TaskQueueServer:
    def __init__(self, ip='127.0.0.1', port=5555, path='', timeout=3):
        self.ip = ip
        self.port = port
        self.path = path
        self.timeout = timeout
        self.queues = []
        self.timers = []

        self.load()

    def __uniqid(self):
        return hex(int(time.time() * 10000000))[2:]

    def __task_timeout(self, queue, task):
        print('TIMEOUT task {}'.format(task['id']))

        queue['running_tasks'].remove(task)
        queue['data'].insert(0, task)
        self.timers = [t for t in self.timers if t['task_id'] != task['id']]

    def add(self, q_name, length, data):
        if length > 1000000:
            raise ValueError()

        q = self.search_in_dict(self.queues, 'name', q_name)
        if q is None:
            self.queues.append({'name': q_name, 'data': [], 'running_tasks': []})
            q = self.queues[-1]

        id = self.__uniqid()

        q['data'].append({'id': id, 'length': length, 'data': data})

        print('ADD task {} to {}'.format(id, q_name))

        return id

    def search_in_dict(self, source, key_name, value):
        for i in source:
            if i[key_name] == value:
                return i
        return None

    def get(self, q_name):
        q = self.search_in_dict(self.queues, 'name', q_name)
        if q is None or len(q['data']) == 0:
            return 'NONE'

        task = q['data'].pop(0)

        # task['start_time'] = time.time()
        t = threading.Timer(float(self.timeout), self.__task_timeout, [q, task])
        t.start()

        self.timers.append({'timer': t, 'task_id': task['id']})

        q['running_tasks'].append(task)

        print('GET task {} from {}'.format(task['id'], q_name))

        return ' '.join(str(i) for i in task.values())

    def ack(self, q_name, task_id):
        q = self.search_in_dict(self.queues, 'name', q_name)

        if q is None or (len(q['data']) == 0 and len(q['running_tasks']) == 0):
            return 'NO'

        task = self.search_in_dict(q['running_tasks'], 'id', task_id)

        if task is None:
            return 'NO'

        timer = [t for t in self.timers if t['task_id'] == task_id][0]
        timer['timer'].cancel()
        self.timers = [t for t in self.timers if t['task_id'] != task_id]

        print('ACK task {} from {}'.format(id, q_name))

        q['running_tasks'] = [task for task in q['running_tasks'] if task['id'] != task_id]

        return 'YES'

    def in_command(self, q_name, task_id):
        q = self.search_in_dict(self.queues, 'name', q_name)

        if q is None or (len(q['data']) == 0 and len(q['running_tasks']) == 0):
            return 'NO'

        task = self.search_in_dict(q['data'], 'id', task_id)

        if task is None:
            task = self.search_in_dict(q['running_tasks'], 'id', task_id)

        if task is None:
            return 'NO'

        return 'YES'

    def save(self):
        if not os.path.exists(self.path):
            return 'ERROR Path do not exist'

        res = 'OK'
        try:
            with open(os.path.join(self.path, 'task_queue.dump'), 'wb') as handle:
                pickle.dump(self.__dict__, handle, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception as e:
            print(e)
            res = 'ERROR'

        print('SAVED')

        return res

    def load(self):
        if not os.path.exists(os.path.join(self.path, 'task_queue.dump')):
            return 'ERROR Dump dile do not exist'

        print('LOAD from file: {}'.format(os.path.join(self.path, 'task_queue.dump')))

        with open(os.path.join(self.path, 'task_queue.dump'), 'rb') as handle:
            data = pickle.load(handle)

        self.__dict__ = data

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.ip, self.port))

        while True:
            sock.listen(1)
            conn, addr = sock.accept()
            print('Connected to client:', addr)

            data = conn.recv(1000000).decode()

            if not data:
                print('NONE')
                conn.shutdown(1)
                conn.close()
                break

            data = data.split()
            if data[0] == 'ADD':
                res = self.add(data[1], int(data[2]), data[3])
            elif data[0] == 'GET':
                res = self.get(data[1])
            elif data[0] == 'ACK':
                res = self.ack(data[1], data[2])
            elif data[0] == 'IN':
                res = self.in_command(data[1], data[2])
            elif data[0] == 'SAVE':
                res = self.save()
            else:
                res = 'ERROR'

            # conn.send((res + '\n').encode())
            conn.send(res.encode())
            conn.close()


def parse_args():
    parser = argparse.ArgumentParser(description='This is a simple task queue server with custom protocol')
    parser.add_argument(
        '-p',
        action="store",
        dest="port",
        type=int,
        default=5555,
        help='Server port')
    parser.add_argument(
        '-i',
        action="store",
        dest="ip",
        type=str,
        default='0.0.0.0',
        help='Server ip adress')
    parser.add_argument(
        '-c',
        action="store",
        dest="path",
        type=str,
        default='./',
        help='Server checkpoints dir')
    parser.add_argument(
        '-t',
        action="store",
        dest="timeout",
        type=int,
        default=300,
        help='Task maximum GET timeout in seconds')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    server = TaskQueueServer(**args.__dict__)
    server.run()
