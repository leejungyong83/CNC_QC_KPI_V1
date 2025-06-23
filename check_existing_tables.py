#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
기존 테이블 구조 확인 및 설정 스크립트
새로운 테이블을 만들지 않고 기존 테이블을 확인합니다.
"""

import streamlit as st
import os
from utils.supabase_client import clear_local_dummy_data, get_supabase_client

def main():
    st.set_page_config(
        page_title="🔍 기존 테이블 확인",
        page_icon="🔍",
        layout="wide"
    )
    
    st.title("🔍 기존 테이블 구조 확인")
    st.success("✅ **테이블이 이미 존재합니다! 새로 만들 필요가 없어요.**")
    st.markdown("---")
    
    # 1단계: 로컬 더미 데이터 제거
    st.header("1️⃣ 로컬 목업 데이터 제거")
    
    if st.button("🗑️ 로컬 더미 데이터 모두 삭제", type="primary"):
        cleared_count = clear_local_dummy_data()
        if cleared_count > 0:
            st.success(f"✅ {cleared_count}개의 로컬 더미 데이터 항목을 삭제했습니다!")
        else:
            st.info("이미 로컬 더미 데이터가 정리되어 있습니다.")
    
    st.markdown("---")
    
    # 2단계: Supabase 연결 정보 설정 (간소화)
    st.header("2️⃣ Supabase 연결 정보 설정")
    
    st.markdown("**.streamlit/secrets.toml 파일에 실제 연결 정보를 입력하세요:**")
    
    st.code("""
# .streamlit/secrets.toml 파일 수정:

SUPABASE_URL = "https://your-actual-project-id.supabase.co"
SUPABASE_KEY = "your-actual-anon-key"
    """, language="toml")
    
    st.markdown("---")
    
    # 3단계: 연결 테스트 및 테이블 확인
    st.header("3️⃣ 연결 테스트 및 기존 테이블 확인")
    
    if st.button("🔗 Supabase 연결 및 테이블 확인", type="primary"):
        try:
            supabase = get_supabase_client()
            st.success("✅ Supabase에 성공적으로 연결되었습니다!")
            
            # 테이블 확인
            st.subheader("📋 기존 테이블 상태 확인")
            
            tables_info = [
                ("users", "사용자 관리"),
                ("production_models", "생산 모델"),
                ("inspectors", "검사원 관리"),
                ("inspection_data", "검사 실적"),
                ("defect_types", "불량 유형"),
                ("defects", "불량 데이터"),
                ("admins", "관리자 (선택사항)")
            ]
            
            working_tables = []
            
            for table_name, description in tables_info:
                try:
                    response = supabase.table(table_name).select('*').limit(1).execute()
                    st.success(f"✅ **{table_name}** - {description} (접근 가능)")
                    working_tables.append(table_name)
                    
                    # 데이터 개수 확인
                    count_response = supabase.table(table_name).select('id').execute()
                    data_count = len(count_response.data) if count_response.data else 0
                    st.info(f"   📊 현재 {data_count}개의 레코드가 있습니다.")
                    
                except Exception as e:
                    st.error(f"❌ **{table_name}** 접근 실패: {str(e)}")
                    
                    # RLS 문제일 가능성 높음
                    if "policy" in str(e).lower() or "rls" in str(e).lower():
                        st.warning(f"   💡 {table_name} 테이블에 RLS가 활성화되어 있을 수 있습니다.")
                        st.code(f"ALTER TABLE {table_name} DISABLE ROW LEVEL SECURITY;", language="sql")
            
            if len(working_tables) >= 5:  # 주요 테이블들이 작동하면
                st.success("🎉 **모든 주요 테이블이 정상 작동합니다!**")
                st.balloons()
            else:
                st.warning("⚠️ 일부 테이블에 접근 문제가 있습니다. RLS 설정을 확인해주세요.")
                    
        except Exception as e:
            st.error(f"❌ 연결 실패: {str(e)}")
            st.error("**Supabase 연결 정보를 다시 확인해주세요!**")
    
    st.markdown("---")
    
    # 4단계: RLS 비활성화 SQL (필요시만)
    st.header("4️⃣ RLS 비활성화 (필요한 경우만)")
    
    st.markdown("**만약 테이블 접근 오류가 있다면, Supabase SQL Editor에서 다음을 실행하세요:**")
    
    with st.expander("🔧 RLS 비활성화 SQL (개발용)"):
        st.code("""
-- 모든 테이블의 RLS(Row Level Security) 비활성화 (개발용)
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE production_models DISABLE ROW LEVEL SECURITY;
ALTER TABLE inspectors DISABLE ROW LEVEL SECURITY;
ALTER TABLE inspection_data DISABLE ROW LEVEL SECURITY;
ALTER TABLE defect_types DISABLE ROW LEVEL SECURITY;
ALTER TABLE defects DISABLE ROW LEVEL SECURITY;
ALTER TABLE admins DISABLE ROW LEVEL SECURITY;
        """, language="sql")
    
    st.markdown("---")
    
    # 5단계: 테스트 데이터 확인
    st.header("5️⃣ 테스트 데이터 확인")
    
    if st.button("📊 현재 데이터 미리보기", type="secondary"):
        try:
            supabase = get_supabase_client()
            
            # users 테이블 미리보기
            st.subheader("👥 Users 테이블")
            users_response = supabase.table('users').select('email, name, role, is_active').limit(5).execute()
            if users_response.data:
                st.dataframe(users_response.data)
            else:
                st.info("users 테이블이 비어있습니다.")
            
            # production_models 테이블 미리보기
            st.subheader("🏭 Production Models 테이블")
            models_response = supabase.table('production_models').select('model_no, model_name, process').limit(5).execute()
            if models_response.data:
                st.dataframe(models_response.data)
            else:
                st.info("production_models 테이블이 비어있습니다.")
                
        except Exception as e:
            st.error(f"데이터 미리보기 실패: {str(e)}")
    
    st.markdown("---")
    st.success("🎉 **설정 완료! 이제 메인 앱을 실행하세요:**")
    st.code("streamlit run app.py", language="bash")

if __name__ == "__main__":
    main() 