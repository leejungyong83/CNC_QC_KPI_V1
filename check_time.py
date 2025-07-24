from datetime import datetime
import pytz

utc_time = datetime.now(pytz.UTC)
vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
vietnam_time = datetime.now(vietnam_tz)

print('현재 UTC:', utc_time.strftime('%H:%M'))
print('현재 베트남:', vietnam_time.strftime('%H:%M'))
print('수파베이스 데이터: 10:06')
print()
print('문제:', '현재 UTC가 10시가 아님' if utc_time.hour != 10 else 'UTC 시간 일치')
print(f'UTC 시각: {utc_time.hour}시')
print('수파베이스: 10시') 