import os
import streamlit as st
from supabase import create_client, Client
from datetime import datetime
import uuid

def get_supabase_client() -> Client:
    """Supabase 클라이언트를 반환합니다. 연결 실패시 오류를 발생시킵니다."""
    try:
        # 환경변수에서 Supabase 설정 가져오기
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        # 환경변수가 없으면 Streamlit secrets에서 시도
        if not supabase_url or not supabase_key:
            try:
                supabase_url = st.secrets.get("SUPABASE_URL")
                supabase_key = st.secrets.get("SUPABASE_KEY")
            except:
                pass
        
        # 둘 다 없으면 에러 표시 및 설정 안내
        if not supabase_url or not supabase_key or supabase_url == "your_supabase_project_url_here":
            st.error("❌ **Supabase 연결 정보가 필요합니다!**")
            st.error("**다음 단계를 따라 설정하세요:**")
            st.code("""
1. .streamlit/secrets.toml 파일을 열어서
2. SUPABASE_URL과 SUPABASE_KEY를 실제 값으로 교체하세요

또는

3. 환경변수로 설정:
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-key
            """)
            st.stop()
        
        # 실제 Supabase 클라이언트 생성
        supabase = create_client(supabase_url, supabase_key)
        
        # 연결 테스트 (메시지 숨김 처리)
        try:
            # 간단한 연결 테스트를 위해 테이블 목록을 조회
            test_response = supabase.table('users').select('id').limit(1).execute()
            # 연결 성공 메시지 숨김 (사용자 요청)
            return supabase
        except Exception as e:
            st.error(f"❌ **Supabase 연결 실패**: {str(e)}")
            st.error("**다음을 확인해주세요:**")
            st.code("""
1. URL과 KEY가 올바른지 확인
2. 네트워크 연결 상태 확인  
3. Supabase 프로젝트가 활성화되어 있는지 확인
4. RLS(Row Level Security) 정책 확인
            """)
            st.stop()
            
    except Exception as e:
        st.error(f"❌ **Supabase 클라이언트 생성 실패**: {str(e)}")
        st.stop()

def clear_local_dummy_data():
    """로컬 더미 데이터를 모두 삭제합니다."""
    dummy_keys = [
        'dummy_defect_types',
        'dummy_users', 
        'dummy_production_models',
        'dummy_last_id',
        'dummy_last_user_id',
        'dummy_last_model_id'
    ]
    
    cleared_count = 0
    for key in dummy_keys:
        if key in st.session_state:
            del st.session_state[key]
            cleared_count += 1
    
    if cleared_count > 0:
        st.info(f"🗑️ **로컬 더미 데이터 {cleared_count}개 항목을 삭제했습니다.**")
    
    return cleared_count 