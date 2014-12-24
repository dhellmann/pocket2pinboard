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

import datetime
import logging

LOG = logging.getLogger(__name__)


def update(pinboard_client, items):
    for i in items:
        tags = i.get('tags', {}).keys()
        if not tags:
            # Skip anything that isn't tagged.
            continue
        title = (i.get('resolved_title') or u'No title').encode('utf-8')
        time_updated = datetime.datetime.fromtimestamp(
            float(i['time_updated'])
        )
        extended = i.get('excerpt', u'').encode('utf-8')
        LOG.info('%s: %s' % (title, tags))
        LOG.debug('URL %s', i['given_url'])
        LOG.debug('Description: %r', title)
        LOG.debug('Tags: %r', tags)
        LOG.debug('Date: %s', time_updated.date())
        pinboard_client.posts.add(
            url=i['given_url'],
            description=title,
            extended=extended,
            tags=u', '.join(tags),
            date=str(time_updated.date()),
        )
        LOG.debug('')
