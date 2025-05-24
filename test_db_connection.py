import os
from dotenv import load_dotenv
from supabase import create_client, Client

# 환경 변수 로드
load_dotenv()

# 기본 연결 테스트
print("=== Supabase 데이터베이스 연결 테스트 ===")

try:
    # 환경 변수 가져오기
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        raise ValueError("Supabase URL과 KEY가 환경 변수에 설정되어 있지 않습니다. .env 파일을 확인하세요.")
    
    # 가장 기본적인 방식으로 연결 시도
    print(f"URL: {supabase_url}")
    print(f"KEY: {supabase_key[:5]}...{supabase_key[-5:] if len(supabase_key) > 10 else ''}")
    
    # 연결
    print("\n직접 연결 시도 중...")
    supabase = create_client(supabase_url, supabase_key)
    print("✅ Supabase 연결 성공!")
    
    # 테이블 연결 테스트
    try:
        # inspectors 테이블 연결 테스트
        response = supabase.table('inspectors').select('*').limit(1).execute()
        print(f"inspectors 테이블 연결 성공. 데이터: {response.data}")
        
        # defect_types 테이블 연결 테스트
        try:
            response = supabase.table('defect_types').select('*').execute()
            print(f"defect_types 테이블 연결 성공. 데이터: {response.data}")
            
            # defect_types 테이블에 데이터가 없으면 기본 데이터 삽입
            if not response.data:
                print("defect_types 테이블에 데이터가 없습니다. 기본 데이터를 삽입합니다.")
                default_defect_types = [
                    {"name": "치수 불량", "description": "제품의 치수가 규격을 벗어남"},
                    {"name": "표면 결함", "description": "제품 표면의 긁힘, 찍힘 등의 결함"},
                    {"name": "가공 불량", "description": "가공 공정에서 발생한 불량"},
                    {"name": "재료 결함", "description": "원자재의 결함으로 인한 불량"},
                    {"name": "기타", "description": "기타 불량 유형"}
                ]
                
                for defect_type in default_defect_types:
                    result = supabase.table('defect_types').insert(defect_type).execute()
                    print(f"불량 유형 삽입 결과: {result.data}")
                    
                # 삽입 후 다시 조회
                response = supabase.table('defect_types').select('*').execute()
                print(f"defect_types 테이블 데이터 삽입 후: {response.data}")
                
        except Exception as e:
            print(f"defect_types 테이블 연결 실패: {str(e)}")
            
            # 테이블이 없으면 생성하는 SQL 문
            print("defect_types 테이블을 생성합니다.")
            print("다음 SQL 문을 Supabase SQL 편집기에서 실행하세요:")
            print("""
            -- defect_types 테이블 생성
            CREATE TABLE IF NOT EXISTS public.defect_types (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                name TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            -- RLS 정책 설정
            ALTER TABLE public.defect_types ENABLE ROW LEVEL SECURITY;
            
            -- 모든 사용자가 조회 가능하도록 정책 설정
            CREATE POLICY "모든 사용자가 불량 유형을 조회할 수 있음" 
            ON public.defect_types FOR SELECT USING (true);
            
            -- 인증된 사용자가 불량 유형을 관리할 수 있도록 정책 설정
            CREATE POLICY "인증된 사용자가 불량 유형을 관리할 수 있음"
            ON public.defect_types FOR ALL USING (auth.role() = 'authenticated');
            """)
        
        # production_models 테이블 연결 테스트
        response = supabase.table('production_models').select('*').limit(5).execute()
        print(f"production_models 테이블 연결 성공. 데이터: {response.data}")
        
        # 검사 데이터 테이블 연결 테스트
        response = supabase.table('inspection_data').select('*').limit(5).execute()
        print(f"inspection_data 테이블 연결 성공. 데이터: {response.data}")
        
        # 불량 데이터 테이블 연결 테스트
        response = supabase.table('defects').select('*').limit(5).execute()
        print(f"defects 테이블 연결 성공. 데이터: {response.data}")
        
        print("모든 테이블 연결 테스트 완료")
        
    except Exception as e:
        print(f"데이터베이스 연결 테스트 실패: {str(e)}")
    
except Exception as e:
    print(f"\n❌ 오류 발생: {str(e)}")
    
    # 오류 세부 정보 출력
    import traceback
    print("\n상세 오류 정보:")
    traceback.print_exc() 