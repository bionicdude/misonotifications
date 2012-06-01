import datetime
import string
import re


class listRotator:
    def __init__(self, ilistsize):
        self.listsize=ilistsize
        self.lrtext=" "
    def AddString(self, sStringToAdd):
        self.lrtext=(self.lrtext+'\n'+datetime.datetime.now().strftime("%Y-%m-%d %H:%M")+': '+sStringToAdd).lstrip()
        if self.lrtext.count('\n') > self.listsize-1:
          a = self.lrtext[self.lrtext.find('\n')+1:]
          self.lrtext=a.strip()
    def atext(self):
        return self.lrtext


def parse_timestamp(s):
  """Returns (datetime, tz offset in minutes) or (None, None)."""
  m = re.match(""" ^
    (?P<year>-?[0-9]{4}) - (?P<month>[0-9]{2}) - (?P<day>[0-9]{2})
    T (?P<hour>[0-9]{2}) : (?P<minute>[0-9]{2}) : (?P<second>[0-9]{2})
    (?P<microsecond>\.[0-9]{1,6})?
    (?P<tz>
      Z | (?P<tz_hr>[-+][0-9]{2}) : (?P<tz_min>[0-9]{2})
    )?
    $ """, s, re.X)
  if m is not None:
    values = m.groupdict()
    if values["tz"] in ("Z", None):
      tz = 0
    else:
      tz = int(values["tz_hr"]) * 60 + int(values["tz_min"])
    if values["microsecond"] is None:
      values["microsecond"] = 0
    else:
      values["microsecond"] = values["microsecond"][1:]
      values["microsecond"] += "0" * (6 - len(values["microsecond"]))
    values = dict((k, int(v)) for k, v in values.iteritems()
                  if not k.startswith("tz"))
    try:
      return datetime.datetime(**values)
    except ValueError:
      pass
  return None
