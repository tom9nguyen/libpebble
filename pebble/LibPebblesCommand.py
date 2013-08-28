import sh, os
import websocket
import logging
import time
from autobahn.websocket import *
from PblCommand import PblCommand
import pebble as libpebble
from EchoServerProtocol import *

class LibPebbleCommand(PblCommand):
    def configure_subparser(self, parser):
        pass

    def run(self, args):
        echo_server_start(libpebble.DEFAULT_PEBBLE_PORT)
        self.pebble = libpebble.Pebble(using_lightblue=False, pair_first=False, using_ws=True)

class PblServerCommand(LibPebbleCommand):
    name = 'server'
    help = 'Run a websocket server to keep the connection to your phone and Pebble opened.'

    def configure_subparser(self, parser):
        PblCommand.configure_subparser(self, parser)

    def run(self, args):
        logging.info("Starting a Pebble WS server on port {}".format(libpebble.DEFAULT_PEBBLE_PORT))
        logging.info("Type Ctrl-C to interrupt.")
        echo_server_start(libpebble.DEFAULT_PEBBLE_PORT, blocking=True)

class PblPingCommand(LibPebbleCommand):
    name = 'ping'
    help = 'Ping your Pebble project to your watch'

    def configure_subparser(self, parser):
        PblCommand.configure_subparser(self, parser)

    def run(self, args):
        LibPebbleCommand.run(self, args)
        self.pebble.ping(cookie=0xDEADBEEF)


class PblInstallCommand(LibPebbleCommand):
    name = 'install'
    help = 'Install your Pebble project to your watch'

    def configure_subparser(self, parser):
        PblCommand.configure_subparser(self, parser)
        parser.add_argument('bundle', type=str)
        parser.add_argument('--logs', action='store_true', help='Display logs after installing the app')

    def run(self, args):
        LibPebbleCommand.run(self, args)
        self.pebble.reinstall_app(args.bundle, True)

        if args.logs:
            logging.info('Displaying logs ... Ctrl-C to interrupt.')
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                return


class PblListCommand(LibPebbleCommand):
    name = 'list'
    help = 'List the apps installed on your watch'

    def configure_subparser(self, parser):
        PblCommand.configure_subparser(self, parser)

    def run(self, args):
        LibPebbleCommand.run(self, args)

        apps = self.pebble.get_appbank_status()
        if apps is not False:
            for app in apps['apps']:
                logging.info('[{}] {}'.format(app['index'], app['name']))
        else:
            logging.info("No apps.")


class PblRemoveCommand(LibPebbleCommand):
    name = 'rm'
    help = 'Remove an app from your watch'

    def configure_subparser(self, parser):
        PblCommand.configure_subparser(self, parser)
        parser.add_argument('bank_id', type=int, help="The bank id of the app to remove (between 1 and 8)")

    def run(self, args):
        LibPebbleCommand.run(self, args)

        for app in self.pebble.get_appbank_status()['apps']:
            if app['index'] == args.bank_id:
                self.pebble.remove_app(app["id"], app["index"])
                logging.info("App removed")
                return 0


class PblLogsCommand(LibPebbleCommand):
    name = 'logs'
    help = 'Continuously displays logs from the watch'

    def configure_subparser(self, parser):
        PblCommand.configure_subparser(self, parser)

    def run(self, args):
        LibPebbleCommand.run(self, args)

        logging.info('Displaying logs ... Ctrl-C to interrupt.')
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            return
