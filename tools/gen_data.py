
import argparse
from datetime import datetime
import requests
import base64
import random


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--uri', action='store',
                        default='http://localhost:6892/intake',
                        help='The uri to make HTTP POST requests to')
    parser.add_argument('--count', action='store', default=1, type=int,
                        help='How many log entry to post.')
    parser.add_argument('--username', action='store',
                        help='The username to send as part of Basic '
                             'authentication')
    parser.add_argument('--password', action='store',
                        help='The password to send as part of Basic '
                             'authentication')
    parser.add_argument('--servers', '--hostnames', action='store',
                        default='host1234',
                        help='A comma-separated list of servers to randomly '
                             'select from for each log entry added')
    parser.add_argument('--log-names', '--sources', action='store',
                        default='/var/log/application.log',
                        help='A comma-separated list of log names to randomly '
                             'select from for each log entry added')

    args = parser.parse_args()

    template = '''{{
    "@timestamp": "{}",
    "source": "{}",
    "host": "{}",
    "message": "{}"
    }}'''

    uri = args.uri
    count = args.count
    username = args.username
    password = args.password
    auth = 'Basic ' + base64.b64encode('{}:{}'.format(username, password))
    servers = list(filter(None, args.servers.split(',')))
    if not servers:
        servers = ['host1234']
    log_names = list(filter(None, args.log_names.split(',')))
    if not log_names:
        log_names = ['/var/log/application.log']
    print('uri: {}'.format(uri))
    print('count: {}'.format(count))
    print('username: {}'.format(username))
    print('password: {}'.format(password))
    print(' -> auth: {}'.format(auth))
    print('servers: {}'.format(servers))
    print('log names: {}'.format(log_names))
    for i in xrange(count):
        timestamp = datetime.utcnow()
        source = random.choice(log_names)
        hostname = random.choice(servers)
        message = 'this is the message'
        payload = template.format(timestamp, source, hostname, message)
        resp = requests.post(
            uri,
            data=payload,
            allow_redirects=False,
            headers={
                'Authorization': auth,
                'Content-type': 'application/json'})
        assert 200 <= resp.status_code < 300
        print 'posted an entry: {}, {}, {}, {}'.format(timestamp, source,
                                                       hostname, message)

if __name__ == '__main__':
    run()
