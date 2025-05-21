import os
from supabase import create_client, Client
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

def get_supabase_client() -> Client:
    """Supabase 클라이언트 반환"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        raise ValueError("Supabase URL과 KEY가 환경 변수에 설정되어 있지 않습니다. .env 파일을 확인하세요.")
    
    # 직접 연결 방식 사용
    return create_client(supabase_url, supabase_key) 