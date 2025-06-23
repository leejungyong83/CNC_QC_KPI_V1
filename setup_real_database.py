#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
실제 데이터베이스 연결 설정 스크립트
로컬 목업 데이터를 제거하고 Supabase 연결을 설정합니다.
"""

import streamlit as st
import os
from utils.supabase_client import clear_local_dummy_data, get_supabase_client

def main():
    st.set_page_config(
        page_title="🔧 실제 데이터베이스 연결 설정",
        page_icon="🔧",
        layout="wide"
    )
    
    st.title("🔧 실제 데이터베이스 연결 설정")
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
    
    # 2단계: Supabase 연결 정보 설정
    st.header("2️⃣ Supabase 연결 정보 설정")
    
    st.markdown("""
    **다음 방법 중 하나를 선택해서 Supabase 연결 정보를 설정하세요:**
    
    ### 방법 1: .streamlit/secrets.toml 파일 수정 (권장)
    """)
    
    st.code("""
# .streamlit/secrets.toml 파일에 다음 내용을 입력하세요:

SUPABASE_URL = "https://your-project-id.supabase.co"
SUPABASE_KEY = "your-anon-key-here"

# 실제 값 예시:
# SUPABASE_URL = "https://abcdefghijk.supabase.co"
# SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXB..."
    """, language="toml")
    
    st.markdown("### 방법 2: 환경변수 설정")
    st.code("""
# PowerShell에서:
$env:SUPABASE_URL="https://your-project-id.supabase.co"
$env:SUPABASE_KEY="your-anon-key-here"

# 또는 Command Prompt에서:
set SUPABASE_URL=https://your-project-id.supabase.co
set SUPABASE_KEY=your-anon-key-here
    """, language="bash")
    
    st.markdown("---")
    
    # 3단계: 연결 테스트
    st.header("3️⃣ 연결 테스트")
    
    if st.button("🔗 Supabase 연결 테스트", type="primary"):
        try:
            supabase = get_supabase_client()
            st.success("✅ Supabase에 성공적으로 연결되었습니다!")
            
            # 테이블 존재 여부 확인
            st.subheader("📋 필요한 테이블 확인")
            
            tables_to_check = [
                'users', 'admins', 'production_models', 
                'inspectors', 'inspection_data', 'defect_types', 'defects'
            ]
            
            for table_name in tables_to_check:
                try:
                    response = supabase.table(table_name).select('*').limit(1).execute()
                    st.success(f"✅ {table_name} 테이블 접근 가능")
                except Exception as e:
                    st.error(f"❌ {table_name} 테이블 접근 실패: {str(e)}")
                    
        except Exception as e:
            st.error(f"❌ 연결 실패: {str(e)}")
    
    st.markdown("---")
    
    # 4단계: 필요한 테이블 생성 SQL
    st.header("4️⃣ 필요한 테이블 생성 SQL")
    
    st.markdown("**Supabase SQL Editor에서 다음 SQL을 실행하여 필요한 테이블들을 생성하세요:**")
    
    with st.expander("📝 users 테이블 생성 SQL"):
        st.code("""
-- users 테이블 생성
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    employee_id TEXT UNIQUE,
    department TEXT,
    role TEXT DEFAULT 'user' CHECK (role IN ('user', 'inspector', 'admin')),
    is_active BOOLEAN DEFAULT true,
    password TEXT,
    password_hash TEXT,
    phone TEXT,
    position TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- RLS 비활성화 (개발용)
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
        """, language="sql")
    
    with st.expander("📝 production_models 테이블 생성 SQL"):
        st.code("""
-- production_models 테이블 생성
CREATE TABLE IF NOT EXISTS production_models (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    model_no TEXT UNIQUE NOT NULL,
    model_name TEXT NOT NULL,
    process TEXT NOT NULL,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_production_models_model_no ON production_models(model_no);
CREATE INDEX IF NOT EXISTS idx_production_models_model_name ON production_models(model_name);

-- RLS 비활성화 (개발용)
ALTER TABLE production_models DISABLE ROW LEVEL SECURITY;
        """, language="sql")
    
    with st.expander("📝 defect_types 테이블 생성 SQL"):
        st.code("""
-- defect_types 테이블 생성
CREATE TABLE IF NOT EXISTS defect_types (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- RLS 비활성화 (개발용)
ALTER TABLE defect_types DISABLE ROW LEVEL SECURITY;
        """, language="sql")
    
    with st.expander("📝 inspectors 테이블 생성 SQL"):
        st.code("""
-- inspectors 테이블 생성
CREATE TABLE IF NOT EXISTS inspectors (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    employee_id TEXT UNIQUE,
    department TEXT,
    phone TEXT,
    position TEXT,
    is_active BOOLEAN DEFAULT true,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- RLS 비활성화 (개발용)
ALTER TABLE inspectors DISABLE ROW LEVEL SECURITY;
        """, language="sql")
    
    with st.expander("📝 inspection_data 테이블 생성 SQL"):
        st.code("""
-- inspection_data 테이블 생성
CREATE TABLE IF NOT EXISTS inspection_data (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    inspection_date DATE NOT NULL,
    inspector_id UUID REFERENCES inspectors(id),
    model_id UUID REFERENCES production_models(id),
    result TEXT CHECK (result IN ('합격', '불합격')),
    quantity INTEGER,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- RLS 비활성화 (개발용)
ALTER TABLE inspection_data DISABLE ROW LEVEL SECURITY;
        """, language="sql")
    
    st.markdown("---")
    
    # 5단계: 기본 데이터 삽입
    st.header("5️⃣ 기본 데이터 삽입")
    
    if st.button("📊 기본 샘플 데이터 삽입", type="secondary"):
        st.info("이 기능은 테이블 생성 후 사용 가능합니다.")
    
    st.markdown("---")
    st.success("🎉 **설정 완료 후 메인 앱을 다시 시작하세요!**")

if __name__ == "__main__":
    main() 