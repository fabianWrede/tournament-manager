import json
import sys

from data.model import BaseData, Tournament, Team, Round, Game


class DataJSONEncoder(json.JSONEncoder):
    # pylint: disable=E0202
    def default(self, obj):
        if isinstance(obj, BaseData):
            return obj.encode_json()
        return json.JSONEncoder.default(self, obj)


def decode_data_json(dct):
    if '_type' in dct:
        cls = getattr(sys.modules[__name__], dct.get('_type'))
        return cls.decode_json(dct)
    return dct
