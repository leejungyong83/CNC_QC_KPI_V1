from utils.data_converter import convert_supabase_data_timezone
from datetime import datetime

print('=== 시간대 변환 테스트 ===')

# 1. 수파베이스에서 가져온 샘플 데이터 (UTC)
sample_data = [
    {
        'id': 'test-id',
        'defect_type': '작업불량',
        'created_at': '2025-07-23T10:06:45.457758+00:00',  # 수파베이스의 실제 데이터
        'description': 'test'
    }
]

print('1. 원본 데이터 (수파베이스에서 가져온 UTC):')
print(f"   created_at: {sample_data[0]['created_at']}")

# 2. 변환 적용
converted_data = convert_supabase_data_timezone(sample_data)

print()
print('2. 변환된 데이터 (베트남 시간):')
print(f"   created_at: {converted_data[0]['created_at']}")

# 3. 예상 결과 계산
utc_str = '2025-07-23T10:06:45'
expected_vietnam = '2025-07-23 17:06:45'  # UTC + 7시간

print()
print('3. 예상 vs 실제:')
print(f'   예상 베트남 시간: {expected_vietnam}')
print(f'   실제 변환 결과: {converted_data[0]["created_at"]}')

# 4. 변환 성공 여부 확인
if '17:06' in str(converted_data[0]['created_at']):
    print('✅ 시간대 변환 성공!')
else:
    print('❌ 시간대 변환 실패')

print()
print('🎯 결론:')
print('- 수파베이스 저장: UTC (정상)')
print('- 앱 표시: 베트남 시간으로 변환 확인 필요') 