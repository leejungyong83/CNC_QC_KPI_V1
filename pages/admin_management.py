import streamlit as st
import pandas as pd
from datetime import datetime
from utils.supabase_client import get_supabase_client
import re

def show_admin_management():
    """관리자 CRUD 관리 페이지를 표시합니다."""
    st.header("👨‍💼 관리자 데이터베이스 관리")
    
    # Supabase 클라이언트 가져오기
    supabase = get_supabase_client()
    
    # 연결 상태 확인 및 표시
    show_connection_status(supabase)
    
    # 탭 생성
    list_tab, add_tab, edit_tab, delete_tab, sync_tab = st.tabs(["관리자 목록", "관리자 추가", "관리자 수정", "관리자 삭제", "데이터 동기화"])
    
    # 관리자 목록 탭
    with list_tab:
        show_admin_list(supabase)
    
    # 관리자 추가 탭
    with add_tab:
        show_add_admin(supabase)
    
    # 관리자 수정 탭
    with edit_tab:
        show_edit_admin(supabase)
    
    # 관리자 삭제 탭
    with delete_tab:
        show_delete_admin(supabase)
    
    # 데이터 동기화 탭
    with sync_tab:
        show_data_sync(supabase)

def show_connection_status(supabase):
    """연결 상태를 표시합니다."""
    if hasattr(supabase, '_init_session_state'):
        # 더미 클라이언트인 경우
        st.warning("⚠️ 현재 오프라인 모드로 작동 중입니다. 실제 Supabase와 연결되지 않았습니다.")
        st.info("💡 실제 데이터베이스 연결을 위해서는 'Supabase 설정' 메뉴에서 올바른 URL과 KEY를 설정하세요.")
    else:
        # 실제 Supabase 클라이언트인 경우
        st.success("✅ Supabase에 연결되었습니다.")

def show_data_sync(supabase):
    """데이터 동기화 기능을 표시합니다."""
    st.subheader("🔄 데이터 동기화")
    
    if hasattr(supabase, '_init_session_state'):
        # 더미 클라이언트인 경우
        st.warning("현재 오프라인 모드입니다. 실제 Supabase 연결 시 사용할 수 있는 기능입니다.")
        st.info("Supabase 연결 후 관리자 데이터를 관리할 수 있습니다.")
    
    else:
        # 실제 Supabase 클라이언트인 경우
        st.success("Supabase에 연결되었습니다.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("실제 데이터베이스에서 조회")
            if st.button("관리자 데이터베이스 조회", type="primary"):
                try:
                    response = supabase.table('admins').select('*').execute()
                    if response.data:
                        df = pd.DataFrame(response.data)
                        st.dataframe(df, use_container_width=True)
                        st.success(f"데이터베이스에서 {len(response.data)}개의 관리자 데이터를 조회했습니다.")
                    else:
                        st.info("데이터베이스에 관리자 데이터가 없습니다.")
                except Exception as e:
                    st.error(f"데이터베이스 조회 중 오류 발생: {str(e)}")
                    if "does not exist" in str(e):
                        st.warning("⚠️ admins 테이블이 존재하지 않습니다.")
                        if st.button("admins 테이블 생성 SQL 보기"):
                            show_create_admins_table_sql()
        
        with col2:
            st.subheader("샘플 데이터 업로드")
            if st.button("샘플 관리자 데이터 업로드"):
                upload_sample_admins(supabase)

def show_create_admins_table_sql():
    """admins 테이블 생성 SQL을 표시합니다."""
    st.subheader("📋 admins 테이블 생성 SQL")
    st.info("다음 SQL을 Supabase SQL Editor에서 실행하세요:")
    
    sql_code = """
-- admins 테이블 생성
CREATE TABLE IF NOT EXISTS admins (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    role TEXT DEFAULT 'admin' CHECK (role IN ('admin', 'superadmin')),
    department TEXT,
    is_active BOOLEAN DEFAULT true,
    phone TEXT,
    position TEXT,
    notes TEXT,
    password TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_admins_email ON admins(email);
CREATE INDEX IF NOT EXISTS idx_admins_role ON admins(role);
CREATE INDEX IF NOT EXISTS idx_admins_is_active ON admins(is_active);
CREATE INDEX IF NOT EXISTS idx_admins_created_at ON admins(created_at);

-- RLS 비활성화 (개발용)
ALTER TABLE admins DISABLE ROW LEVEL SECURITY;

-- 기본 관리자 데이터 삽입
INSERT INTO admins (email, name, role, department, phone, position, notes, password) 
VALUES 
('admin@company.com', '시스템관리자', 'superadmin', 'IT팀', '010-1111-1111', 'CTO', '시스템 총괄 관리자', 'admin123'),
('manager@company.com', '운영관리자', 'admin', '운영팀', '010-2222-2222', '운영팀장', '일반 운영 관리자', 'manager123')
ON CONFLICT (email) DO NOTHING;
"""
    
    st.code(sql_code, language="sql")

def upload_sample_admins(supabase):
    """샘플 관리자 데이터를 실제 데이터베이스에 업로드합니다."""
    sample_admins = [
        {
            "email": "admin@company.com",
            "name": "시스템관리자",
            "role": "superadmin",
            "department": "IT팀",
            "is_active": True,
            "phone": "010-1111-1111",
            "position": "CTO",
            "notes": "시스템 총괄 관리자",
            "password": "admin123",
            "created_at": "2024-01-01T09:00:00",
            "updated_at": "2024-01-01T09:00:00"
        },
        {
            "email": "manager@company.com", 
            "name": "운영관리자",
            "role": "admin",
            "department": "운영팀",
            "is_active": True,
            "phone": "010-2222-2222",
            "position": "운영팀장",
            "notes": "일반 운영 관리자",
            "password": "manager123",
            "created_at": "2024-01-02T09:00:00",
            "updated_at": "2024-01-02T09:00:00"
        },
        {
            "email": "supervisor@company.com",
            "name": "감독관리자", 
            "role": "admin",
            "department": "품질팀",
            "is_active": True,
            "phone": "010-3333-3333",
            "position": "품질팀장",
            "notes": "품질 관리 감독",
            "password": "supervisor123",
            "created_at": "2024-01-03T09:00:00",
            "updated_at": "2024-01-03T09:00:00"
        }
    ]
    
    try:
        # 기존 데이터 확인
        existing_response = supabase.table('admins').select('email').execute()
        existing_emails = [admin['email'] for admin in existing_response.data] if existing_response.data else []
        
        # 중복되지 않는 관리자만 추가
        new_admins = [admin for admin in sample_admins if admin['email'] not in existing_emails]
        
        if new_admins:
            response = supabase.table('admins').insert(new_admins).execute()
            if response.data:
                st.success(f"{len(new_admins)}명의 관리자가 성공적으로 업로드되었습니다!")
                st.rerun()
            else:
                st.error("관리자 업로드에 실패했습니다.")
        else:
            st.warning("모든 샘플 관리자가 이미 데이터베이스에 존재합니다.")
            
    except Exception as e:
        st.error(f"샘플 데이터 업로드 중 오류 발생: {str(e)}")
        if "does not exist" in str(e):
            st.warning("⚠️ admins 테이블이 존재하지 않습니다.")
            if st.button("테이블 생성 방법 보기"):
                show_create_admins_table_sql()

def show_admin_list(supabase):
    """관리자 목록을 표시합니다."""
    st.subheader("📋 관리자 목록")
    
    # 실제 Supabase 연결인지 확인
    is_real_supabase = not hasattr(supabase, '_init_session_state')
    
    try:
        # admins 테이블에서 모든 관리자 조회
        response = supabase.table('admins').select('*').order('created_at', desc=True).execute()
        
        if response.data:
            # 데이터프레임으로 변환
            df = pd.DataFrame(response.data)
            
            # 컬럼 순서 정리
            display_columns = []
            if 'id' in df.columns:
                display_columns.append('id')
            if 'email' in df.columns:
                display_columns.append('email')
            if 'name' in df.columns:
                display_columns.append('name')
            if 'role' in df.columns:
                display_columns.append('role')
            if 'department' in df.columns:
                display_columns.append('department')
            if 'position' in df.columns:
                display_columns.append('position')
            if 'phone' in df.columns:
                display_columns.append('phone')
            if 'is_active' in df.columns:
                display_columns.append('is_active')
            if 'created_at' in df.columns:
                display_columns.append('created_at')
            if 'updated_at' in df.columns:
                display_columns.append('updated_at')
            
            # 컬럼 설정
            column_config = {
                "id": st.column_config.TextColumn("ID", width="small"),
                "email": st.column_config.TextColumn("이메일", width="medium"),
                "name": st.column_config.TextColumn("이름", width="medium"),
                "role": st.column_config.TextColumn("권한", width="small"),
                "department": st.column_config.TextColumn("부서", width="medium"),
                "position": st.column_config.TextColumn("직책", width="medium"),
                "phone": st.column_config.TextColumn("전화번호", width="medium"),
                "is_active": st.column_config.CheckboxColumn("활성", width="small"),
                "created_at": st.column_config.DatetimeColumn("생성일", width="medium"),
                "updated_at": st.column_config.DatetimeColumn("수정일", width="medium"),
            }
            
            # 표시할 컬럼만 선택
            df_display = df[display_columns] if display_columns else df
            
            st.dataframe(
                df_display,
                column_config=column_config,
                use_container_width=True,
                hide_index=True
            )
            
            st.success(f"총 {len(df)}명의 관리자가 등록되어 있습니다.")
            
        else:
            st.info("등록된 관리자가 없습니다.")
            if st.button("샘플 관리자 데이터 추가"):
                upload_sample_admins(supabase)
    
    except Exception as e:
        error_message = str(e)
        st.error(f"관리자 목록을 불러오는 중 오류가 발생했습니다: {error_message}")
        
        if "does not exist" in error_message:
            st.warning("⚠️ admins 테이블이 존재하지 않습니다.")
            if st.button("테이블 생성 방법 보기"):
                show_create_admins_table_sql()

def show_add_admin(supabase):
    """새 관리자 추가 폼을 표시합니다."""
    st.subheader("➕ 새 관리자 추가")
    
    # 실제 Supabase 연결인지 확인
    is_real_supabase = not hasattr(supabase, '_init_session_state')
    
    if not is_real_supabase:
        st.warning("오프라인 모드에서는 관리자 추가 기능을 사용할 수 없습니다.")
        return
    
    with st.form("add_admin_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            email = st.text_input("이메일 *", placeholder="admin@example.com")
            name = st.text_input("이름 *", placeholder="홍길동")
            role = st.selectbox("권한 *", ["admin", "superadmin"], index=0, 
                               help="admin: 일반 관리자, superadmin: 최고 관리자")
            department = st.text_input("부서", placeholder="IT팀")
        
        with col2:
            password = st.text_input("비밀번호 *", type="password")
            phone = st.text_input("전화번호", placeholder="010-1234-5678")
            position = st.text_input("직책", placeholder="팀장")
            is_active = st.checkbox("활성 상태", value=True)
        
        # 추가 정보
        notes = st.text_area("비고", placeholder="기타 정보", height=100)
        
        submitted = st.form_submit_button("관리자 추가", type="primary")
        
        if submitted:
            # 필수 필드 검증
            if not email or not name or not password:
                st.error("이메일, 이름, 비밀번호는 필수 항목입니다.")
                return
            
            # 이메일 형식 검증
            if not validate_email(email):
                st.error("올바른 이메일 형식을 입력하세요.")
                return
            
            try:
                admin_data = {
                    "email": email,
                    "name": name,
                    "role": role,
                    "department": department,
                    "phone": phone,
                    "position": position,
                    "is_active": is_active,
                    "notes": notes,
                    "password": password,  # 실제 환경에서는 해시화 필요
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                
                response = supabase.table('admins').insert(admin_data).execute()
                
                if response.data:
                    st.success(f"관리자 '{name}'이(가) 성공적으로 추가되었습니다!")
                    st.rerun()
                else:
                    st.error("관리자 추가에 실패했습니다.")
                    
            except Exception as e:
                error_message = str(e)
                st.error(f"관리자 추가 중 오류가 발생했습니다: {error_message}")
                
                # 구체적인 오류 해결 가이드 제공
                if "duplicate key value violates unique constraint" in error_message:
                    st.warning("⚠️ 이미 존재하는 이메일입니다.")
                elif "violates check constraint" in error_message and "role" in error_message:
                    st.warning("⚠️ 권한 값이 올바르지 않습니다. (admin 또는 superadmin만 가능)")
                elif "does not exist" in error_message:
                    st.warning("⚠️ admins 테이블이 존재하지 않습니다.")
                    if st.button("테이블 생성 방법 보기"):
                        show_create_admins_table_sql()

def show_edit_admin(supabase):
    """관리자 수정 폼을 표시합니다."""
    st.subheader("✏️ 관리자 정보 수정")
    
    # 실제 Supabase 연결인지 확인
    is_real_supabase = not hasattr(supabase, '_init_session_state')
    
    if not is_real_supabase:
        st.warning("오프라인 모드에서는 관리자 수정 기능을 사용할 수 없습니다.")
        return
    
    try:
        # 관리자 목록 조회
        response = supabase.table('admins').select('*').execute()
        
        if not response.data:
            st.info("수정할 관리자가 없습니다.")
            return
        
        # 관리자 선택
        admin_options = {f"{admin['name']} ({admin['email']})": admin for admin in response.data}
        selected_admin_key = st.selectbox("수정할 관리자 선택", list(admin_options.keys()))
        
        if selected_admin_key:
            selected_admin = admin_options[selected_admin_key]
            
            with st.form("edit_admin_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    email = st.text_input("이메일 *", value=selected_admin.get('email', ''))
                    name = st.text_input("이름 *", value=selected_admin.get('name', ''))
                    current_role = selected_admin.get('role', 'admin')
                    role_index = ["admin", "superadmin"].index(current_role) if current_role in ["admin", "superadmin"] else 0
                    role = st.selectbox("권한", ["admin", "superadmin"], index=role_index)
                    department = st.text_input("부서", value=selected_admin.get('department', ''))
                
                with col2:
                    is_active = st.checkbox("활성 상태", value=selected_admin.get('is_active', True))
                    phone = st.text_input("전화번호", value=selected_admin.get('phone', ''))
                    position = st.text_input("직책", value=selected_admin.get('position', ''))
                    change_password = st.checkbox("비밀번호 변경")
                
                if change_password:
                    new_password = st.text_input("새 비밀번호", type="password")
                
                notes = st.text_area("비고", value=selected_admin.get('notes', ''), height=100)
                
                submitted = st.form_submit_button("수정 저장", type="primary")
                
                if submitted:
                    # 필수 필드 검증
                    if not email or not name:
                        st.error("이메일과 이름은 필수 항목입니다.")
                        return
                    
                    # 이메일 형식 검증
                    if not validate_email(email):
                        st.error("올바른 이메일 형식을 입력하세요.")
                        return
                    
                    try:
                        update_data = {
                            "email": email,
                            "name": name,
                            "role": role,
                            "department": department,
                            "phone": phone,
                            "position": position,
                            "is_active": is_active,
                            "notes": notes,
                            "updated_at": datetime.now().isoformat()
                        }
                        
                        if change_password and new_password:
                            update_data["password"] = new_password
                        
                        response = supabase.table('admins').update(update_data).eq('id', selected_admin['id']).execute()
                        
                        if response.data:
                            st.success(f"관리자 '{name}'의 정보가 성공적으로 수정되었습니다!")
                            st.rerun()
                        else:
                            st.error("관리자 정보 수정에 실패했습니다.")
                            
                    except Exception as e:
                        error_message = str(e)
                        st.error(f"관리자 수정 중 오류가 발생했습니다: {error_message}")
                        
                        if "duplicate key value violates unique constraint" in error_message:
                            st.warning("⚠️ 이미 존재하는 이메일입니다.")
                        elif "violates check constraint" in error_message:
                            st.warning("⚠️ 권한 값이 올바르지 않습니다.")
    
    except Exception as e:
        st.error(f"관리자 목록을 불러오는 중 오류가 발생했습니다: {str(e)}")

def show_delete_admin(supabase):
    """관리자 삭제 폼을 표시합니다."""
    st.subheader("🗑️ 관리자 삭제")
    
    # 실제 Supabase 연결인지 확인
    is_real_supabase = not hasattr(supabase, '_init_session_state')
    
    if not is_real_supabase:
        st.warning("오프라인 모드에서는 관리자 삭제 기능을 사용할 수 없습니다.")
        return
    
    st.warning("⚠️ 주의: 관리자를 삭제하면 되돌릴 수 없습니다!")
    
    try:
        # 관리자 목록 조회
        response = supabase.table('admins').select('*').execute()
        
        if not response.data:
            st.info("삭제할 관리자가 없습니다.")
            return
        
        # 관리자 선택
        admin_options = {f"{admin['name']} ({admin['email']})": admin for admin in response.data}
        selected_admin_key = st.selectbox("삭제할 관리자 선택", list(admin_options.keys()))
        
        if selected_admin_key:
            selected_admin = admin_options[selected_admin_key]
            
            # 선택된 관리자 정보 표시
            st.subheader("삭제할 관리자 정보")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**이름:** {selected_admin.get('name', '')}")
                st.write(f"**이메일:** {selected_admin.get('email', '')}")
                st.write(f"**권한:** {selected_admin.get('role', '')}")
            
            with col2:
                st.write(f"**부서:** {selected_admin.get('department', '')}")
                st.write(f"**직책:** {selected_admin.get('position', '')}")
                st.write(f"**활성 상태:** {'✅' if selected_admin.get('is_active') else '❌'}")
            
            # 삭제 확인
            st.markdown("---")
            confirm_text = st.text_input(
                "삭제를 확인하려면 '삭제'를 입력하세요:",
                placeholder="삭제"
            )
            
            if st.button("🗑️ 관리자 삭제", type="secondary"):
                if confirm_text != "삭제":
                    st.error("'삭제'를 정확히 입력해야 합니다.")
                    return
                
                try:
                    response = supabase.table('admins').delete().eq('id', selected_admin['id']).execute()
                    
                    if response.data:
                        st.success(f"관리자 '{selected_admin['name']}'이(가) 성공적으로 삭제되었습니다!")
                        st.rerun()
                    else:
                        st.error("관리자 삭제에 실패했습니다.")
                        
                except Exception as e:
                    st.error(f"관리자 삭제 중 오류가 발생했습니다: {str(e)}")
    
    except Exception as e:
        st.error(f"관리자 목록을 불러오는 중 오류가 발생했습니다: {str(e)}")

def validate_email(email):
    """이메일 형식 검증"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def hash_password(password):
    """비밀번호 해시화 (실제 환경에서는 보안 라이브러리 사용 필요)"""
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest() 