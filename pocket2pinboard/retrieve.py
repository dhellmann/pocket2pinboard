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

import collections
import datetime
import logging

import requests


LOG = logging.getLogger(__name__)


_url = 'https://getpocket.com/v3/get'
_headers = {
    'X-Accept': 'application/json',
}


PocketItem = collections.namedtuple(
    'PocketItem',
    ['url', 'title', 'excerpt', 'time_updated', 'tags']
)


def make_pocket_item(i):
    tags = i.get('tags', {}).keys()
    title = (i.get('resolved_title') or u'No title').encode('utf-8')
    time_updated = datetime.datetime.fromtimestamp(
        float(i['time_updated'])
    )
    excerpt = i.get('excerpt', u'').encode('utf-8')
    return PocketItem(
        url=i['resolved_url'],
        title=title,
        excerpt=excerpt,
        time_updated=time_updated,
        tags=tags,
    )


def get_items(consumer_key, access_token, since):
    payload = {
        'consumer_key': consumer_key,
        'access_token': access_token,
        'state': 'all',
        'detailType': 'complete',
    }
    if since:
        payload['since'] = since
    response = requests.post(_url, data=payload, headers=_headers)
    if response.status_code == 200:
        data = response.json()
        new_since = data['since']
        items = data['list']
        # If the list is empty, we get a list. If it has values, it is a
        # dictionary mapping ids to contents. We want to iterate over all
        # of them, so just make a list of the values.
        if isinstance(items, dict):
            items = list(items.values())
        return ((make_pocket_item(i) for i in items), new_since)
    raise RuntimeError('could not retrieve: %s: %s' %
                       (response.status_code, response.text))
