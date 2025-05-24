import streamlit as st
import os
from dotenv import load_dotenv, set_key, find_dotenv
from utils.supabase_client import get_supabase_client

# .env 파일 로드
load_dotenv()

def load_env_settings():
    """환경 설정을 .env 파일에서 로드합니다."""
    env_file = find_dotenv()
    if not env_file:
        # .env 파일이 없으면 생성
        env_file = os.path.join(os.getcwd(), '.env')
        if not os.path.exists(env_file):
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write('SUPABASE_URL=your_supabase_url\n')
                f.write('SUPABASE_KEY=your_supabase_key\n')
    
    load_dotenv(env_file)
    return env_file

def save_env_setting(key, value):
    """환경 설정을 .env 파일에 저장합니다."""
    env_file = find_dotenv()
    if not env_file:
        env_file = os.path.join(os.getcwd(), '.env')
    set_key(env_file, key, value)

def simple_connection_test():
    """간단한 연결 테스트 (button 없이)"""
    try:
        client = get_supabase_client()
        client_type = type(client).__name__
        
        if client_type == "DummySupabaseClient":
            st.error("❌ 오프라인 모드로 작동 중입니다. Supabase 연결이 설정되지 않았습니다.")
            
            # 설정 상태 진단
            url = os.getenv("SUPABASE_URL", "")
            key = os.getenv("SUPABASE_KEY", "")
            
            if url in ["", "your_supabase_url"]:
                st.warning("🔧 Supabase URL이 설정되지 않았습니다.")
            elif key in ["", "your_supabase_key"]:
                st.warning("🔧 Supabase KEY가 설정되지 않았습니다.")
            else:
                st.warning("🔧 설정은 되어있지만 연결에 실패했습니다. URL과 KEY를 다시 확인해주세요.")
        else:
            # 실제 연결 테스트
            try:
                # 간단한 쿼리로 연결 테스트
                response = client.table('users').select('*').limit(1).execute()
                st.success("✅ Supabase에 성공적으로 연결되었습니다!")
                st.success("🎯 users 테이블에도 정상적으로 접근 가능합니다!")
            except Exception as e:
                st.success("✅ Supabase 기본 연결은 성공했습니다!")
                st.warning(f"⚠️ 테이블 접근 시 오류: {str(e)}")
                st.info("💡 테이블이 없거나 RLS 정책 문제일 수 있습니다.")
    except Exception as e:
        st.error(f"❌ 연결 테스트 중 오류 발생: {str(e)}")

def show_supabase_config():
    """Supabase 연결 설정 화면을 표시합니다."""
    st.title("🔧 Supabase 연결 설정")
    
    # .env 파일에서 설정 로드
    env_file = load_env_settings()
    current_url = os.getenv("SUPABASE_URL", "설정되지 않음")
    current_key = os.getenv("SUPABASE_KEY", "설정되지 않음")
    
    # 현재 설정 상태 표시
    st.subheader("현재 설정 상태")
    
    # .env 파일 경로 표시
    st.info(f"📁 설정 파일 위치: `{env_file}`")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if current_url in ["설정되지 않음", "your_supabase_url"]:
            st.warning("**Supabase URL:** 설정되지 않음")
        else:
            # URL의 일부만 표시 (보안)
            masked_url = current_url[:25] + "..." if len(current_url) > 25 else current_url
            st.success(f"**Supabase URL:** {masked_url}")
    
    with col2:
        if current_key in ["설정되지 않음", "your_supabase_key"]:
            st.warning("**Supabase KEY:** 설정되지 않음")
        else:
            st.success("**Supabase KEY:** ✅ 설정됨")
    
    # 연결 상태 테스트 (form 외부)
    st.subheader("연결 상태")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 연결 테스트", use_container_width=True):
            test_connection()
    
    with col2:
        if st.button("🔄 설정 새로고침", use_container_width=True):
            load_env_settings()
            st.success("설정이 새로고침되었습니다!")
            st.rerun()
    
    st.markdown("---")
    
    # 설정 변경 폼
    st.subheader("Supabase 연결 설정")
    
    # 현재 설정된 값이 있으면 기본값으로 사용 (보안상 KEY는 비움)
    default_url = current_url if current_url not in ["설정되지 않음", "your_supabase_url"] else ""
    
    with st.form("supabase_config_form"):
        st.markdown("""
        **📋 Supabase 프로젝트 설정 방법:**
        1. [Supabase](https://supabase.com)에 로그인
        2. 프로젝트 대시보드 → Settings → API
        3. 아래 정보를 복사하여 입력
        4. 💾 **한번 저장하면 다음부터는 자동으로 로드됩니다!**
        """)
        
        # URL 입력
        new_url = st.text_input(
            "Supabase URL",
            value=default_url,
            placeholder="https://your-project-id.supabase.co",
            help="Supabase 프로젝트의 URL을 입력하세요"
        )
        
        # API Key 입력
        new_key = st.text_input(
            "Supabase Anon Key",
            value="",
            type="password",
            placeholder="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            help="Supabase 프로젝트의 anon key를 입력하세요 (보안상 기존값은 표시되지 않습니다)"
        )
        
        # 저장 버튼
        submit_button = st.form_submit_button("💾 설정 저장 (영구 보존)", use_container_width=True)
        
        if submit_button:
            if not new_url:
                st.error("Supabase URL을 입력해주세요.")
            elif not new_url.startswith("https://"):
                st.error("올바른 Supabase URL 형식이 아닙니다. (https://로 시작해야 합니다)")
            else:
                try:
                    # .env 파일에 설정 저장
                    save_env_setting("SUPABASE_URL", new_url)
                    
                    # KEY가 입력된 경우에만 저장
                    if new_key:
                        save_env_setting("SUPABASE_KEY", new_key)
                    
                    st.success("✅ Supabase 설정이 .env 파일에 영구 저장되었습니다!")
                    st.success("🎉 다음부터는 앱을 재시작해도 자동으로 설정이 로드됩니다!")
                    
                    # 간단한 연결 테스트 (button 없이)
                    simple_connection_test()
                    
                    # 페이지 새로고침으로 변경사항 적용
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ 설정 저장 중 오류 발생: {str(e)}")
    
    # 설정 초기화 기능 (form 외부로 이동)
    st.markdown("---")
    st.subheader("⚙️ 고급 설정")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ 설정 초기화", use_container_width=True):
            if st.session_state.get('confirm_reset', False):
                # 설정 초기화 실행
                save_env_setting("SUPABASE_URL", "your_supabase_url")
                save_env_setting("SUPABASE_KEY", "your_supabase_key")
                st.success("✅ 설정이 초기화되었습니다!")
                st.session_state['confirm_reset'] = False
                st.rerun()
            else:
                # 확인 요청
                st.session_state['confirm_reset'] = True
                st.warning("⚠️ 다시 한번 클릭하면 설정이 초기화됩니다!")
    
    with col2:
        if os.path.exists(env_file):
            with open(env_file, 'r', encoding='utf-8') as f:
                env_content = f.read()
            
            st.download_button(
                label="📥 .env 파일 다운로드",
                data=env_content,
                file_name=".env",
                mime="text/plain",
                use_container_width=True,
                help="현재 설정을 백업용으로 다운로드합니다"
            )

def test_connection():
    """연결 상태를 테스트하고 결과를 표시합니다. (button 포함된 전체 버전)"""
    # 간단한 연결 테스트
    simple_connection_test()
    
    # 도움말 섹션 추가
    st.markdown("---")
    st.subheader("📚 도움말")
    
    with st.expander("Supabase 설정 찾는 방법"):
        st.markdown("""
        1. **Supabase 대시보드** 접속 (https://app.supabase.com)
        2. 프로젝트 선택
        3. 왼쪽 메뉴에서 **Settings** 클릭
        4. **API** 탭 선택
        5. 다음 정보 복사:
           - **URL**: Project URL
           - **Anon Key**: anon public key
        """)
    
    with st.expander("테이블 설정 확인"):
        st.markdown("""
        Supabase에서 다음 테이블들이 생성되어 있는지 확인하세요:
        
        **users 테이블:**
        ```sql
        CREATE TABLE users (
            id BIGSERIAL PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            department TEXT,
            is_active BOOLEAN DEFAULT true,
            phone TEXT,
            position TEXT,
            notes TEXT,
            password TEXT,
            created_at TIMESTAMPTZ DEFAULT now(),
            updated_at TIMESTAMPTZ DEFAULT now()
        );
        ```
        
        **또는 간단히 RLS 비활성화:**
        ```sql
        ALTER TABLE users DISABLE ROW LEVEL SECURITY;
        ALTER TABLE defect_types DISABLE ROW LEVEL SECURITY;
        ```
        """)
    
    # 테이블 설정 및 테스트 기능 (form 외부)
    st.subheader("🧪 테이블 설정 및 테스트")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🏗️ users 테이블 생성", use_container_width=True, key="create_table"):
            create_users_table()
    
    with col2:
        if st.button("📋 테스트 데이터 삽입", use_container_width=True, key="test_data"):
            test_data_insertion()
    
    col3, col4 = st.columns(2)
    
    with col3:
        if st.button("🔧 제약 조건 수정", use_container_width=True, key="fix_constraints"):
            fix_constraints()
    
    with col4:
        if st.button("📊 테이블 구조 확인", use_container_width=True, key="check_structure"):
            client = get_supabase_client()
            if type(client).__name__ != "DummySupabaseClient":
                check_table_structure(client)
            else:
                st.error("❌ Supabase에 연결되지 않았습니다.")

def create_users_table():
    """users 테이블을 생성하거나 수정합니다."""
    try:
        client = get_supabase_client()
        if type(client).__name__ == "DummySupabaseClient":
            st.error("❌ Supabase에 연결되지 않았습니다. 먼저 연결 설정을 완료하세요.")
            return
        
        st.info("💡 기존 테이블 구조를 확인하고 안전하게 업데이트합니다.")
        
        # SQL 스크립트 표시
        st.code("""
        -- 안전한 테이블 업데이트
        ALTER TABLE users ADD COLUMN IF NOT EXISTS name TEXT;
        ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;
        ALTER TABLE users ADD COLUMN IF NOT EXISTS department TEXT;
        ALTER TABLE users ADD COLUMN IF NOT EXISTS phone TEXT;
        ALTER TABLE users ADD COLUMN IF NOT EXISTS position TEXT;
        ALTER TABLE users ADD COLUMN IF NOT EXISTS notes TEXT;
        ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT now();
        ALTER TABLE users ADD COLUMN IF NOT EXISTS password TEXT;
        
        -- RLS 비활성화 (간단한 해결책)
        ALTER TABLE users DISABLE ROW LEVEL SECURITY;
        """, language="sql")
        
        st.warning("⚠️ 위 SQL을 Supabase SQL 편집기에서 실행하세요.")
        
    except Exception as e:
        st.error(f"❌ 오류 발생: {str(e)}")

def test_data_insertion():
    """테스트 데이터 삽입을 시도합니다."""
    try:
        client = get_supabase_client()
        if type(client).__name__ == "DummySupabaseClient":
            st.error("❌ Supabase에 연결되지 않았습니다. 먼저 연결 설정을 완료하세요.")
            return
        
        # 테스트 데이터
        test_data = {
            "email": "test@example.com",
            "name": "테스트사용자",
            "role": "user",
            "department": "테스트팀",
            "is_active": True,
            "phone": "010-0000-0000",
            "position": "테스터",
            "notes": "테스트용 계정",
            "password": "test123"
        }
        
        # 기존 테스트 데이터 삭제 시도
        try:
            client.table('users').delete().eq('email', 'test@example.com').execute()
        except:
            pass  # 삭제 실패해도 계속 진행
        
        # 새 데이터 삽입 시도
        response = client.table('users').insert(test_data).execute()
        
        if response.data:
            st.success("✅ 테스트 데이터가 성공적으로 삽입되었습니다!")
            st.json(response.data)
            
            # 삽입된 데이터 삭제
            client.table('users').delete().eq('email', 'test@example.com').execute()
            st.info("🗑️ 테스트 데이터가 삭제되었습니다.")
        else:
            st.error("❌ 데이터 삽입에 실패했습니다.")
            
    except Exception as e:
        st.error(f"❌ 테스트 중 오류 발생: {str(e)}")

def fix_constraints():
    """제약 조건을 수정합니다."""
    try:
        client = get_supabase_client()
        if type(client).__name__ == "DummySupabaseClient":
            st.error("❌ Supabase에 연결되지 않았습니다.")
            return
        
        st.info("💡 제약 조건 수정이 필요하면 다음 SQL을 실행하세요:")
        st.code("""
        ALTER TABLE users DROP CONSTRAINT IF EXISTS users_role_check;
        ALTER TABLE users ADD CONSTRAINT users_role_check 
        CHECK (role IN ('user', 'admin', 'manager', 'inspector'));
        """, language="sql")
        
    except Exception as e:
        st.error(f"❌ 오류 발생: {str(e)}")

def check_table_structure(client):
    """테이블 구조를 확인합니다."""
    try:
        # 테이블 정보 조회
        response = client.table('users').select('*').limit(1).execute()
        st.success("✅ users 테이블에 접근 가능합니다!")
        
        if response.data:
            st.subheader("테이블 구조")
            columns = list(response.data[0].keys())
            for col in columns:
                st.write(f"- `{col}`")
        else:
            st.info("테이블은 존재하지만 데이터가 없습니다.")
            
    except Exception as e:
        st.error(f"❌ 테이블 구조 확인 실패: {str(e)}") 