import os
import streamlit as st
from supabase import create_client, Client
from datetime import datetime
import uuid

def get_supabase_client() -> Client:
    """Supabase 클라이언트를 반환합니다. 실패시 더미 클라이언트 반환."""
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
        
        # 둘 다 없으면 더미 클라이언트 반환
        if not supabase_url or not supabase_key:
            st.warning("⚠️ Supabase 설정이 없습니다. 오프라인 모드로 실행됩니다.")
            return DummySupabaseClient()
        
        # 실제 Supabase 클라이언트 생성
        supabase = create_client(supabase_url, supabase_key)
        
        # 연결 테스트
        try:
            test_response = supabase.table('users').select('id').limit(1).execute()
            return supabase
        except Exception as e:
            st.warning(f"⚠️ Supabase 연결 실패: {str(e)}. 오프라인 모드로 실행됩니다.")
            return DummySupabaseClient()
            
    except Exception as e:
        st.warning(f"⚠️ Supabase 클라이언트 생성 실패: {str(e)}. 오프라인 모드로 실행됩니다.")
        return DummySupabaseClient()

class DummySupabaseClient:
    """오프라인 모드에서 사용할 수 있는 더미 Supabase 클라이언트"""
    
    def __init__(self):
        # 세션 상태 초기화를 더 확실하게 처리
        self._init_session_state()
    
    def _init_session_state(self):
        """세션 상태를 확실하게 초기화"""
        if 'dummy_defect_types' not in st.session_state:
            st.session_state.dummy_defect_types = [
                {"id": "1", "name": "치수 불량", "description": "제품의 치수가 규격을 벗어남"},
                {"id": "2", "name": "표면 결함", "description": "제품 표면의 긁힘, 찍힘 등의 결함"},
                {"id": "3", "name": "가공 불량", "description": "가공 공정에서 발생한 불량"},
                {"id": "4", "name": "재료 결함", "description": "원자재의 결함으로 인한 불량"},
                {"id": "5", "name": "기타", "description": "기타 불량 유형"}
            ]
        
        if 'dummy_users' not in st.session_state:
            st.session_state.dummy_users = [
                {
                    "id": 1,
                    "email": "admin@example.com",
                    "name": "관리자",
                    "role": "admin",
                    "department": "관리팀",
                    "is_active": True,
                    "phone": "010-1234-5678",
                    "position": "시스템 관리자",
                    "notes": "시스템 총 관리자",
                    "created_at": "2024-01-01T00:00:00",
                    "updated_at": "2024-01-01T00:00:00"
                },
                {
                    "id": 2,
                    "email": "user1@example.com",
                    "name": "홍길동",
                    "role": "user",
                    "department": "생산팀",
                    "is_active": True,
                    "phone": "010-2345-6789",
                    "position": "검사원",
                    "notes": "품질검사 담당",
                    "created_at": "2024-01-02T00:00:00",
                    "updated_at": "2024-01-02T00:00:00"
                },
                {
                    "id": 3,
                    "email": "manager1@example.com",
                    "name": "김영희",
                    "role": "manager",
                    "department": "품질팀",
                    "is_active": True,
                    "phone": "010-3456-7890",
                    "position": "팀장",
                    "notes": "품질팀 매니저",
                    "created_at": "2024-01-03T00:00:00",
                    "updated_at": "2024-01-03T00:00:00"
                }
            ]
        
        # production_models 더미 데이터 초기화 (Supabase 실제 데이터와 일치)
        if 'dummy_production_models' not in st.session_state:
            st.session_state.dummy_production_models = [
                {
                    "id": "1df2409d-a5b2-46c3-ac9e-9857ea6b24d1",
                    "model_no": "AUTO-202505211130839",
                    "model_name": "PA1",
                    "process": "CNC2_PQC",
                    "notes": "오프라인 모드 - Supabase 동일 데이터",
                    "created_at": "2025-05-21T06:08:39.297Z",
                    "updated_at": "2025-05-21T06:08:39.297Z"
                },
                {
                    "id": "d7464e2e-bdd0-49f8-b1cd-35a826fe23b1",
                    "model_no": "AUTO-202505211104305",
                    "model_name": "PA2",
                    "process": "OQC",
                    "notes": "오프라인 모드 - Supabase 동일 데이터",
                    "created_at": "2025-05-21T03:43:05.326Z",
                    "updated_at": "2025-05-21T03:43:05.326Z"
                }
            ]
        
        if 'dummy_last_id' not in st.session_state:
            st.session_state.dummy_last_id = 5
        
        if 'dummy_last_user_id' not in st.session_state:
            st.session_state.dummy_last_user_id = 3
        
        if 'dummy_last_model_id' not in st.session_state:
            st.session_state.dummy_last_model_id = 2
    
    def table(self, table_name):
        """테이블 객체를 반환합니다."""
        return DummyTable(table_name, self)
    
    def get_defect_types(self):
        """현재 불량 유형 목록을 반환합니다."""
        self._init_session_state()
        return st.session_state.dummy_defect_types
    
    def add_defect_type(self, data):
        """불량 유형을 추가합니다."""
        self._init_session_state()
        st.session_state.dummy_last_id += 1
        new_item = {
            "id": str(st.session_state.dummy_last_id),
            "name": data.get("name", ""),
            "description": data.get("description", "")
        }
        st.session_state.dummy_defect_types.append(new_item)
        return [new_item]
    
    def update_defect_type(self, defect_id, data):
        """불량 유형을 수정합니다."""
        self._init_session_state()
        for i, item in enumerate(st.session_state.dummy_defect_types):
            if item["id"] == defect_id:
                st.session_state.dummy_defect_types[i].update(data)
                return [st.session_state.dummy_defect_types[i]]
        return []
    
    def delete_defect_type(self, defect_id):
        """불량 유형을 삭제합니다."""
        self._init_session_state()
        for i, item in enumerate(st.session_state.dummy_defect_types):
            if item["id"] == defect_id:
                deleted = st.session_state.dummy_defect_types.pop(i)
                return [deleted]
        return []
    
    # Users 테이블 관련 메서드들
    def get_users(self):
        """현재 사용자 목록을 반환합니다."""
        self._init_session_state()
        return st.session_state.dummy_users
    
    def add_user(self, data):
        """사용자를 추가합니다."""
        self._init_session_state()
        st.session_state.dummy_last_user_id += 1
        new_user = data.copy()
        new_user["id"] = st.session_state.dummy_last_user_id
        st.session_state.dummy_users.append(new_user)
        return [new_user]
    
    def update_user(self, user_id, data):
        """사용자 정보를 수정합니다."""
        self._init_session_state()
        for i, user in enumerate(st.session_state.dummy_users):
            if user["id"] == user_id:
                st.session_state.dummy_users[i].update(data)
                return [st.session_state.dummy_users[i]]
        return []
    
    def delete_user(self, user_id):
        """사용자를 삭제합니다."""
        self._init_session_state()
        for i, user in enumerate(st.session_state.dummy_users):
            if user["id"] == user_id:
                deleted = st.session_state.dummy_users.pop(i)
                return [deleted]
        return []
    
    # Production Models 테이블 관련 메서드들
    def get_production_models(self):
        """현재 생산모델 목록을 반환합니다."""
        self._init_session_state()
        return st.session_state.dummy_production_models
    
    def add_production_model(self, data):
        """생산모델을 추가합니다."""
        self._init_session_state()
        new_id = str(uuid.uuid4())
        new_model = {
            "id": new_id,
            "model_no": data.get("model_no", ""),
            "model_name": data.get("model_name", ""),
            "process": data.get("process", ""),
            "notes": data.get("notes", ""),
            "created_at": data.get("created_at", datetime.now().isoformat()),
            "updated_at": data.get("updated_at", datetime.now().isoformat())
        }
        st.session_state.dummy_production_models.append(new_model)
        return [new_model]
    
    def update_production_model(self, model_id, data):
        """생산모델을 수정합니다."""
        self._init_session_state()
        for i, model in enumerate(st.session_state.dummy_production_models):
            if model["id"] == model_id:
                st.session_state.dummy_production_models[i].update(data)
                st.session_state.dummy_production_models[i]["updated_at"] = datetime.now().isoformat()
                return [st.session_state.dummy_production_models[i]]
        return []
    
    def delete_production_model(self, model_id):
        """생산모델을 삭제합니다."""
        self._init_session_state()
        for i, model in enumerate(st.session_state.dummy_production_models):
            if model["id"] == model_id:
                deleted = st.session_state.dummy_production_models.pop(i)
                return [deleted]
        return []

class DummyTable:
    """더미 테이블 객체"""
    
    def __init__(self, table_name, client):
        self.table_name = table_name
        self.client = client
        self._reset_query()
    
    def _reset_query(self):
        """쿼리 상태 초기화"""
        self._operation = None
        self._data = None
        self._where_column = None
        self._where_value = None
        self._order_column = None
        self._order_desc = False
    
    def select(self, select_query="*"):
        """SELECT 쿼리 설정"""
        self._operation = "select"
        return self
    
    def order(self, column, desc=False):
        """ORDER BY 쿼리 설정"""
        self._order_column = column
        self._order_desc = desc
        return self
    
    def insert(self, data):
        """INSERT 쿼리 설정"""
        self._operation = "insert"
        self._data = data
        return self
    
    def update(self, data):
        """UPDATE 쿼리 설정"""
        self._operation = "update"
        self._data = data
        return self
    
    def eq(self, column, value):
        """WHERE 조건 설정"""
        self._where_column = column
        self._where_value = value
        return self
    
    def execute(self):
        """쿼리 실행"""
        
        class Response:
            def __init__(self, data):
                self.data = data
        
        if self.table_name == "production_models":
            if self._operation == "select":
                models = self.client.get_production_models()
                return Response(models)
            elif self._operation == "insert":
                result = self.client.add_production_model(self._data)
                return Response(result)
            elif self._operation == "update":
                result = self.client.update_production_model(self._where_value, self._data)
                return Response(result)
            elif self._operation == "delete":
                result = self.client.delete_production_model(self._where_value)
                return Response(result)
        
        elif self.table_name == "defect_types":
            if self._operation == "select":
                defects = self.client.get_defect_types()
                return Response(defects)
            elif self._operation == "insert":
                result = self.client.add_defect_type(self._data)
                return Response(result)
            elif self._operation == "update":
                result = self.client.update_defect_type(self._where_value, self._data)
                return Response(result)
            elif self._operation == "delete":
                result = self.client.delete_defect_type(self._where_value)
                return Response(result)
        
        elif self.table_name == "users":
            if self._operation == "select":
                users = self.client.get_users()
                return Response(users)
            elif self._operation == "insert":
                result = self.client.add_user(self._data)
                return Response(result)
            elif self._operation == "update":
                result = self.client.update_user(self._where_value, self._data)
                return Response(result)
            elif self._operation == "delete":
                result = self.client.delete_user(self._where_value)
                return Response(result)
        
        # 기본 응답
        return Response([])
    
    def limit(self, count):
        """LIMIT 설정 (더미에서는 무시)"""
        return self
    
    def delete(self):
        """DELETE 쿼리 설정"""
        self._operation = "delete"
        return self 