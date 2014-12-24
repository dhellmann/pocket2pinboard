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

import ConfigParser


def read(config_name):
    """Given a filename, read the configuration."""
    cfg = ConfigParser.SafeConfigParser()
    cfg.read(config_name)
    if not cfg.has_section('pinboard'):
        cfg.add_section('pinboard')
    if not cfg.has_option('pinboard', 'token'):
        cfg.set('pinboard', 'token', '')
    if not cfg.has_section('history'):
        cfg.add_section('history')
    if not cfg.has_option('history', 'since'):
        cfg.set('history', 'since', '')
    return cfg


def save(cfg, config_name, since=None):
    """Write a new config file, including an update to 'since' if needed."""
    if since:
        cfg.set('history', 'since', str(since))
    with open(config_name, 'w') as f:
        cfg.write(f)
