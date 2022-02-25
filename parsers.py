import datetime

from django.conf import settings
from django.utils import timezone

def parser_datetime(value, format='%Y-%m-%d %H:%M:%S', *, align=None, aware=settings.USE_TZ):
    parsed = datetime.datetime.strptime(value, format)

    if align == "start":
        parsed = parsed.replace(hour=0, minute=0, second=0)
    elif align == "end":
        parsed = parsed.replace(hour=23, minute=59, second=59)

    if aware:
        parsed = timezone.make_aware(parsed)

    return parsed
