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
    
except Exception as e:
    print(f"\n❌ 오류 발생: {str(e)}")
    
    # 오류 세부 정보 출력
    import traceback
    print("\n상세 오류 정보:")
    traceback.print_exc() 