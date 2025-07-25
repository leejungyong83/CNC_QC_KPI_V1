from datetime import datetime
import pytz

print("=== 🔍 Supabase UTC 저장 분석 ===")

# 스크린샷의 시간 분석 (09:33:20)
vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
utc_933 = datetime(2025, 7, 24, 9, 33, 20, tzinfo=pytz.UTC)
vietnam_933 = utc_933.astimezone(vietnam_tz)

print("📊 스크린샷 시간:")
print(f"   Supabase 표시: 09:33:20 UTC")
print(f"   베트남 변환: {vietnam_933.strftime('%H:%M:%S')} ICT")
print(f"   시간차: +{vietnam_933.hour - utc_933.hour}시간")

print()
print("=== 현재 시간 비교 ===")
utc_now = datetime.now(pytz.UTC)
vietnam_now = datetime.now(vietnam_tz)

print(f"현재 UTC: {utc_now.strftime('%H:%M:%S')}")
print(f"현재 베트남: {vietnam_now.strftime('%H:%M:%S')}")

print()
print("✅ 결론:")
print("- PostgreSQL TIMESTAMPTZ는 항상 UTC로 저장")
print("- Supabase UI는 UTC로 표시 (정상)")
print("- 앱에서 베트남 시간으로 입력 → UTC 변환 저장")
print("- 조회 시 베트남 시간으로 표시하면 OK") 