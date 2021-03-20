import pytz
from datetime import datetime
from datetime import timedelta

timezone = pytz.timezone('Europe/Kiev')

result = datetime.now(pytz.timezone('Europe/Kiev')).strftime("%H:%M")

print(result + timedelta(hours=2))