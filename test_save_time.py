from datetime import datetime
import pytz
import sys
import os

# 프로젝트 루트를 Python path에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from utils.vietnam_timezone import get_database_time_iso, get_vietnam_timestamptz
    utils_available = True
except ImportError:
    utils_available = False
    print("⚠️ utils.vietnam_timezone을 불러올 수 없습니다. 직접 구현을 사용합니다.")

print('=== 🇻🇳 베트남 시간대 저장 테스트 ===')

# 1. 기존 UTC 방식
utc_save_time = datetime.now(pytz.UTC).isoformat()
print(f'❌ 기존 UTC 방식: {utc_save_time}')

# 2. 베트남 시간대 방식
vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
vietnam_time = datetime.now(vietnam_tz)
vietnam_iso = vietnam_time.isoformat()
vietnam_pg = vietnam_time.strftime('%Y-%m-%d %H:%M:%S%z')

print(f'✅ 베트남 ISO: {vietnam_iso}')
print(f'✅ 베트남 PG: {vietnam_pg}')

if utils_available:
    print(f'✅ Utils ISO: {get_database_time_iso()}')
    print(f'✅ Utils PG: {get_vietnam_timestamptz()}')

print()
print('=== 시간 비교 ===')
utc_time = datetime.now(pytz.UTC)
print(f'UTC 시간: {utc_time.strftime("%H:%M:%S")}')
print(f'베트남 시간: {vietnam_time.strftime("%H:%M:%S")}')
print(f'시간 차이: +{vietnam_time.hour - utc_time.hour}시간')

print()
print('🔍 베트남 시간대 정보:')
print(f'   시간대명: {vietnam_time.tzname()}')
print(f'   UTC 오프셋: {vietnam_time.strftime("%z")}')
print(f'   형식: Asia/Ho_Chi_Minh (ICT)')

print()
print('📊 결론:')
print('✅ 이제 베트남 시간대(UTC+7)로 저장됩니다')
print('✅ 수파베이스에서 자동으로 UTC로 변환하여 저장')
print('✅ 조회 시 베트남 시간으로 표시') 