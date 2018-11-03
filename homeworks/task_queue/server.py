# -*- coding: utf-8 -*-
import argparse
import queue
import socket


class TaskQueueServer:

    def __init__(self, ip='127.0.0.1', port=5555, path='', timeout=300):
        self.ip = ip
        self.port = port
        self.path = path
        self.timeout = timeout
        self.queues = []

    def add(self, q_name, length, data):
        # filter (lambda x: x['name']==data[0],self.queues)
        q = self.search_in_dict(self.queues, 'name', q_name)
        if q == None:
            self.queues.append({'name': q_name, 'q': []})
            q = self.queues[-1]

        # TODO: генерация id
        id = '111'

        q['q'].append({'id': id, 'data': data, 'length': length})
        return id

    def search_in_dict(self, source, key_name, value):
        for i in source:
            if i[key_name] == value:
                return i
        return None

    def get(self, q_name):
        q = self.search_in_dict(self.queues, 'name', q_name)
        if q == None or len(q['q']) == 0:
            return 'NONE'
        task = q['q'][-1]
        return ' '.join(str(i) for i in task.values())

    def ack(self, q_name, task_id):
        q = self.search_in_dict(self.queues, 'name', q_name)
        if q == None or len(q['q']) == 0:
            return 'NONE'
        task = self.search_in_dict(q['q'], 'id', task_id)
        if task is None:
            return 'NO'
        q['q'].pop()
        return 'YES'

    def in_command(self, q_name, task_id):
        q = self.search_in_dict(self.queues, 'name', q_name)
        if q == None or len(q['q']) == 0:
            return 'NONE'
        task = self.search_in_dict(q['q'], 'id', task_id)
        if task is None:
            return 'NO'
        return 'YES'
        pass

    def save(self):
        # объект self.queues записать в файл
        pass

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((self.ip, self.port))
            sock.listen(1)
            conn, addr = sock.accept()
            print('connected:', addr)
            while True:
                data = conn.recv(1024).decode()
                if not data:
                    break
                # наша обработка
                data = data.split()
                if data[0] == 'ADD':
                    res = self.add(data[1], data[2], data[3])
                    conn.send(res.encode())
                elif data[0] == 'GET':
                    res = self.get(data[1])
                    conn.send(res.encode())
                elif data[0] == 'ACK':
                    res = self.ack(data[1], data[2])
                    conn.send(res.encode())
                elif data[0] == 'IN':
                    res = self.in_command(data[1], data[2])
                    conn.send(res.encode())
                elif data[0] == 'SAVE':
                    res = self.save()
                    conn.send(res.encode())
                else:
                    conn.send('ERROR'.encode())
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
