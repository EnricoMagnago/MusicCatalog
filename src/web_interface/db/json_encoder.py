from flask.json import JSONEncoder
from db.music_sheet import MusicSheet


class GBCJSONEncoder(JSONEncoder):
    """Extend base flask JSONEncoder to serialise MusicSheet objects"""

    def default(self, obj):
        retval = None
        if isinstance(obj, MusicSheet):
            retval = {
                'title': obj.title,
                'composer': obj.composer,
                'arranger': obj.arranger,
                'date_added': obj.date_added,
                'instruments': obj.instruments
            }
        else:
            retval = super(GBCJSONEncoder, self).default(obj)
        return retval
