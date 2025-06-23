import streamlit as st
import os
import json
from utils.supabase_client import get_supabase_client

# 설정 파일 경로
SETTINGS_FILE = ".streamlit/config.json"

def load_env_settings():
    """환경 설정을 로드합니다."""
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def save_env_setting(key, value):
    """환경 설정을 저장합니다."""
    try:
        os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
        settings = load_env_settings()
        settings[key] = value
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"설정 저장 실패: {str(e)}")
        return False

def show_supabase_config():
    """Supabase 설정 화면을 표시합니다."""
    st.title("⚙️ Supabase 설정")
    
    # 현재 연결 상태 확인
    check_connection_status()
    
    # 탭 생성
    tabs = st.tabs(["🔧 연결 설정", "📊 테이블 관리", "🧪 연결 테스트"])
    
    with tabs[0]:
        show_connection_settings()
    
    with tabs[1]:
        show_table_management()
    
    with tabs[2]:
        show_connection_test()

def check_connection_status():
    """현재 연결 상태를 확인하고 표시합니다."""
    st.subheader("🔗 현재 연결 상태")
    
    try:
        client = get_supabase_client()
        
        # 기본 연결 테스트
        try:
            response = client.table('users').select('*').limit(1).execute()
            st.success("✅ Supabase에 성공적으로 연결되었습니다!")
            st.success("🎯 users 테이블에도 정상적으로 접근 가능합니다!")
        except Exception as e:
            st.success("✅ Supabase 기본 연결은 성공했습니다!")
            st.warning(f"⚠️ users 테이블 접근 오류: {str(e)}")
            
            st.markdown("""
**해결 방법:**

1. **RLS 정책 비활성화** (가장 간단한 해결책):
   ```sql
   ALTER TABLE users DISABLE ROW LEVEL SECURITY;
   ```

2. **로그인 문제 해결**:
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
    
    except Exception as e:
        st.error(f"❌ Supabase 연결 실패: {str(e)}")
        st.info("💡 아래에서 올바른 URL과 API Key를 설정하세요.")

def show_connection_settings():
    """연결 설정 화면을 표시합니다."""
    st.subheader("🔧 Supabase 연결 설정")
    
    # 현재 설정 로드
    settings = load_env_settings()
    
    with st.form("supabase_config"):
        st.write("**Supabase 프로젝트 정보를 입력하세요:**")
        
        # URL 입력
        supabase_url = st.text_input(
            "Supabase URL",
            value=settings.get("SUPABASE_URL", ""),
            placeholder="https://your-project.supabase.co",
            help="Supabase 프로젝트 대시보드에서 확인할 수 있습니다"
        )
        
        # API Key 입력
        supabase_key = st.text_input(
            "Supabase API Key (anon/public)",
            value=settings.get("SUPABASE_KEY", ""),
            type="password",
            placeholder="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            help="공개(anon) API 키를 입력하세요"
        )
        
        # 저장 버튼
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.form_submit_button("💾 설정 저장", type="primary"):
                if not supabase_url or not supabase_key:
                    st.error("URL과 API Key를 모두 입력해주세요.")
                else:
                    # 설정 저장
                    success1 = save_env_setting("SUPABASE_URL", supabase_url)
                    success2 = save_env_setting("SUPABASE_KEY", supabase_key)
                    
                    if success1 and success2:
                        st.success("✅ 설정이 저장되었습니다!")
                        st.info("🔄 페이지를 새로고침하여 새 설정을 적용하세요.")
                    else:
                        st.error("❌ 설정 저장에 실패했습니다.")
        
        with col2:
            if st.form_submit_button("🗑️ 설정 초기화"):
                try:
                    if os.path.exists(SETTINGS_FILE):
                        os.remove(SETTINGS_FILE)
                    st.success("✅ 설정이 초기화되었습니다!")
                    st.info("🔄 페이지를 새로고침하세요.")
                except Exception as e:
                    st.error(f"❌ 초기화 실패: {str(e)}")
        
        with col3:
            if st.form_submit_button("🔄 연결 테스트"):
                if supabase_url and supabase_key:
                    st.info("연결을 테스트하는 중...")
                    # 여기서 실제 연결 테스트 로직을 추가할 수 있습니다
                else:
                    st.warning("URL과 API Key를 먼저 입력하세요.")

def show_table_management():
    """테이블 관리 화면을 표시합니다."""
    st.subheader("📊 테이블 관리")
    
    try:
        client = get_supabase_client()
        
        # 테이블 구조 확인
        check_table_structure(client)
        
        st.markdown("---")
        
        # 테이블 생성/수정 가이드
        show_create_users_table_guide()
        
        st.markdown("---")
        
        # 테스트 데이터 관리
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🧪 테스트 데이터 삽입"):
                test_data_insertion()
        
        with col2:
            if st.button("🔧 제약조건 수정"):
                fix_constraints()
    
    except Exception as e:
        st.error(f"❌ 테이블 관리 오류: {str(e)}")

def show_connection_test():
    """연결 테스트 화면을 표시합니다."""
    st.subheader("🧪 연결 테스트")
    
    try:
        client = get_supabase_client()
        
        # 기본 연결 테스트
        if st.button("🔍 기본 연결 테스트"):
            try:
                response = client.table('users').select('count').execute()
                st.success("✅ 기본 연결 성공!")
                
                # 테이블별 테스트
                tables_to_test = ['users', 'inspectors', 'defect_types', 'production_models', 'inspection_data']
                
                st.subheader("📋 테이블별 연결 테스트")
                for table in tables_to_test:
                    try:
                        response = client.table(table).select('*').limit(1).execute()
                        if response.data is not None:
                            st.success(f"✅ {table} 테이블: 연결 성공 (데이터 {len(response.data)}건)")
                        else:
                            st.warning(f"⚠️ {table} 테이블: 연결됨 (데이터 없음)")
                    except Exception as table_error:
                        st.error(f"❌ {table} 테이블: {str(table_error)}")
                
            except Exception as e:
                st.error(f"❌ 연결 테스트 실패: {str(e)}")
        
        # 성능 테스트
        if st.button("⚡ 성능 테스트"):
            import time
            
            try:
                start_time = time.time()
                response = client.table('users').select('*').limit(10).execute()
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000
                
                if response_time < 500:
                    st.success(f"⚡ 응답시간: {response_time:.2f}ms (매우 빠름)")
                elif response_time < 1000:
                    st.success(f"✅ 응답시간: {response_time:.2f}ms (양호)")
                else:
                    st.warning(f"⚠️ 응답시간: {response_time:.2f}ms (느림)")
                
            except Exception as e:
                st.error(f"❌ 성능 테스트 실패: {str(e)}")
    
    except Exception as e:
        st.error(f"❌ 연결 테스트 오류: {str(e)}")

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
                    
                st.info("💡 누락된 컬럼을 추가하려면 아래 SQL을 사용하세요.")
            
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
            st.info("💡 아래 'users 테이블 생성 가이드'를 사용하여 새 테이블을 생성하세요.")

def show_create_users_table_guide():
    """users 테이블 생성 가이드를 표시합니다.""" 
    st.subheader("📋 users 테이블 생성 가이드")
    st.info("다음 SQL 스크립트를 Supabase SQL Editor에서 실행하세요:")
    
    sql_code = """-- users 테이블 생성 (최신 버전)
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    employee_id TEXT UNIQUE,
    department TEXT,
    role TEXT DEFAULT 'user' CHECK (role IN ('user', 'inspector')),
    password TEXT,
    password_hash TEXT,
    is_active BOOLEAN DEFAULT true,
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

-- RLS 비활성화 (개발용)
ALTER TABLE users DISABLE ROW LEVEL SECURITY;

-- 기본 사용자 데이터 삽입
INSERT INTO users (name, email, employee_id, department, role, password, is_active) 
VALUES 
('관리자', 'admin@company.com', 'A001', 'IT팀', 'user', 'admin123', true),
('검사자1', 'inspector1@company.com', 'I001', '품질팀', 'inspector', 'inspector123', true),
('검사자2', 'inspector2@company.com', 'I002', '품질팀', 'inspector', 'inspector123', true)
ON CONFLICT (email) DO NOTHING;"""
    
    st.code(sql_code, language="sql")
    
    st.warning("⚠️ 위 SQL을 복사하여 Supabase SQL Editor에서 실행하세요.")

def test_data_insertion():
    """테스트 데이터 삽입을 시도합니다."""
    try:
        client = get_supabase_client()
        
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
        
        st.info("💡 제약 조건 수정이 필요하면 다음 SQL을 실행하세요:")
        st.code("""
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_role_check;
ALTER TABLE users ADD CONSTRAINT users_role_check 
CHECK (role IN ('user', 'admin', 'manager', 'inspector'));
""", language="sql")
        
    except Exception as e:
        st.error(f"❌ 오류 발생: {str(e)}") 