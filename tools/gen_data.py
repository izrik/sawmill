
import argparse
from datetime import datetime
import requests
import base64


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
    for i in xrange(count):
        timestamp = datetime.utcnow()
        source = '/var/log/application.log'
        hostname = 'host1234'
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
        print 'posted an entry'

if __name__ == '__main__':
    run()
