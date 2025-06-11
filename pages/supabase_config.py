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

    # 로그인 문제 해결을 위한 추가 기능
    st.markdown("---")
    st.subheader("🔐 로그인 문제 해결")
    
    col3, col4 = st.columns(2)
    
    with col3:
        if st.button("👥 기본 사용자 추가", use_container_width=True, key="add_basic_users"):
            add_basic_users()
    
    with col4:
        if st.button("🔍 사용자 목록 확인", use_container_width=True, key="check_users"):
            check_current_users()

    col5, col6 = st.columns(2)
    
    with col5:
        if st.button("🔧 기존 사용자 비밀번호 수정", use_container_width=True, key="fix_passwords"):
            fix_existing_user_passwords()
    
    with col6:
        if st.button("📋 테이블 구조 확인", use_container_width=True, key="check_structure_2"):
            client = get_supabase_client()
            if type(client).__name__ != "DummySupabaseClient":
                check_table_structure(client)
            else:
                st.error("❌ Supabase에 연결되지 않았습니다.")

    # 종합 로그인 문제 해결 가이드
    st.markdown("---")
    st.subheader("📚 로그인 문제 해결 가이드")
    
    with st.expander("🔍 단계별 문제 해결 방법"):
        st.markdown("""
        ### 1단계: 연결 상태 확인
        - 위의 "🔍 연결 테스트" 버튼을 클릭하여 Supabase 연결 상태 확인
        - 연결이 안 되면 URL과 KEY 설정을 다시 확인
        
        ### 2단계: 사용자 데이터 확인
        - "🔍 사용자 목록 확인" 버튼으로 현재 데이터베이스의 사용자 확인
        - 사용자가 없으면 "👥 기본 사용자 추가" 버튼으로 테스트 계정 생성
        
        ### 3단계: 비밀번호 문제 해결
        - "🔧 기존 사용자 비밀번호 수정" 버튼으로 알려진 사용자들의 비밀번호 업데이트
        - 또는 새로운 사용자를 "👥 기본 사용자 추가"로 생성
        
        ### 4단계: 테이블 구조 확인
        - "📋 테이블 구조 확인" 버튼으로 users 테이블 구조 점검
        - 필요한 컬럼이 없으면 아래 SQL 실행
        
        ### 5단계: 로그인 시도
        - 메인 화면에서 다음 계정들로 로그인 시도:
          - `admin@company.com` / `admin123`
          - `user@company.com` / `user123`
          - `inspector@company.com` / `inspector123`
          - `diwjddyd83@gmail.com` / `01100110`
          - `hong@company.com` / `user123`
        """)
    
    with st.expander("🛠️ 테이블 구조 수정 SQL"):
        st.code("""
-- users 테이블 기본 구조 확인 및 수정
ALTER TABLE users ADD COLUMN IF NOT EXISTS password TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;
ALTER TABLE users ADD COLUMN IF NOT EXISTS name TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS role TEXT DEFAULT 'user';

-- RLS 비활성화 (개발용)
ALTER TABLE users DISABLE ROW LEVEL SECURITY;

-- 기본 사용자 추가 (없는 경우)
INSERT INTO users (email, name, role, password, is_active) 
VALUES 
('admin@company.com', '관리자', 'admin', 'admin123', true),
('user@company.com', '사용자', 'user', 'user123', true),
('inspector@company.com', '검사원', 'inspector', 'inspector123', true)
ON CONFLICT (email) DO NOTHING;
        """, language="sql")
    
    with st.expander("🚨 긴급 복구 방법"):
        st.markdown("""
        **모든 방법이 실패한 경우:**
        
        1. **RLS 정책 비활성화 (가장 가능성 높은 해결책)**:
           ```sql
           ALTER TABLE users DISABLE ROW LEVEL SECURITY;
           ```
        
        2. **오프라인 모드 사용**: 
           - Supabase 연결을 끊고 기본 테스트 계정으로 로그인
           - `admin@company.com` / `admin123`
        
        3. **테이블 완전 재생성**:
           ```sql
           DROP TABLE IF EXISTS users CASCADE;
           CREATE TABLE users (
               id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
               email TEXT UNIQUE NOT NULL,
               name TEXT NOT NULL,
               role TEXT DEFAULT 'user',
               password TEXT,
               password_hash TEXT,
               is_active BOOLEAN DEFAULT true,
               created_at TIMESTAMPTZ DEFAULT now()
           );
           ALTER TABLE users DISABLE ROW LEVEL SECURITY;
           ```
        
        4. **환경 변수 초기화**:
           - "🗑️ 설정 초기화" 버튼으로 Supabase 설정 리셋
           - 다시 올바른 URL과 KEY 입력
        """)

    # RLS 문제 해결을 위한 긴급 안내
    st.markdown("---")
    st.error("🚨 **로그인 문제가 지속되는 경우 RLS 정책을 비활성화하세요:**")
    st.code("ALTER TABLE users DISABLE ROW LEVEL SECURITY;", language="sql")
    st.info("💡 이 SQL을 Supabase SQL Editor에서 실행하면 즉시 로그인 문제가 해결됩니다.")

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
            "password_hash": "test123_hash"
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
        st.subheader("📊 users 테이블 구조 분석")
        
        # 테이블 정보 조회
        response = client.table('users').select('*').limit(1).execute()
        st.success("✅ users 테이블에 접근 가능합니다!")
        
        if response.data:
            st.subheader("현재 테이블 컬럼")
            current_columns = list(response.data[0].keys())
            
            # 필수 컬럼과 선택적 컬럼 정의
            required_columns = ['id', 'email', 'name', 'role']
            optional_columns = ['department', 'is_active', 'password', 'phone', 'position', 'notes', 'created_at', 'updated_at']
            
            st.write("**현재 존재하는 컬럼:**")
            for col in current_columns:
                if col in required_columns:
                    st.write(f"✅ `{col}` (필수)")
                elif col in optional_columns:
                    st.write(f"✅ `{col}` (선택)")
                else:
                    st.write(f"ℹ️ `{col}` (기타)")
            
            # 누락된 컬럼 확인
            missing_required = [col for col in required_columns if col not in current_columns]
            missing_optional = [col for col in optional_columns if col not in current_columns]
            
            if missing_required:
                st.error("**누락된 필수 컬럼:**")
                for col in missing_required:
                    st.write(f"❌ `{col}`")
            
            if missing_optional:
                st.warning("**누락된 선택적 컬럼:**")
                for col in missing_optional:
                    st.write(f"⚠️ `{col}`")
                    
                st.info("💡 누락된 컬럼을 추가하려면 위의 '기존 테이블 구조 확인 및 안전 업데이트' SQL을 사용하세요.")
            
            if not missing_required and not missing_optional:
                st.success("🎉 모든 필요한 컬럼이 존재합니다!")
                
        else:
            st.info("테이블은 존재하지만 데이터가 없습니다.")
            st.warning("빈 테이블이므로 컬럼 구조를 정확히 확인하기 어렵습니다.")
            
    except Exception as e:
        error_message = str(e)
        st.error(f"❌ 테이블 구조 확인 실패: {error_message}")
        
        if "does not exist" in error_message:
            st.warning("⚠️ users 테이블이 존재하지 않습니다.")
            st.info("💡 'users 테이블 생성 가이드'를 사용하여 새 테이블을 생성하세요.")
        elif "could not find" in error_message:
            st.warning("⚠️ 테이블에 접근할 수 없거나 권한이 부족합니다.")
            st.info("💡 RLS 정책을 확인하거나 비활성화하세요.")
            st.code("ALTER TABLE users DISABLE ROW LEVEL SECURITY;", language="sql")

def show_create_users_table_guide():
    """users 테이블 생성 가이드를 표시합니다.""" 
    st.subheader("📋 users 테이블 생성 가이드")
    st.info("다음 SQL 스크립트를 Supabase SQL Editor에서 실행하세요:")
    
    sql_code = """
-- users 테이블 생성 (최신 버전)
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    employee_id TEXT UNIQUE,
    department TEXT,
    role TEXT DEFAULT 'user' CHECK (role IN ('user', 'inspector')),
    is_active BOOLEAN DEFAULT true,
    password TEXT,
    phone TEXT,
    position TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_employee_id ON users(employee_id);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

-- 기본 트리거 (업데이트 시간 자동 갱신)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at 
BEFORE UPDATE ON users 
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- RLS 비활성화 (개발용)
ALTER TABLE users DISABLE ROW LEVEL SECURITY;

-- 샘플 사용자 데이터 삽입
INSERT INTO users (name, email, employee_id, department, role, phone, position, notes, password) 
VALUES 
('홍길동', 'hong@company.com', 'EMP001', '생산팀', 'user', '010-1234-5678', '기술자', '생산라인 담당', 'user123'),
('김검사', 'kim@company.com', 'EMP002', '품질팀', 'inspector', '010-2345-6789', '품질검사원', '품질검사 담당', 'inspector123'),
('이직원', 'lee@company.com', 'EMP003', '제조팀', 'user', '010-3456-7890', '조립원', '제품 조립', 'user456')
ON CONFLICT (email) DO NOTHING;
"""
    
    st.code(sql_code, language="sql")
    
    st.markdown("---")
    st.subheader("🔧 기존 users 테이블 role 제약 조건 수정")
    st.info("기존 users 테이블이 있는 경우, role 제약 조건을 수정하려면 아래 SQL을 실행하세요:")
    
    role_fix_sql = """
-- 기존 role 제약 조건 삭제
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_role_check;

-- 새로운 role 제약 조건 추가 (user, inspector만 허용)
ALTER TABLE users ADD CONSTRAINT users_role_check 
CHECK (role IN ('user', 'inspector'));

-- 기존 admin, manager 역할을 user로 변경 (필요한 경우)
UPDATE users SET role = 'user' WHERE role IN ('admin', 'manager');
"""
    
    st.code(role_fix_sql, language="sql")
    
    st.markdown("---")
    st.subheader("🔍 기존 테이블 구조 확인 및 안전 업데이트")
    st.info("기존 users 테이블이 있는 경우, 구조를 확인하고 안전하게 업데이트하세요:")
    
    check_and_update_sql = """
-- 1. 현재 테이블 구조 확인
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'users' 
ORDER BY ordinal_position;

-- 2. 안전하게 누락된 컬럼 추가
ALTER TABLE users ADD COLUMN IF NOT EXISTS name TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS department TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;
ALTER TABLE users ADD COLUMN IF NOT EXISTS password TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS phone TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS position TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS notes TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT now();

-- 3. 기존 role 제약 조건 업데이트
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_role_check;
ALTER TABLE users ADD CONSTRAINT users_role_check 
CHECK (role IN ('user', 'inspector'));

-- 4. 기존 admin/manager 역할을 user로 변경
UPDATE users SET role = 'user' WHERE role IN ('admin', 'manager');

-- 5. name 컬럼이 비어있는 경우 email에서 추출
UPDATE users SET name = SPLIT_PART(email, '@', 1) WHERE name IS NULL OR name = '';

-- 6. is_active가 NULL인 경우 true로 설정
UPDATE users SET is_active = true WHERE is_active IS NULL;

-- 7. RLS 비활성화 (개발용)
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
"""
    
    st.code(check_and_update_sql, language="sql")
    
    st.markdown("---")
    st.subheader("🔧 password_hash 컬럼 타입 수정")
    st.warning("⚠️ password_hash 컬럼이 uuid 타입으로 되어 있어 text 타입으로 변경이 필요합니다:")
    
    password_hash_fix_sql = """
-- 1. 기존 password_hash 컬럼 삭제 (uuid 타입이므로)
ALTER TABLE users DROP COLUMN IF EXISTS password_hash;

-- 2. 올바른 TEXT 타입으로 password_hash 컬럼 재생성
ALTER TABLE users ADD COLUMN password_hash TEXT;

-- 3. 인덱스 생성 (성능 향상)
CREATE INDEX IF NOT EXISTS idx_users_password_hash ON users(password_hash);
"""
    
    st.code(password_hash_fix_sql, language="sql")
    
    st.markdown("---")
    st.subheader("🚀 간단한 해결책: password_hash 없이 진행")
    st.info("당장 사용자 추가 기능을 사용하려면 password_hash 없이 진행할 수도 있습니다.")
    
    no_password_sql = """
-- password_hash 컬럼을 사용하지 않고 기본 필드만으로 사용자 관리
-- 필요한 경우 나중에 별도 인증 시스템 구축 가능
"""
    
    st.code(no_password_sql, language="sql")

def add_basic_users():
    """기본 테스트 사용자들을 추가합니다."""
    try:
        client = get_supabase_client()
        if type(client).__name__ == "DummySupabaseClient":
            st.error("❌ Supabase에 연결되지 않았습니다.")
            return
        
        st.info("기본 사용자 계정을 추가합니다...")
        
        # 기본 사용자 데이터
        basic_users = [
            {
                "email": "admin@company.com",
                "name": "관리자",
                "role": "admin",
                "department": "관리팀",
                "is_active": True,
                "password": "admin123"
            },
            {
                "email": "user@company.com", 
                "name": "사용자",
                "role": "user",
                "department": "생산팀",
                "is_active": True,
                "password": "user123"
            },
            {
                "email": "inspector@company.com",
                "name": "검사원", 
                "role": "inspector",
                "department": "품질팀",
                "is_active": True,
                "password": "inspector123"
            }
        ]
        
        success_count = 0
        for user in basic_users:
            try:
                # 기존 사용자 확인
                existing = client.table('users').select('email').eq('email', user['email']).execute()
                
                if not existing.data:
                    # 새 사용자 추가
                    response = client.table('users').insert(user).execute()
                    if response.data:
                        success_count += 1
                        st.success(f"✅ {user['name']} ({user['email']}) 추가됨")
                    else:
                        st.warning(f"⚠️ {user['email']} 추가 실패")
                else:
                    st.info(f"ℹ️ {user['email']} 이미 존재함")
                    
            except Exception as e:
                st.error(f"❌ {user['email']} 추가 중 오류: {str(e)}")
        
        if success_count > 0:
            st.success(f"🎉 총 {success_count}개의 사용자가 추가되었습니다!")
        
    except Exception as e:
        st.error(f"❌ 기본 사용자 추가 실패: {str(e)}")

def check_current_users():
    """현재 데이터베이스의 사용자 목록을 확인합니다."""
    try:
        client = get_supabase_client()
        if type(client).__name__ == "DummySupabaseClient":
            st.error("❌ Supabase에 연결되지 않았습니다.")
            return
        
        st.info("현재 사용자 목록을 조회합니다...")
        
        # 사용자 목록 조회
        response = client.table('users').select('email, name, role, is_active, password, password_hash').execute()
        
        if response.data:
            st.success(f"✅ {len(response.data)}명의 사용자를 찾았습니다:")
            
            import pandas as pd
            df = pd.DataFrame(response.data)
            
            # 비밀번호 정보 마스킹
            if 'password' in df.columns:
                df['password'] = df['password'].apply(lambda x: "***" if x else "없음")
            if 'password_hash' in df.columns:
                df['password_hash'] = df['password_hash'].apply(lambda x: "***" if x else "없음")
            
            st.dataframe(df, use_container_width=True)
            
            # 로그인 가능한 계정 안내
            active_users = [user for user in response.data if user.get('is_active', True)]
            if active_users:
                st.subheader("🔑 로그인 가능한 계정:")
                for user in active_users:
                    has_password = user.get('password') or user.get('password_hash')
                    password_info = "비밀번호 설정됨" if has_password else "비밀번호 없음"
                    st.write(f"- **{user.get('name', 'Unknown')}**: `{user.get('email')}` ({password_info})")
            
        else:
            st.warning("⚠️ 사용자가 없습니다. 기본 사용자를 추가하세요.")
            
    except Exception as e:
        st.error(f"❌ 사용자 목록 조회 실패: {str(e)}")
        
        # 테이블 구조 문제일 가능성 안내
        if "does not exist" in str(e).lower():
            st.info("💡 users 테이블이 존재하지 않는 것 같습니다. 위의 '🏗️ users 테이블 생성' 버튼을 클릭하세요.")
        elif "column" in str(e).lower():
            st.info("💡 테이블 구조에 문제가 있을 수 있습니다. 테이블을 다시 생성해보세요.")

def fix_existing_user_passwords():
    """기존 사용자들의 비밀번호를 알려진 값으로 업데이트합니다."""
    try:
        client = get_supabase_client()
        if type(client).__name__ == "DummySupabaseClient":
            st.error("❌ Supabase에 연결되지 않았습니다.")
            return
        
        st.info("기존 사용자들의 비밀번호를 업데이트합니다...")
        
        # 알려진 사용자들의 비밀번호 매핑
        password_updates = {
            'diwjddyd83@gmail.com': '01100110',
            'zetooo1972@gmail.com': '01100110', 
            'jinuk.cho@gmail.com': '01100110',
            'hong@company.com': 'user123',
            'kim@company.com': 'inspector123',
            'lee@company.com': 'user456'
        }
        
        success_count = 0
        for email, password in password_updates.items():
            try:
                # 사용자 존재 확인
                existing = client.table('users').select('email, name').eq('email', email).execute()
                
                if existing.data:
                    # 비밀번호 해시 생성
                    import hashlib
                    password_hash = hashlib.sha256(password.encode()).hexdigest()
                    
                    # 비밀번호 업데이트 (password와 password_hash 둘 다)
                    update_data = {
                        'password': password,
                        'password_hash': password_hash,
                        'is_active': True
                    }
                    
                    response = client.table('users').update(update_data).eq('email', email).execute()
                    
                    if response.data:
                        success_count += 1
                        st.success(f"✅ {email} 비밀번호 업데이트됨 (비밀번호: {password})")
                    else:
                        st.warning(f"⚠️ {email} 업데이트 실패")
                else:
                    st.info(f"ℹ️ {email} 사용자가 존재하지 않음")
                    
            except Exception as e:
                st.error(f"❌ {email} 업데이트 중 오류: {str(e)}")
        
        if success_count > 0:
            st.success(f"🎉 총 {success_count}개의 사용자 비밀번호가 업데이트되었습니다!")
            st.info("💡 이제 다음 계정들로 로그인할 수 있습니다:")
            for email, password in password_updates.items():
                st.write(f"- {email} / {password}")
        
    except Exception as e:
        st.error(f"❌ 비밀번호 업데이트 실패: {str(e)}") 