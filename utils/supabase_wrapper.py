"""
Supabase 조회 래퍼 함수
모든 데이터 조회 시 자동으로 베트남 시간대로 변환
"""

from utils.supabase_client import get_supabase_client
from utils.data_converter import convert_supabase_data_timezone
import pandas as pd


class SupabaseQueryWrapper:
    """Supabase 조회 시 자동 시간대 변환을 제공하는 래퍼 클래스"""
    
    def __init__(self):
        self.supabase = get_supabase_client()
    
    def select_with_timezone(self, table_name, columns="*", filters=None, order_by=None, limit=None):
        """
        테이블 조회 시 자동으로 시간대 변환 적용
        
        Args:
            table_name: 테이블명
            columns: 조회할 컬럼 (기본값: "*")
            filters: 필터 딕셔너리 [{"column": "value", "operator": "eq"}]
            order_by: 정렬 옵션 [{"column": "created_at", "desc": True}]
            limit: 조회 제한 수
        
        Returns:
            시간대가 변환된 데이터 리스트
        """
        try:
            query = self.supabase.table(table_name).select(columns)
            
            # 필터 적용
            if filters:
                for filter_item in filters:
                    column = filter_item.get('column')
                    value = filter_item.get('value')
                    operator = filter_item.get('operator', 'eq')
                    
                    if operator == 'eq':
                        query = query.eq(column, value)
                    elif operator == 'gte':
                        query = query.gte(column, value)
                    elif operator == 'lte':
                        query = query.lte(column, value)
                    elif operator == 'gt':
                        query = query.gt(column, value)
                    elif operator == 'lt':
                        query = query.lt(column, value)
                    elif operator == 'neq':
                        query = query.neq(column, value)
            
            # 정렬 적용
            if order_by:
                column = order_by.get('column', 'created_at')
                desc = order_by.get('desc', True)
                query = query.order(column, desc=desc)
            
            # 제한 적용
            if limit:
                query = query.limit(limit)
            
            # 실행
            result = query.execute()
            
            # 시간대 변환 적용
            if result.data:
                converted_data = convert_supabase_data_timezone(result.data)
                return converted_data
            else:
                return []
                
        except Exception as e:
            print(f"Supabase 조회 오류 ({table_name}): {e}")
            return []
    
    def select_defects_with_timezone(self, inspection_id=None, limit=None):
        """불량 데이터 조회 (시간대 자동 변환)"""
        filters = []
        if inspection_id:
            filters.append({"column": "inspection_id", "value": inspection_id})
        
        return self.select_with_timezone(
            table_name="defects",
            filters=filters if filters else None,
            order_by={"column": "created_at", "desc": True},
            limit=limit
        )
    
    def select_inspection_data_with_timezone(self, start_date=None, end_date=None, limit=None):
        """검사 데이터 조회 (시간대 자동 변환)"""
        filters = []
        if start_date:
            filters.append({"column": "inspection_date", "value": start_date, "operator": "gte"})
        if end_date:
            filters.append({"column": "inspection_date", "value": end_date, "operator": "lte"})
        
        return self.select_with_timezone(
            table_name="inspection_data",
            filters=filters if filters else None,
            order_by={"column": "inspection_date", "desc": True},
            limit=limit
        )


def get_supabase_wrapper():
    """Supabase 래퍼 인스턴스 반환"""
    return SupabaseQueryWrapper() 