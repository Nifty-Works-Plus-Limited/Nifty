from datetime import datetime
import pytz


def get_current_time():
    nairobiTimeZone = pytz.timezone("Africa/Nairobi")
    timeInNairobi = datetime.now(nairobiTimeZone)
    return timeInNairobi
