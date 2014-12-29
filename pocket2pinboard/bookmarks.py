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

import logging

LOG = logging.getLogger(__name__)


def update(pinboard_client, items):
    for i in items:
        if not i.tags:
            # Skip anything that isn't tagged.
            continue
        LOG.info('%s - %s: %s' % (i.time_updated.date(), i.title, i.tags))
        LOG.debug('%r', i)
        pinboard_client.posts.add(
            url=i.url,
            description=i.title,
            extended=i.excerpt,
            tags=u', '.join(i.tags),
            date=str(i.time_updated.date()),
        )
        LOG.debug('')
