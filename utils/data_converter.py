"""
데이터 변환 유틸리티
Supabase 데이터 조회 시 시간대 자동 변환 기능 제공
"""

import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
from utils.vietnam_timezone import convert_utc_to_vietnam, get_vietnam_display_time


def convert_supabase_data_timezone(data: List[Dict[str, Any]], 
                                   time_columns: List[str] = None) -> List[Dict[str, Any]]:
    """
    Supabase에서 조회한 데이터의 시간 컬럼들을 베트남 시간대로 변환
    
    Args:
        data: Supabase에서 조회한 데이터 리스트
        time_columns: 변환할 시간 컬럼명 리스트 (None이면 자동 감지)
    
    Returns:
        시간대가 변환된 데이터 리스트
    """
    if not data:
        return data
    
    # 기본 시간 컬럼들
    if time_columns is None:
        time_columns = [
            'created_at', 'updated_at', 'inspection_date', 
            'last_login', 'timestamp', 'date_created'
        ]
    
    converted_data = []
    
    for row in data:
        converted_row = row.copy()
        
        for column in time_columns:
            if column in converted_row and converted_row[column]:
                try:
                    # UTC 시간을 베트남 시간으로 변환
                    utc_time = converted_row[column]
                    vietnam_time = convert_utc_to_vietnam(utc_time)
                    
                    # 날짜만 필요한 경우와 전체 시간이 필요한 경우 구분
                    if column == 'inspection_date':
                        converted_row[column] = vietnam_time.strftime('%Y-%m-%d')
                    else:
                        converted_row[column] = vietnam_time.strftime('%Y-%m-%d %H:%M:%S')
                        
                except Exception as e:
                    # 변환 실패 시 원본 유지
                    print(f"시간 변환 실패 ({column}): {e}")
                    pass
        
        converted_data.append(converted_row)
    
    return converted_data


def convert_dataframe_timezone(df: pd.DataFrame, 
                               time_columns: List[str] = None) -> pd.DataFrame:
    """
    DataFrame의 시간 컬럼들을 베트남 시간대로 변환
    
    Args:
        df: 변환할 DataFrame
        time_columns: 변환할 시간 컬럼명 리스트 (None이면 자동 감지)
    
    Returns:
        시간대가 변환된 DataFrame
    """
    if df.empty:
        return df
    
    # 기본 시간 컬럼들
    if time_columns is None:
        time_columns = [
            'created_at', 'updated_at', 'inspection_date', 
            'last_login', 'timestamp', 'date_created'
        ]
    
    df_converted = df.copy()
    
    for column in time_columns:
        if column in df_converted.columns:
            try:
                # 각 행의 시간을 베트남 시간으로 변환
                def convert_time(time_str):
                    if pd.isna(time_str) or time_str == '':
                        return time_str
                    try:
                        vietnam_time = convert_utc_to_vietnam(time_str)
                        if column == 'inspection_date':
                            return vietnam_time.strftime('%Y-%m-%d')
                        else:
                            return vietnam_time.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        return time_str
                
                df_converted[column] = df_converted[column].apply(convert_time)
                
            except Exception as e:
                print(f"DataFrame 시간 변환 실패 ({column}): {e}")
                pass
    
    return df_converted


def format_time_for_display(time_value, format_type='datetime'):
    """
    시간 값을 베트남 시간대로 변환하여 표시용 형식으로 포맷
    
    Args:
        time_value: 시간 값 (문자열 또는 datetime)
        format_type: 'datetime', 'date', 'time' 중 하나
    
    Returns:
        포맷된 시간 문자열
    """
    if not time_value:
        return ''
    
    try:
        vietnam_time = convert_utc_to_vietnam(time_value)
        
        if format_type == 'date':
            return vietnam_time.strftime('%Y-%m-%d')
        elif format_type == 'time':
            return vietnam_time.strftime('%H:%M:%S')
        else:  # datetime
            return vietnam_time.strftime('%Y-%m-%d %H:%M:%S')
            
    except Exception:
        return str(time_value)


# 편의 함수들
def get_vietnam_formatted_time(format_type='datetime'):
    """현재 베트남 시간을 원하는 형식으로 반환"""
    vietnam_now = get_vietnam_display_time()
    
    if format_type == 'date':
        return vietnam_now.strftime('%Y-%m-%d')
    elif format_type == 'time':
        return vietnam_now.strftime('%H:%M:%S')
    else:  # datetime
        return vietnam_now.strftime('%Y-%m-%d %H:%M:%S') 