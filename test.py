from datetime import datetime
from datetime import timedelta

print((datetime.now() + timedelta(hours=12)).strftime("%H:%S"))