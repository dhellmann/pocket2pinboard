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
import ConfigParser
import datetime
import logging
import os
import sys

import pinboard

from pocket2pinboard import auth
from pocket2pinboard import keys
from pocket2pinboard import retrieve


def read_config(config_name):
    config = ConfigParser.SafeConfigParser()
    config.read(config_name)
    if not config.has_section('pinboard'):
        config.add_section('pinboard')
    if not config.has_option('pinboard', 'token'):
        config.set('pinboard', 'token', '')
    if not config.has_section('history'):
        config.add_section('history')
    if not config.has_option('history', 'since'):
        config.set('history', 'since', '')
    return config


def save_config(config, config_name, since=None):
    if since:
        config.set('history', 'since', str(since))
    with open(config_name, 'w') as f:
        config.write(f)


def main():
    # Load the configuration file.
    config_name = os.path.expanduser('~/.pocket2pinboardrc')
    config = read_config(config_name)
    since = config.get('history', 'since')
    pinboard_token = config.get('pinboard', 'token')
    if not pinboard_token:
        # Save the skeleton file to make editing it easier later.
        save_config(config, config_name)

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
        default=pinboard_token,
        help='pinboard.in API token',
    )
    args = parser.parse_args()

    if not args.pinboard_token:
        parser.error('Please update the pinboard token in %s or provide one via -t' % config_name)

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

    items_response = retrieve.get_items(keys.consumer_key, access_token, since)
    items = items_response['list']
    # If the list is empty, we get a list. If it has values, it is a
    # dictionary mapping ids to contents. We want to iterate over all
    # of them, so just make a list.
    if isinstance(items, dict):
        items = items.values()

    for i in items:
        tags = i.get('tags', {}).keys()
        if not tags:
            # Skip anything that isn't tagged.
            continue
        title = (i.get('resolved_title') or u'No title').encode('utf-8')
        time_updated = datetime.datetime.fromtimestamp(float(i['time_updated']))
        extended = i.get('excerpt', u'').encode('utf-8')
        print('%s: %s' % (title, tags))
        # print(dict(
        #     url=i['given_url'],
        #     description=i['resolved_title'],
        #     #extended=i['excerpt'],
        #     tags=u', '.join(tags),
        #     date=str(time_updated.date()),
        # ))
        pinboard_client.posts.add(
            url=i['given_url'],
            description=title,
            extended=extended,
            tags=u', '.join(tags),
            date=str(time_updated.date()),
        )
        print('')

    save_config(config, config_name, items_response['since'])
