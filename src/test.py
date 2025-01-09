from datetime import datetime
import pytz

timezone = pytz.timezone('Asia/Ho_Chi_Minh')

current_time_gmt7 = datetime.now(timezone)

print("Current time in GMT+7:", current_time_gmt7)