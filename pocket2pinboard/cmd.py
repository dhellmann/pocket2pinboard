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
import logging
import sys

from pocket2pinboard import auth
from pocket2pinboard import keys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v',
                        dest='verbose',
                        action='store_const',
                        default=False,
                        const=True
                        )
    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(message)s',
    )

    requests_logger = logging.getLogger('requests')
    requests_logger.setLevel(logging.WARNING)

    try:
        auth_response = auth.authenticate(keys.consumer_key)
    except auth.AuthError as e:
        print(e)
        sys.exit(1)
