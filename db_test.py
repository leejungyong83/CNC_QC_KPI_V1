import os
import uuid
from utils.supabase_client import get_supabase_client
from datetime import datetime
import json

print("=== Supabase 데이터베이스 연결 및 CRUD 테스트 ===")

try:
    # Supabase 클라이언트 가져오기
    print("1. Supabase 클라이언트 연결 중...")
    supabase = get_supabase_client()
    print("   ✅ Supabase 연결 성공")
    
    # 테스트용 데이터
    test_inspector = {
        "name": "테스트 검사자",
        "employee_id": f"EMP{uuid.uuid4().hex[:6]}",
        "department": "품질관리부"
    }
    
    test_model = {
        "model_no": f"MODEL-{uuid.uuid4().hex[:6]}",
        "model_name": "테스트 모델",
        "process": "가공"
    }
    
    # 1. 검사자 추가 테스트
    print("\n2. 검사자 추가 테스트...")
    inspector_result = supabase.table('inspectors').insert(test_inspector).execute()
    inspector_data = inspector_result.data[0]
    inspector_id = inspector_data['id']
    print(f"   ✅ 검사자 추가 성공: {inspector_data['name']} (ID: {inspector_id})")
    
    # 2. 생산모델 추가 테스트
    print("\n3. 생산모델 추가 테스트...")
    model_result = supabase.table('production_models').insert(test_model).execute()
    model_data = model_result.data[0]
    model_id = model_data['id']
    print(f"   ✅ 생산모델 추가 성공: {model_data['model_name']} (ID: {model_id})")
    
    # 3. 검사 데이터 추가 테스트
    print("\n4. 검사 데이터 추가 테스트...")
    inspection_data = {
        "inspection_date": datetime.now().strftime("%Y-%m-%d"),
        "inspector_id": inspector_id,
        "model_id": model_id,
        "result": "합격",
        "quantity": 100,
        "notes": "테스트 데이터"
    }
    
    inspection_result = supabase.table('inspection_data').insert(inspection_data).execute()
    inspection_data = inspection_result.data[0]
    inspection_id = inspection_data['id']
    print(f"   ✅ 검사 데이터 추가 성공 (ID: {inspection_id})")
    
    # 4. 불량 데이터 추가 테스트
    print("\n5. 불량 데이터 추가 테스트...")
    defect_data = {
        "inspection_id": inspection_id,
        "defect_type": "치수 불량",
        "defect_count": 5,
        "description": "테스트 불량 데이터"
    }
    
    defect_result = supabase.table('defects').insert(defect_data).execute()
    defect_data = defect_result.data[0]
    defect_id = defect_data['id']
    print(f"   ✅ 불량 데이터 추가 성공 (ID: {defect_id})")
    
    # 5. 데이터 조회 테스트
    print("\n6. 데이터 조회 테스트...")
    
    # 검사자 조회
    inspector = supabase.table('inspectors').select('*').eq('id', inspector_id).execute()
    print(f"   ✅ 검사자 조회 성공: {inspector.data[0]['name']}")
    
    # 생산모델 조회
    model = supabase.table('production_models').select('*').eq('id', model_id).execute()
    print(f"   ✅ 생산모델 조회 성공: {model.data[0]['model_name']}")
    
    # 검사 데이터 조회 (JOIN 포함)
    inspection = supabase.table('inspection_data') \
        .select('*, inspectors(name), production_models(model_name)') \
        .eq('id', inspection_id) \
        .execute()
    
    print(f"   ✅ 검사 데이터 조회 성공: 검사자={inspection.data[0]['inspectors']['name']}, 모델={inspection.data[0]['production_models']['model_name']}")
    
    # 6. 데이터 수정 테스트
    print("\n7. 데이터 수정 테스트...")
    
    # 검사 데이터 수정
    update_data = {
        "result": "불합격",
        "notes": "테스트 수정 데이터"
    }
    
    update_result = supabase.table('inspection_data') \
        .update(update_data) \
        .eq('id', inspection_id) \
        .execute()
    
    print(f"   ✅ 검사 데이터 수정 성공: {update_result.data[0]['result']}")
    
    # 7. 수정된 데이터 재확인
    updated_inspection = supabase.table('inspection_data') \
        .select('*') \
        .eq('id', inspection_id) \
        .execute()
    
    print(f"   ✅ 수정된 데이터 확인: result={updated_inspection.data[0]['result']}, notes={updated_inspection.data[0]['notes']}")
    
    # 8. 데이터 삭제 테스트 (테스트 완료 후 정리)
    print("\n8. 테스트 데이터 정리 중...")
    
    # 불량 데이터 삭제
    supabase.table('defects').delete().eq('id', defect_id).execute()
    print(f"   ✅ 불량 데이터 삭제 성공")
    
    # 검사 데이터 삭제
    supabase.table('inspection_data').delete().eq('id', inspection_id).execute()
    print(f"   ✅ 검사 데이터 삭제 성공")
    
    # 생산모델 삭제
    supabase.table('production_models').delete().eq('id', model_id).execute()
    print(f"   ✅ 생산모델 삭제 성공")
    
    # 검사자 삭제
    supabase.table('inspectors').delete().eq('id', inspector_id).execute()
    print(f"   ✅ 검사자 삭제 성공")
    
    print("\n=== 모든 테스트가 성공적으로 완료되었습니다! ===")
    
except Exception as e:
    print(f"\n❌ 오류 발생: {str(e)}")
    
    # 오류 세부 정보 출력
    import traceback
    print("\n상세 오류 정보:")
    traceback.print_exc() 