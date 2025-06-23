import pandas as pd
from utils.supabase_client import get_supabase_client
import streamlit as st

def get_all_defect_types():
    """
    Supabase 데이터베이스에서 모든 불량 유형을 가져옵니다.
    
    Returns:
        pandas.DataFrame: 불량 유형 데이터프레임 (id, name, description 포함)
    """
    try:
        # Supabase 클라이언트 가져오기
        supabase = get_supabase_client()
        
        # defect_types 테이블에서 모든 데이터 조회 - 캐싱 없이 항상 최신 데이터 조회
        response = supabase.table('defect_types').select('*').order('name').execute()
        
        # 결과를 DataFrame으로 변환
        df = pd.DataFrame(response.data)
        
        # 결과가 없으면 기본 불량 유형 설정
        if df.empty:
            # 기본 불량 유형 생성
            create_default_defect_types()
            
            # 다시 조회
            response = supabase.table('defect_types').select('*').order('name').execute()
            df = pd.DataFrame(response.data)
            
            # 여전히 결과가 없으면 하드코딩된 기본값 반환
            if df.empty:
                default_types = [
                    {"id": "1", "name": "치수 불량", "description": "제품의 치수가 규격을 벗어남"},
                    {"id": "2", "name": "표면 결함", "description": "제품 표면의 긁힘, 찍힘 등의 결함"},
                    {"id": "3", "name": "가공 불량", "description": "가공 공정에서 발생한 불량"},
                    {"id": "4", "name": "재료 결함", "description": "원자재의 결함으로 인한 불량"},
                    {"id": "5", "name": "기타", "description": "기타 불량 유형"}
                ]
                df = pd.DataFrame(default_types)
        
        return df
    
    except Exception as e:
        # 오류 발생 시 하드코딩된 기본값 반환
        default_types = [
            {"id": "1", "name": "치수 불량", "description": "제품의 치수가 규격을 벗어남"},
            {"id": "2", "name": "표면 결함", "description": "제품 표면의 긁힘, 찍힘 등의 결함"},
            {"id": "3", "name": "가공 불량", "description": "가공 공정에서 발생한 불량"},
            {"id": "4", "name": "재료 결함", "description": "원자재의 결함으로 인한 불량"},
            {"id": "5", "name": "기타", "description": "기타 불량 유형"}
        ]
        return pd.DataFrame(default_types)

def create_default_defect_types():
    """
    기본 불량 유형을 데이터베이스에 생성합니다.
    """
    try:
        # Supabase 클라이언트 가져오기
        supabase = get_supabase_client()
        
        # 기본 불량 유형 정의
        default_defect_types = [
            {"name": "치수 불량", "description": "제품의 치수가 규격을 벗어남"},
            {"name": "표면 결함", "description": "제품 표면의 긁힘, 찍힘 등의 결함"},
            {"name": "가공 불량", "description": "가공 공정에서 발생한 불량"},
            {"name": "재료 결함", "description": "원자재의 결함으로 인한 불량"},
            {"name": "기타", "description": "기타 불량 유형"}
        ]
        
        # 테이블에 데이터 삽입
        for defect_type in default_defect_types:
            supabase.table('defect_types').insert(defect_type).execute()
            
    except Exception as e:
        # 오류 처리 (로깅 등 필요 시 여기에 추가)
        pass

def get_defect_type_names():
    """
    불량 유형 이름 목록만 가져옵니다.
    
    Returns:
        list: 불량 유형 이름 목록
    """
    try:
        df = get_all_defect_types()
        return df["name"].tolist()
    except:
        # 오류 발생 시 하드코딩된 기본값 반환
        return ["치수 불량", "표면 결함", "가공 불량", "재료 결함", "기타"] 