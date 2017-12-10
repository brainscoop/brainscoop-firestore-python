import argparse
import command
import errno
import firebase_admin
import json
import logging
import os
import sys
from firebase_admin import credentials
from firebase_admin import firestore


class HelpFormatter(argparse.HelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):
        prefix = 'Usage: '
        usage = '%(prog)s [options] [command]'
        return super(HelpFormatter, self).add_usage(
            usage, actions, groups, prefix
        )


def parse_firebase_rc(firebaserc):
    try:
        return json.load(open(firebaserc))
    except IOError, err:
        if err.errno == errno.ENOENT:
            print('{}. Please run "firebase init" first '
                  'or specify environment with option '
                  '"-e" or "--env").'.format(err))
        else:
            print(err)
        sys.exit(1)


def parse_opts():
    parser = argparse.ArgumentParser(formatter_class=HelpFormatter)
    parser.add_argument('-p', '--project',
                        help='firebase project name.')
    parser.add_argument('-e', '--env',
                        help='.firebaserc path.',
                        default=os.path.abspath('.firebaserc'))
    parser.add_argument('-k', '--key',
                        help='client secret file path (json).',
                        default=os.path.abspath('client-secret.json'))
    parser.add_argument('-v', '--verbose', action='store_true')
    subparsers = parser.add_subparsers(dest='command')

    # create the parser for the "bootstrap" command.
    bootstrap_group = subparsers.add_parser('bootstrap')
    bootstrap_group.add_argument('-n', '--num', default=10, type=int)
    bootstrap_group.set_defaults(func=command.bootstrap,
                                 schema=os.path.abspath('schema'))

    # create the parser for the "delete" command.
    delete_group = subparsers.add_parser('delete')
    delete_group.add_argument('path')
    delete_group.set_defaults(func=command.delete)

    # create the parser for the "dump" command.
    dump_group = subparsers.add_parser('dump')
    dump_group.add_argument('path')
    dump_group.set_defaults(func=command.dump)

    # create the parser for the "update" command.
    update_group = subparsers.add_parser('update')
    update_group.add_argument('path')
    update_group.add_argument('-f', '--field', type=str)
    update_group.set_defaults(func=command.update)

    return parser.parse_args(sys.argv[1:])


def create_db(project, key):
    try:
        cred = credentials.Certificate(key)
        firebase_admin.initialize_app(cred, {
            'projectId': project
        })
        return firestore.client()
    except IOError, err:
        if err.errno == errno.ENOENT:
            print('{}. Please specify key with option '
                  '"-k" or "--key".'.format(err))
        else:
            print(err)
        sys.exit(1)


def main():
    opts = parse_opts()
    if opts.verbose:
        logging.basicConfig(format='%(message)s', level=logging.INFO)
    if not opts.project:
        rc = parse_firebase_rc(opts.env)
        try:
            opts.project = rc['projects']['default']
        except KeyError:
            print('No default firebase project found in ".firebaserc". '
                  'Please specify project using "-p" or "--project" option.')
            sys.exit(1)
    try:
        db = create_db(opts.project, opts.key)
        opts.func(db, opts)
    except Exception, err:
        if hasattr(err, 'details'):
            print'{}'.format(err.details())
        else:
            print err
        sys.exit(1)


if __name__ == '__main__':
    main()
