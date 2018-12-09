import os
import sys
import yaml
import argparse

import aiohttp
import asyncio
import aiofiles
from aiohttp import web


class AsyncStorage:
    def __init__(self, config='config.yml'):
        if not os.path.isfile(config):
            raise TypeError("Config file doesn't exist!")

        with open(config, 'rt') as f:
            data = yaml.load(f)

        if not os.path.isdir(data['path']):
            raise TypeError("Path doesn't exist!")

        self.host = data['host']
        self.port = data['port']
        self.path = data['path']
        self.nodes = data['nodes']
        self.do_save_files = data['do_save_files']
        self.file_text = None

    def start(self):
        app = web.Application()
        app.add_routes([
            web.get('/{filename}', self.handle)
        ])

        return app, self.host, self.port

    async def read_file(self, file_path):
        async with aiofiles.open(file_path, mode='r') as f:
            content = await f.read()
        return content

    async def write_file(self, file_path, data):
        async with aiofiles.open(file_path, mode='w') as f:
            await f.write(data)

    async def ask_node(self, session, url):
        async with session.get(url) as response:
            if response.status == 200:
                self.file_text = await response.text()

    async def handle(self, request):
        filename = request.match_info.get('filename')
        file_path = os.path.join(self.path, filename)

        if os.path.isfile(file_path):
            content = await self.read_file(file_path)
            return web.Response(text=content)
        else:
            self.file_text = None

            if self.nodes is None:
                return web.Response(status=404, text='Not Found')

            tasks = []
            async with aiohttp.ClientSession() as session:
                for node in self.nodes:
                    node_url = 'http://{}:{}/{}'.format(node['host'], node['port'], filename)
                    tasks.append(asyncio.ensure_future(self.ask_node(session, node_url)))

                await asyncio.gather(*tasks)

            if self.file_text is None:
                return web.Response(status=404, text='Not Found')
            else:
                if self.do_save_files:
                    await self.write_file(file_path, self.file_text)
                return web.Response(text=self.file_text)


def parse_args(args):
    parser = argparse.ArgumentParser(description='Async File Storage')
    parser.add_argument(
        '-c', '--config',
        action="store",
        dest="config",
        default='config.yml',
        help='Path to your config file')
    return parser.parse_args(args)


def main():
    params = parse_args(sys.argv[1:])
    storage = AsyncStorage(config=params.config)
    app, host, port = storage.start()
    web.run_app(app, host=host, port=port)


if __name__ == '__main__':
    main()
