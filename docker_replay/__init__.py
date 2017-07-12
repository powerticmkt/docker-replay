import os
import sys
import logging
from argparse import ArgumentParser

from docker_replay import version

log = logging.getLogger('docker-replay')

class DockerReplay(object):
    def __init__(self, container_id, pretty_print=True):
        from docker import client, errors
        from docker_replay.opts import OptionParser

        self.pretty_print = pretty_print

        client_args = { 'version': 'auto' }
        if os.getenv('DOCKER_HOST'):
            client_args['base_url'] = os.getenv('DOCKER_HOST')

        try:
            inspect = client.APIClient(**client_args).inspect_container(container_id)
            self.parser = OptionParser(inspect)
        except errors.NotFound:
            print('no such container: %s' % container_id)
            sys.exit(1)

    def __str__(self):
        opts = sorted([ str(o) for o in self.parser.opts if not o.is_null() ])
        opts += [ str(a) for a in self.parser.args if not a.is_null() ]

        if self.pretty_print:
            return 'docker run %s' % ' \\\n           '.join(opts)
        return 'docker run %s' % ' '.join(opts)

def main():
    argparser = ArgumentParser(description='docker-replay v%s' % version)
    argparser.add_argument('-d', '--debug', action='store_true',
                            help='enable debug output')
    argparser.add_argument('-p', '--pretty-print', action='store_true',
                            help='pretty-print output')
    argparser.add_argument('container',
                            help='container to generate command from')
    args = argparser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARN)

    print(DockerReplay(args.container, args.pretty_print))
