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
import os
import sys

import pinboard

import pkg_resources

from pocket2pinboard import auth
from pocket2pinboard import bookmarks
from pocket2pinboard import config
from pocket2pinboard import keys
from pocket2pinboard import retrieve

LOG = logging.getLogger(__name__)


def main():
    # Load the configuration file and determine default values for a
    # few parameters.
    config_name = os.path.expanduser('~/.pocket2pinboardrc')
    cfg = config.read(config_name)
    since = cfg.get('history', 'since')
    pinboard_token = cfg.get('pinboard', 'token')
    if not pinboard_token:
        # Save the skeleton file to make editing it easier later.
        config.save(cfg, config_name)

    # Handle command line arguments.
    parser = argparse.ArgumentParser()
    dist = pkg_resources.get_distribution('pocket2pinboard')
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s {0}'.format(dist.version),
    )
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

    # Make sure we know how to talk to pinboard.in.
    if not args.pinboard_token:
        parser.error(
            'Please update the pinboard token in %s or provide one via -t'
            % config_name)

    # Set up logging for use as output channel.
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(message)s',
    )
    if not args.verbose:
        requests_logger = logging.getLogger('requests')
        requests_logger.setLevel(logging.WARNING)

    try:
        # Connect to both services early to find authentication
        # issues.
        access_token = auth.authenticate(keys.consumer_key)
        pinboard_client = pinboard.Pinboard(args.pinboard_token)

        # Get a list of the pocket items we are going to process.
        if args.all:
            since = None
        if since:
            LOG.info('loading pocket items since %s',
                     datetime.datetime.fromtimestamp(float(since)))
        else:
            LOG.info('fetching all pocket items')

        items, new_since = retrieve.get_items(
            keys.consumer_key,
            access_token,
            since,
        )

        # Send the pocket items to pinboard.
        bookmarks.update(pinboard_client, items)

        # Remember the new value for 'since'.
        config.save(cfg, config_name, new_since)
    except Exception as e:
        if args.verbose:
            raise
        parser.error(e)
        sys.exit(1)
