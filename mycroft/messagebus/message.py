# Copyright 2017 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import re
from mycroft_bus_client import Message as MycroftMessage
from mycroft_bus_client.message import dig_for_message
from mycroft.messagebus.load_config import get_bus_config
from mycroft.util.parse import normalize


class Message(MycroftMessage):
    """Mycroft specific Message class."""

    def __new__(cls, *args, **kwargs):
        bus_config = get_bus_config()
        if bus_config.get("use_chatterbox"):
            # chatterbox bus client is a drop in replacement
            # it adds functionality to encrypt payloads
            # this is done transparently from the .conf
            from chatterbox_bus_client.message import \
                Message as ChatterboxMessage
            return ChatterboxMessage(*args, **kwargs)

        # utterance_remainder is not available on mycroft-bus-client
        MycroftMessage.utterance_remainder = cls.__utterance_remainder
        return MycroftMessage(*args, **kwargs)

    def __utterance_remainder(self):
        """
        For intents get the portion not consumed by Adapt.

        For example: if they say 'Turn on the family room light' and there are
        entity matches for "turn on" and "light", then it will leave behind
        " the family room " which is then normalized to "family room".

        Returns:
            str: Leftover words or None if not an utterance.
        """
        utt = normalize(self.data.get("utterance", ""))
        if utt and "__tags__" in self.data:
            for token in self.data["__tags__"]:
                # Substitute only whole words matching the token
                utt = re.sub(r'\b' + token.get("key", "") + r"\b", "", utt)
        return normalize(utt)
