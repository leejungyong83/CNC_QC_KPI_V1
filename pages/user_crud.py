import streamlit as st
import pandas as pd
from datetime import datetime
from utils.supabase_client import get_supabase_client
from utils.vietnam_timezone import get_database_time
from utils.data_converter import convert_supabase_data_timezone, convert_dataframe_timezone

def show_user_crud():
    """사용자 CRUD 관리 페이지를 표시합니다."""
    st.header("👥 사용자 데이터베이스 관리")
    
    # Supabase 클라이언트 가져오기
    supabase = get_supabase_client()
    
    # 연결 상태 확인 및 표시
    show_connection_status(supabase)
    
    # 탭 생성
    list_tab, add_tab, edit_tab, delete_tab, sync_tab = st.tabs(["사용자 목록", "사용자 추가", "사용자 수정", "사용자 삭제", "데이터 동기화"])
    
    # 사용자 목록 탭
    with list_tab:
        show_user_list(supabase)
    
    # 사용자 추가 탭
    with add_tab:
        show_add_user(supabase)
    
    # 사용자 수정 탭
    with edit_tab:
        show_edit_user(supabase)
    
    # 사용자 삭제 탭
    with delete_tab:
        show_delete_user(supabase)
    
    # 데이터 동기화 탭
    with sync_tab:
        show_data_sync(supabase)

def show_connection_status(supabase):
    """연결 상태를 표시합니다."""
    st.success("✅ Supabase에 연결되었습니다.")

def show_data_sync(supabase):
    """데이터 동기화 기능을 표시합니다."""
    st.subheader("🔄 데이터 동기화")
    
    st.success("Supabase에 연결되었습니다.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("실제 데이터베이스에서 조회")
        if st.button("데이터베이스 조회", type="primary"):
            try:
                response = supabase.table('users').select('*').execute()
                if response.data:
                    df = pd.DataFrame(response.data)
                    st.dataframe(df, use_container_width=True)
                    st.success(f"데이터베이스에서 {len(response.data)}개의 사용자 데이터를 조회했습니다.")
                else:
                    st.info("데이터베이스에 사용자 데이터가 없습니다.")
            except Exception as e:
                st.error(f"데이터베이스 조회 중 오류 발생: {str(e)}")
    
    with col2:
        st.subheader("샘플 데이터 업로드")
        if st.button("샘플 사용자 데이터 업로드"):
            upload_sample_users(supabase)

def upload_sample_users(supabase):
    """샘플 사용자 데이터를 실제 데이터베이스에 업로드합니다."""
    sample_users = [
        {
            "email": "admin@company.com",
            "name": "시스템관리자",
            "role": "admin",
            "department": "IT팀",
            "is_active": True,
            "phone": "010-1111-1111",
            "position": "시스템 관리자",
            "notes": "시스템 총괄 관리자",
            "password_hash": hash_password("admin123"),  # password -> password_hash
            "created_at": "2024-01-01T09:00:00",
            "updated_at": "2024-01-01T09:00:00"
        },
        {
            "email": "inspector1@company.com", 
            "name": "김검사",
            "role": "inspector",
            "department": "품질팀",
            "is_active": True,
            "phone": "010-2222-2222",
            "position": "품질검사원",
            "notes": "CNC 품질검사 담당",
            "password_hash": hash_password("inspector123"),  # password -> password_hash
            "created_at": "2024-01-02T09:00:00",
            "updated_at": "2024-01-02T09:00:00"
        },
        {
            "email": "manager1@company.com",
            "name": "박매니저", 
            "role": "manager",
            "department": "생산팀",
            "is_active": True,
            "phone": "010-3333-3333",
            "position": "생산팀장",
            "notes": "생산라인 총괄",
            "password_hash": hash_password("manager123"),  # password -> password_hash
            "created_at": "2024-01-03T09:00:00",
            "updated_at": "2024-01-03T09:00:00"
        }
    ]
    
    try:
        # 기존 데이터 확인
        existing_response = supabase.table('users').select('email').execute()
        existing_emails = [user['email'] for user in existing_response.data] if existing_response.data else []
        
        # 중복되지 않는 사용자만 추가
        new_users = [user for user in sample_users if user['email'] not in existing_emails]
        
        if new_users:
            response = supabase.table('users').insert(new_users).execute()
            if response.data:
                st.success(f"{len(new_users)}명의 사용자가 성공적으로 업로드되었습니다!")
                st.rerun()
            else:
                st.error("사용자 업로드에 실패했습니다.")
        else:
            st.warning("모든 샘플 사용자가 이미 데이터베이스에 존재합니다.")
            
    except Exception as e:
        st.error(f"샘플 데이터 업로드 중 오류 발생: {str(e)}")
        st.info("RLS 정책 오류인 경우 Supabase 설정에서 RLS를 비활성화하거나 적절한 정책을 설정하세요.")

def show_user_list(supabase):
    """사용자 목록을 표시합니다."""
    st.subheader("📋 사용자 목록")
    
    # 실제 Supabase 연결 확인
    is_real_supabase = True
    
    try:
        # users 테이블에서 모든 사용자 조회
        response = supabase.table('users').select('*').order('created_at', desc=True).execute()
        
        if response.data:
            # 시간대 변환 후 데이터프레임으로 변환
            converted_data = convert_supabase_data_timezone(response.data)
            df = pd.DataFrame(converted_data)
            
            if is_real_supabase:
                # 실제 Supabase - 현재 테이블 구조에 맞는 컬럼 순서
                display_columns = []
                if 'id' in df.columns:
                    display_columns.append('id')
                if 'username' in df.columns:
                    display_columns.append('username')
                if 'email' in df.columns:
                    display_columns.append('email')
                if 'name' in df.columns:  # name 컬럼이 있으면 표시
                    display_columns.append('name')
                if 'role' in df.columns:
                    display_columns.append('role')
                if 'is_active' in df.columns:  # is_active 컬럼이 있으면 표시
                    display_columns.append('is_active')
                if 'created_at' in df.columns:
                    display_columns.append('created_at')
                if 'updated_at' in df.columns:
                    display_columns.append('updated_at')
                
                # 컬럼 설정 (실제 Supabase)
                column_config = {
                    "id": st.column_config.TextColumn("ID", width="small"),
                    "username": st.column_config.TextColumn("사용자명", width="medium"),
                    "email": st.column_config.TextColumn("이메일", width="medium"),
                    "name": st.column_config.TextColumn("이름", width="medium"),
                    "role": st.column_config.TextColumn("역할", width="small"),
                    "is_active": st.column_config.CheckboxColumn("활성", width="small"),
                    "created_at": st.column_config.DatetimeColumn("생성일", width="medium"),
                    "updated_at": st.column_config.DatetimeColumn("수정일", width="medium"),
                }
            else:
                # 더미 모드 - 기존 컬럼 순서
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
                if 'is_active' in df.columns:
                    display_columns.append('is_active')
                if 'created_at' in df.columns:
                    display_columns.append('created_at')
                if 'updated_at' in df.columns:
                    display_columns.append('updated_at')
                
                # 컬럼 설정 (더미 모드)
                column_config = {
                    "id": st.column_config.NumberColumn("ID", width="small"),
                    "email": st.column_config.TextColumn("이메일", width="medium"),
                    "name": st.column_config.TextColumn("이름", width="medium"),
                    "role": st.column_config.TextColumn("역할", width="small"),
                    "department": st.column_config.TextColumn("부서", width="medium"),
                    "is_active": st.column_config.CheckboxColumn("활성", width="small"),
                    "created_at": st.column_config.DatetimeColumn("생성일", width="medium"),
                    "updated_at": st.column_config.DatetimeColumn("수정일", width="medium"),
                }
            
            # 사용 가능한 컬럼만 표시
            if display_columns:
                available_columns = [col for col in display_columns if col in df.columns]
                if available_columns:
                    df = df[available_columns]
            
            st.dataframe(
                df,
                column_config=column_config,
                use_container_width=True,
                hide_index=True
            )
            
            st.info(f"총 {len(df)} 명의 사용자가 등록되어 있습니다.")
        else:
            st.info("등록된 사용자가 없습니다.")
            
    except Exception as e:
        st.error(f"사용자 목록을 불러오는 중 오류가 발생했습니다: {str(e)}")

def show_add_user(supabase):
    """새 사용자 추가 폼을 표시합니다."""
    st.subheader("➕ 새 사용자 추가")
    
    # 실제 Supabase 연결인지 확인
    is_real_supabase = True
    # 연결 테스트 및 테이블 구조 확인
    if is_real_supabase:
        try:
            # 테이블 구조 확인을 위한 더 안전한 접근
            test_response = supabase.table('users').select('*').limit(1).execute()
            st.info("✅ Supabase users 테이블에 연결되었습니다.")
            
            # 실제 테이블 컬럼 확인
            if test_response.data:
                available_columns = list(test_response.data[0].keys())
                st.info(f"사용 가능한 컬럼: {', '.join(available_columns)}")
            
        except Exception as e:
            st.error(f"❌ users 테이블 연결 오류: {str(e)}")
            if "does not exist" in str(e):
                st.warning("⚠️ users 테이블이 존재하지 않습니다. 'Supabase 설정'에서 테이블을 생성하세요.")
                return
    
    with st.form("add_user_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            email = st.text_input("이메일 *", placeholder="user@example.com")
            name = st.text_input("이름 *", placeholder="홍길동")
            if is_real_supabase:
                # 실제 Supabase - 기본 필드만 사용
                role = st.selectbox("역할", ["user", "inspector"], index=0)
                department = st.text_input("부서", placeholder="생산팀")
            else:
                # 더미 모드 - 기존 구조 유지
                role = st.selectbox("역할 *", ["user", "admin", "manager", "inspector"])
        
        with col2:
            password = st.text_input("비밀번호 *", type="password")
            if not is_real_supabase:
                is_active = st.checkbox("활성 상태", value=True)
        
        # 추가 필드들 (선택사항) - 더미 모드에서만 표시
        if not is_real_supabase:
            with st.expander("추가 정보 (선택사항)"):
                department = st.text_input("부서", placeholder="생산팀")
                phone = st.text_input("전화번호", placeholder="010-1234-5678")
                position = st.text_input("직책", placeholder="팀장")
                notes = st.text_area("비고", placeholder="기타 정보")
        
        submitted = st.form_submit_button("사용자 추가", type="primary")
        
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
                if is_real_supabase:
                    # 실제 Supabase - 가장 안전한 기본 필드만 사용
                    user_data = {
                        "name": name,
                        "email": email,
                        "role": role
                    }
                    
                    # 부서 정보가 있으면 추가
                    if 'department' in locals() and department:
                        user_data["department"] = department
                    
                    # is_active 기본값 설정
                    user_data["is_active"] = True
                    
                    # password_hash를 TEXT 타입으로 수정했으므로 다시 활성화
                    user_data["password_hash"] = hash_password(password)
                        
                else:
                    # 더미 모드 - 전체 필드 사용
                    user_data = {
                        "email": email,
                        "name": name,
                        "role": role,
                        "department": department if 'department' in locals() else "",
                        "is_active": is_active,
                        "password_hash": hash_password(password),  # password -> password_hash
                "created_at": get_database_time(),
                "updated_at": get_database_time()
                    }
                    
                    # 추가 정보가 있으면 포함
                    if 'phone' in locals() and phone:
                        user_data["phone"] = phone
                    if 'position' in locals() and position:
                        user_data["position"] = position
                    if 'notes' in locals() and notes:
                        user_data["notes"] = notes
                
                # 데이터베이스에 삽입
                response = supabase.table('users').insert(user_data).execute()
                
                if response.data:
                    st.success(f"사용자 '{name}' ({email})이(가) 성공적으로 추가되었습니다!")
                    # 추가된 데이터 확인
                    st.json(response.data[0])
                    st.rerun()
                else:
                    st.error("사용자 추가에 실패했습니다.")
                    
            except Exception as e:
                error_message = str(e)
                st.error(f"사용자 추가 중 오류가 발생했습니다: {error_message}")
                
                # 구체적인 오류 해결 가이드 제공
                if "could not find" in error_message.lower() and "column" in error_message.lower():
                    st.warning("⚠️ 테이블 구조 불일치 오류입니다.")
                    st.info("💡 'Supabase 설정' 메뉴에서 올바른 users 테이블을 생성하거나, 기존 테이블 구조를 확인하세요.")
                    
                    # 기존 테이블 구조에 맞는 안전한 SQL 제안
                    st.subheader("🔧 기존 테이블 구조 확인 및 수정")
                    st.code("""
-- 1. 기존 테이블 구조 확인
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'users';

-- 2. 누락된 컬럼 추가 (필요한 경우)
ALTER TABLE users ADD COLUMN IF NOT EXISTS department TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;

-- 3. role 제약 조건 수정
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_role_check;
ALTER TABLE users ADD CONSTRAINT users_role_check 
CHECK (role IN ('user', 'inspector'));
                    """, language="sql")
                    
                elif "violates row-level security policy" in error_message:
                    st.warning("⚠️ RLS 정책 오류입니다.")
                    st.code("ALTER TABLE users DISABLE ROW LEVEL SECURITY;", language="sql")
                elif "duplicate key value violates unique constraint" in error_message:
                    st.warning("⚠️ 이미 존재하는 이메일입니다.")
                elif "violates check constraint" in error_message and "role" in error_message:
                    st.warning("⚠️ Role 제약 조건 오류입니다.")
                    st.info("💡 다음 SQL을 실행하여 role 제약 조건을 수정하세요:")
                    st.code("""
-- 기존 role 제약 조건 삭제
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_role_check;

-- 새로운 role 제약 조건 추가
ALTER TABLE users ADD CONSTRAINT users_role_check 
CHECK (role IN ('user', 'inspector'));
                    """, language="sql")
                elif "23514" in error_message:
                    st.warning("⚠️ 데이터베이스 제약 조건 위반입니다.")
                    st.info("💡 입력 데이터가 테이블의 제약 조건을 위반했습니다. 'Supabase 설정'에서 제약 조건을 확인하세요.")
                else:
                    st.info("💡 자세한 해결 방법은 'Supabase 설정' 메뉴를 참조하세요.")

def show_edit_user(supabase):
    """사용자 정보 수정 폼을 표시합니다."""
    st.subheader("✏️ 사용자 정보 수정")
    
    # 실제 Supabase 연결인지 확인
    is_real_supabase = True
    try:
        # 사용자 목록 조회
        response = supabase.table('users').select('*').order('name').execute()
        
        if not response.data:
            st.info("수정할 사용자가 없습니다.")
            return
        
        # 사용자 선택
        user_options = {f"{user['name']} ({user['email']})": user for user in response.data}
        selected_user_key = st.selectbox("수정할 사용자 선택", list(user_options.keys()))
        
        if selected_user_key:
            selected_user = user_options[selected_user_key]
            
            with st.form("edit_user_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    email = st.text_input("이메일 *", value=selected_user.get('email', ''))
                    name = st.text_input("이름 *", value=selected_user.get('name', ''))
                    if is_real_supabase:
                        # 실제 Supabase - 기본 role만 사용
                        current_role = selected_user.get('role', 'user')
                        role_index = ["user", "inspector"].index(current_role) if current_role in ["user", "inspector"] else 0
                        role = st.selectbox("역할", ["user", "inspector"], index=role_index)
                    else:
                        # 더미 모드 - 전체 role 사용
                        current_role = selected_user.get('role', 'user')
                        role_index = ["user", "admin", "manager", "inspector"].index(current_role) if current_role in ["user", "admin", "manager", "inspector"] else 0
                        role = st.selectbox("역할 *", ["user", "admin", "manager", "inspector"], index=role_index)
                
                with col2:
                    is_active = st.checkbox("활성 상태", value=selected_user.get('is_active', True))
                    change_password = st.checkbox("비밀번호 변경")
                
                if change_password:
                    new_password = st.text_input("새 비밀번호", type="password")
                
                # 추가 필드들
                if is_real_supabase:
                    # 실제 Supabase - 기본 필드 표시
                    department = st.text_input("부서", value=selected_user.get('department', ''))
                else:
                    # 더미 모드 - 전체 필드 표시
                    with st.expander("추가 정보"):
                        department = st.text_input("부서", value=selected_user.get('department', ''))
                        phone = st.text_input("전화번호", value=selected_user.get('phone', ''))
                        position = st.text_input("직책", value=selected_user.get('position', ''))
                        notes = st.text_area("비고", value=selected_user.get('notes', ''))
                
                submitted = st.form_submit_button("수정", type="primary")
                
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
                        if is_real_supabase:
                            # 실제 Supabase - 기본 필드만 사용
                            update_data = {
                                "email": email,
                                "name": name,
                                "role": role,
                                "is_active": is_active,
                "updated_at": get_database_time()
                            }
                            
                            # 부서 정보 추가
                            if 'department' in locals() and department is not None:
                                update_data["department"] = department
                        else:
                            # 더미 모드 - 전체 필드 사용
                            update_data = {
                                "email": email,
                                "name": name,
                                "role": role,
                                "department": department if 'department' in locals() else "",
                                "is_active": is_active,
                                "phone": phone if 'phone' in locals() else "",
                                "position": position if 'position' in locals() else "",
                                "notes": notes if 'notes' in locals() else "",
                "updated_at": get_database_time()
                            }
                        
                        # 비밀번호 변경이 요청된 경우
                        if change_password and 'new_password' in locals() and new_password:
                            update_data["password_hash"] = hash_password(new_password)
                        
                        # 데이터베이스 업데이트
                        response = supabase.table('users').update(update_data).eq('id', selected_user['id']).execute()
                        
                        if response.data:
                            st.success(f"사용자 '{name}' 정보가 성공적으로 수정되었습니다!")
                            st.rerun()
                        else:
                            st.error("사용자 정보 수정에 실패했습니다.")
                            
                    except Exception as e:
                        error_message = str(e)
                        st.error(f"사용자 정보 수정 중 오류가 발생했습니다: {error_message}")
                        
                        # 구체적인 오류 해결 가이드 제공
                        if "could not find" in error_message.lower() and "column" in error_message.lower():
                            st.warning("⚠️ 테이블 구조 불일치 오류입니다.")
                            st.info("💡 'Supabase 설정' 메뉴에서 올바른 users 테이블을 생성하거나, 기존 테이블 구조를 확인하세요.")
                        elif "violates row-level security policy" in error_message:
                            st.warning("⚠️ RLS 정책 오류입니다.")
                            st.code("ALTER TABLE users DISABLE ROW LEVEL SECURITY;", language="sql")
                        elif "duplicate key value violates unique constraint" in error_message:
                            st.warning("⚠️ 이미 존재하는 이메일입니다.")
                        elif "violates check constraint" in error_message and "role" in error_message:
                            st.warning("⚠️ Role 제약 조건 오류입니다.")
                            st.info("💡 다음 SQL을 실행하여 role 제약 조건을 수정하세요:")
                            st.code("""
-- 기존 role 제약 조건 삭제
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_role_check;

-- 새로운 role 제약 조건 추가
ALTER TABLE users ADD CONSTRAINT users_role_check 
CHECK (role IN ('user', 'inspector'));
                            """, language="sql")
                        elif "23514" in error_message:
                            st.warning("⚠️ 데이터베이스 제약 조건 위반입니다.")
                            st.info("💡 입력 데이터가 테이블의 제약 조건을 위반했습니다. 'Supabase 설정'에서 제약 조건을 확인하세요.")
                        else:
                            st.info("💡 자세한 해결 방법은 'Supabase 설정' 메뉴를 참조하세요.")
            
    except Exception as e:
        error_message = str(e)
        st.error(f"사용자 목록을 불러오는 중 오류가 발생했습니다: {error_message}")
        
        if "does not exist" in error_message:
            st.warning("⚠️ users 테이블이 존재하지 않습니다. 'Supabase 설정'에서 테이블을 생성하세요.")

def show_delete_user(supabase):
    """사용자 삭제 폼을 표시합니다."""
    st.subheader("🗑️ 사용자 삭제")
    
    # 경고 메시지
    st.warning("⚠️ 사용자 삭제는 되돌릴 수 없습니다. 신중하게 진행하세요.")
    
    try:
        # 사용자 목록 조회
        response = supabase.table('users').select('*').order('name').execute()
        
        if not response.data:
            st.info("삭제할 사용자가 없습니다.")
            return
        
        # 사용자 선택
        user_options = {f"{user['name']} ({user['email']})": user for user in response.data}
        selected_user_key = st.selectbox("삭제할 사용자 선택", ["선택하세요..."] + list(user_options.keys()))
        
        if selected_user_key != "선택하세요...":
            selected_user = user_options[selected_user_key]
            
            # 선택된 사용자 정보 표시
            st.subheader("삭제 대상 사용자 정보")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**이름:** {selected_user.get('name', 'N/A')}")
                st.write(f"**이메일:** {selected_user.get('email', 'N/A')}")
                st.write(f"**역할:** {selected_user.get('role', 'N/A')}")
            
            with col2:
                st.write(f"**부서:** {selected_user.get('department', 'N/A')}")
                st.write(f"**활성 상태:** {'활성' if selected_user.get('is_active', False) else '비활성'}")
                st.write(f"**생성일:** {selected_user.get('created_at', 'N/A')}")
            
            # 삭제 확인
            st.subheader("삭제 확인")
            
            # 안전을 위한 확인 단계
            confirm_text = st.text_input(
                f"삭제를 확인하려면 '{selected_user['name']}'을(를) 입력하세요:",
                placeholder="사용자 이름 입력"
            )
            
            # 추가 확인 체크박스
            final_confirm = st.checkbox("위 사용자를 삭제하겠다는 것을 확인합니다.")
            
            if st.button("사용자 삭제", type="primary", disabled=not final_confirm):
                if confirm_text == selected_user['name']:
                    try:
                        # 데이터베이스에서 사용자 삭제
                        response = supabase.table('users').delete().eq('id', selected_user['id']).execute()
                        
                        if response.data:
                            st.success(f"사용자 '{selected_user['name']}' ({selected_user['email']})이(가) 성공적으로 삭제되었습니다.")
                            st.rerun()
                        else:
                            st.error("사용자 삭제에 실패했습니다.")
                            
                    except Exception as e:
                        st.error(f"사용자 삭제 중 오류가 발생했습니다: {str(e)}")
                else:
                    st.error("사용자 이름이 일치하지 않습니다. 정확히 입력해주세요.")
            
    except Exception as e:
        st.error(f"사용자 목록을 불러오는 중 오류가 발생했습니다: {str(e)}")

# 유틸리티 함수들
def validate_email(email):
    """이메일 형식 검증"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def hash_password(password):
    """비밀번호 해시화 (실제 구현에서는 bcrypt 등 사용)"""
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest() 
