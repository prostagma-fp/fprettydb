# Metadata to pass from get_web_meta().
import fpclib

MONTHS = fpclib.MONTHS

class Curation():
        
    def __init__(self, **kwargs):
        self.meta = {
            'developer': None,
            'releaseDate': None,
            'originalDescription': None#,
            #'language': None
        }
    
    def get_meta(self):
        """Returns all parameters from the Curation object's "meta" variable.
        """
        return self.meta

    def parse(self, s):
        """Uses this date format object to parse the given string :code:`s` into a proper iso date.
        
        :param str s: A string to parse for a date.
        
        :returns: An iso date parsed from string :code:`s`
        
        :raises ValueError: if no date in :code:`s` could be found.
        """
        match = self.format.search(s)
        if not match: raise ValueError(f'No date in "{s}"')
        
        y = match["year"]
        if not y: raise ValueError(f'No year in "{s}"')
        try: m = match["month"]
        except IndexError: m = None
        try: d = match["day"]
        except IndexError: d = None
        
        if d and not m: raise ValueError(f'Day but no month in "{s}"')
        
        if self.year:
            year = self.year(y).zfill(4)
        else:
            year = y.zfill(4)
        
        if m:
            if self.month:
                month = "-" + self.month(m).zfill(2)
            else:
                month = "-" + m.zfill(2)
        else:
            month = ""
        
        if d:
            if self.day:
                day = "-" + self.day(d).zfill(2)
            else:
                day = "-" + d.zfill(2)
        else:
            day = ""
        
        return year + month + day

DP_US = fpclib.DP_US
"""A :class:`DateParser` that parses dates in the american format of "March 5th, 2016", "3/5/2016", "March 2016" or similar."""
DP_UK = fpclib.DP_UK
"""A :class:`DateParser` that parses dates in the european format of "5th of March, 2016", "5/3/2016", "March 2016" or similar."""
DP_ISO = fpclib.DP_ISO
"""A :class:`DateParser` that parses dates in the format of "2016 March 5th" or similar."""