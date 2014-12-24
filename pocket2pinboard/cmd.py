# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function

import argparse
import datetime
import logging
import sys

import pinboard

from pocket2pinboard import auth
from pocket2pinboard import keys
from pocket2pinboard import retrieve


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v',
                        dest='verbose',
                        action='store_true',
                        default=False,
                        help='provide verbose output',
                        )
    parser.add_argument('--all',
                        action='store_true',
                        default=False,
                        help='process all pocket articles',
                        )
    parser.add_argument(
        '--pinboard-token', '-t',
        help='pinboard.in API token',
        required=True,
    )
    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(message)s',
    )

    if not args.verbose:
        requests_logger = logging.getLogger('requests')
        requests_logger.setLevel(logging.WARNING)

    try:
        access_token = auth.authenticate(keys.consumer_key)
    except auth.AuthError as e:
        print(e)
        sys.exit(1)

    pinboard_client = pinboard.Pinboard(args.pinboard_token)

    if args.all:
        since = None
    else:
        since = '1419434347'
    items_response = retrieve.get_items(keys.consumer_key, access_token, since)
    print(items_response['since'])
    items = items_response['list']
    if isinstance(items, dict):
        items = items.values()

    for i in items:
        tags = i.get('tags', {}).keys()
        if not tags:
            # Skip anything that isn't tagged.
            continue
        print('%s: %s' % (i['resolved_title'], tags))
        time_updated = datetime.datetime.fromtimestamp(float(i['time_updated']))
        pinboard_client.posts.add(
            url=i['given_url'],
            description=i['resolved_title'],
            #extended=i['excerpt'],
            tags=u', '.join(tags),
            date=str(time_updated.date()),
        )
        print('')
