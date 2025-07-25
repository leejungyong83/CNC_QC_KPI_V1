"""
기존 검사 데이터에 교대조 정보 추가 스크립트
- inspection_data 테이블의 기존 데이터에 shift 컬럼 값 추가
- created_at 기준으로 교대조 자동 계산
"""

from utils.supabase_client import get_supabase_client
from utils.shift_manager import get_shift_for_time
from utils.vietnam_timezone import get_vietnam_now
from datetime import datetime
import pytz

def update_existing_shift_data():
    """기존 검사 데이터에 교대조 정보 추가"""
    print("🔄 기존 검사 데이터에 교대조 정보 추가 시작...")
    
    try:
        supabase = get_supabase_client()
        vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        
        # shift 정보가 없는 데이터 조회
        result = supabase.table('inspection_data') \
            .select('id, created_at') \
            .is_('shift', 'null') \
            .execute()
        
        if not result.data:
            print("✅ 업데이트할 데이터가 없습니다. 모든 데이터에 교대조 정보가 있습니다.")
            return
        
        print(f"📊 업데이트 대상: {len(result.data)}건")
        
        updated_count = 0
        error_count = 0
        
        for record in result.data:
            try:
                # created_at 시간을 기준으로 교대조 계산
                created_at_str = record['created_at']
                
                # ISO 형식 파싱 (UTC 시간)
                if created_at_str.endswith('Z'):
                    created_at_utc = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                elif '+' in created_at_str:
                    created_at_utc = datetime.fromisoformat(created_at_str)
                else:
                    # 타임존 정보가 없는 경우 UTC로 가정
                    created_at_utc = datetime.fromisoformat(created_at_str).replace(tzinfo=pytz.UTC)
                
                # 베트남 시간으로 변환
                created_at_vietnam = created_at_utc.astimezone(vietnam_tz)
                
                # 교대조 정보 계산
                shift_info = get_shift_for_time(created_at_vietnam)
                shift_name = shift_info['shift_name']
                
                # 데이터베이스 업데이트
                update_result = supabase.table('inspection_data') \
                    .update({'shift': shift_name}) \
                    .eq('id', record['id']) \
                    .execute()
                
                if update_result.data:
                    updated_count += 1
                    if updated_count % 10 == 0:
                        print(f"   진행률: {updated_count}/{len(result.data)} ({updated_count/len(result.data)*100:.1f}%)")
                else:
                    print(f"❌ 업데이트 실패: ID {record['id']}")
                    error_count += 1
                    
            except Exception as e:
                print(f"❌ 레코드 처리 오류 (ID: {record['id']}): {str(e)}")
                error_count += 1
                continue
        
        print(f"\n✅ 업데이트 완료!")
        print(f"   📊 성공: {updated_count}건")
        print(f"   ❌ 실패: {error_count}건")
        print(f"   📈 성공률: {updated_count/(updated_count+error_count)*100:.1f}%")
        
        # 업데이트 결과 확인
        verify_result = supabase.table('inspection_data') \
            .select('shift') \
            .not_.is_('shift', 'null') \
            .execute()
        
        total_with_shift = len(verify_result.data) if verify_result.data else 0
        
        remaining_result = supabase.table('inspection_data') \
            .select('id') \
            .is_('shift', 'null') \
            .execute()
        
        remaining_without_shift = len(remaining_result.data) if remaining_result.data else 0
        
        print(f"\n📊 최종 상태:")
        print(f"   🏭 교대조 정보 있음: {total_with_shift}건")
        print(f"   ⚠️ 교대조 정보 없음: {remaining_without_shift}건")
        
    except Exception as e:
        print(f"❌ 스크립트 실행 오류: {str(e)}")
        import traceback
        traceback.print_exc()

def verify_shift_data():
    """교대조 데이터 검증"""
    print("\n🔍 교대조 데이터 검증 시작...")
    
    try:
        supabase = get_supabase_client()
        
        # 교대조별 통계
        result = supabase.table('inspection_data') \
            .select('shift') \
            .not_.is_('shift', 'null') \
            .execute()
        
        if result.data:
            shift_stats = {}
            for record in result.data:
                shift = record['shift']
                shift_stats[shift] = shift_stats.get(shift, 0) + 1
            
            print("📊 교대조별 데이터 분포:")
            for shift, count in sorted(shift_stats.items()):
                print(f"   {shift}: {count}건")
        
        # 최근 데이터 샘플 확인
        recent_result = supabase.table('inspection_data') \
            .select('created_at, shift') \
            .not_.is_('shift', 'null') \
            .order('created_at', desc=True) \
            .limit(5) \
            .execute()
        
        if recent_result.data:
            print("\n📋 최근 데이터 샘플:")
            for record in recent_result.data:
                created_at = record['created_at'][:19].replace('T', ' ')
                shift = record['shift']
                print(f"   {created_at} → {shift}")
        
    except Exception as e:
        print(f"❌ 검증 오류: {str(e)}")

def main():
    """메인 실행 함수"""
    print("🏭 교대조 데이터 업데이트 스크립트")
    print("=" * 50)
    print("📋 작업 내용:")
    print("   1. 기존 검사 데이터에 교대조 정보 추가")
    print("   2. created_at 기준으로 교대조 자동 계산")
    print("   3. shift 컬럼에 교대조명 저장")
    print("=" * 50)
    print()
    
    # 현재 교대조 정보 표시
    from utils.shift_manager import get_current_shift
    current_shift = get_current_shift()
    print(f"🕐 현재 교대조: {current_shift['full_shift_name']}")
    print()
    
    # 기존 데이터 업데이트
    update_existing_shift_data()
    
    # 검증
    verify_shift_data()
    
    print(f"\n🎉 모든 작업이 완료되었습니다!")
    print(f"💡 이제 모든 검사 데이터에 교대조 정보가 포함됩니다.")

if __name__ == "__main__":
    main() 