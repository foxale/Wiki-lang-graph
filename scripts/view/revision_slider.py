import numbers
from datetime import date
from datetime import datetime

from bokeh.core.property.datetime import Datetime
from bokeh.core.property.override import Override
from bokeh.core.property.primitive import Int
from bokeh.models import AbstractSlider


class RevisionSlider(AbstractSlider):
    """ Slider-based date selection widget. """

    def __init__(self, **kwargs):
        self._data = kwargs.pop('data')
        super().__init__(**kwargs)

    @property
    def value_as_datetime(self):
        """ Convenience property to retrieve the value as a datetime object.

        Added in version 2.0
        """
        if self.value is None:
            return None

        if isinstance(self.value, numbers.Number):
            return datetime.utcfromtimestamp(self.value / 1000)

        return self.value

    @property
    def value_as_date(self):
        """ Convenience property to retrieve the value as a date object.

        Added in version 2.0
        """
        if self.value is None:
            return None

        if isinstance(self.value, numbers.Number):
            dt = datetime.utcfromtimestamp(self.value / 1000)
            return date(*dt.timetuple()[:3])

        return self.value

    value = Datetime(help="""
    Initial or selected value.
    """)

    value_throttled = Datetime(help="""
    Initial or selected value, throttled to report only on mouseup.
    """)

    start = Datetime(help="""
    The minimum allowable value.
    """)

    end = Datetime(help="""
    The maximum allowable value.
    """)

    step = Int(default=1, help="""
    The step between consecutive values.
    """)

    format = Override(default="%d %b %Y")
