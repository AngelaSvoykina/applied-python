# -*- coding: utf-8 -*-
import argparse
import socket
import pickle
import time
import os
import threading


def search_in_dict(source, key_name, value):
    for i in source:
        if i[key_name] == value:
            return i
    return None


class TaskQueueServer:
    def __init__(self, ip='127.0.0.1', port=5555, path='', timeout=3):
        self.ip = ip
        self.port = port
        self.path = path
        self.timeout = timeout
        self.queues = {}
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

        try:
            q = self.queues[q_name]
        except KeyError:
            self.queues[q_name] = []
            q = self.queues[q_name]

        id = self.__uniqid()

        q.append({'id': id, 'length': length, 'data': data, 'start_time': None})

        print('ADD task {} to {}'.format(id, q_name))

        return id

    def get(self, q_name):

        try:
            q = self.queues[q_name]
        except KeyError:
            return 'NONE'

        if len(q) == 0:
            return 'NONE'

        task = None
        for t in q:
            if t['start_time'] is None or time.time() - t['start_time'] > self.timeout:
                task = t
                break

        if task is None:
            return 'NONE'

        task['start_time'] = time.time()
        print('GET task {} from {}'.format(task['id'], q_name))

        return ' '.join(str(i) for i in [task['id'], task['length'], task['data']])

    def ack(self, q_name, task_id):

        try:
            q = self.queues[q_name]
        except KeyError:
            return 'NO'

        if len(q) == 0:
            return 'NO'

        task = search_in_dict(q, 'id', task_id)

        if task is None or time.time() - task['start_time'] > self.timeout:
            return 'NO'

        q.remove(task)

        print('ACK task {} from {}'.format(id, q_name))
        print(self.queues)

        return 'YES'

    def in_command(self, q_name, task_id):

        try:
            q = self.queues[q_name]
        except KeyError:
            return 'NO'

        if len(q) == 0:
            return 'NO'

        task = search_in_dict(q, 'id', task_id)

        if task is None:
            return 'NO'

        return 'YES'

    def save(self):
        if not os.path.exists(self.path):
            return 'ERROR Path do not exist'

        res = 'OK'

        data = {'queues': self.queues, 'timers': self.timers}

        try:
            with open(os.path.join(self.path, 'task_queue.dump'), 'wb') as handle:
                pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception as e:
            print(e)
            res = 'ERROR'

        print('SAVED')

        return res

    def load(self):
        if not os.path.exists(os.path.join(self.path, 'task_queue.dump')):
            return 'ERROR Dump file does not exist'

        print('LOAD from file: {}'.format(os.path.join(self.path, 'task_queue.dump')))

        with open(os.path.join(self.path, 'task_queue.dump'), 'rb') as handle:
            data = pickle.load(handle)

        self.__dict__['queues'] = data['queues']
        self.__dict__['timers'] = data['timers']

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