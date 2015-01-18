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


_DEFAULTS = [
    ('pinboard', 'token', ''),
    ('pocket', 'token', ''),
    ('history', 'since', ''),
]

def read(config_name):
    """Given a filename, read the configuration."""
    cfg = ConfigParser.SafeConfigParser()
    cfg.read(config_name)
    for s, o, v in _DEFAULTS:
        if not cfg.has_section(s):
            cfg.add_section(s)
        if not cfg.has_option(s, o):
            cfg.set(s, o, v)
    return cfg


def save(cfg, config_name):
    """Write a new config file."""
    with open(config_name, 'w') as f:
        cfg.write(f)
