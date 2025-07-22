-- ========================================
-- CNC QC KPI 시스템 통합 데이터베이스 스키마
-- ========================================
-- 생성일: 2025-01-15
-- 목적: 모든 테이블을 하나의 표준 스키마로 통합
-- 사용법: Supabase SQL Editor에서 전체 스크립트 실행

-- ========================================
-- 1. 기존 테이블 정리 (선택사항)
-- ========================================
-- 주의: 아래 DROP 문은 기존 데이터를 완전히 삭제합니다!
-- 개발 환경에서만 사용하고, 운영 환경에서는 주석 처리하세요.

-- DROP TABLE IF EXISTS defects CASCADE;
-- DROP TABLE IF EXISTS inspection_data CASCADE;
-- DROP TABLE IF EXISTS production_models CASCADE;
-- DROP TABLE IF EXISTS inspectors CASCADE;
-- DROP TABLE IF EXISTS defect_types CASCADE;
-- DROP TABLE IF EXISTS users CASCADE;
-- DROP TABLE IF EXISTS admins CASCADE;

-- ========================================
-- 2. 사용자 관련 테이블
-- ========================================

-- 2.1. users 테이블 (일반 사용자 및 검사자)
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    employee_id TEXT UNIQUE,
    department TEXT,
    role TEXT DEFAULT 'user' CHECK (role IN ('user', 'inspector', 'manager', 'admin')),
    password TEXT,
    password_hash TEXT,
    salt TEXT,
    is_active BOOLEAN DEFAULT true,
    phone TEXT,
    position TEXT,
    notes TEXT,
    -- 2FA 관련 컬럼
    totp_secret TEXT,
    backup_codes TEXT[],
    is_2fa_enabled BOOLEAN DEFAULT false,
    -- 보안 관련
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMPTZ,
    last_login TIMESTAMPTZ,
    -- 메타데이터
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 2.2. admins 테이블 (관리자 전용)
CREATE TABLE IF NOT EXISTS admins (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    employee_id TEXT UNIQUE,
    department TEXT DEFAULT 'IT팀',
    role TEXT DEFAULT 'admin' CHECK (role IN ('admin', 'superadmin')),
    password_hash TEXT NOT NULL,
    salt TEXT,
    is_active BOOLEAN DEFAULT true,
    phone TEXT,
    position TEXT,
    notes TEXT,
    -- 2FA 관련
    totp_secret TEXT,
    backup_codes TEXT[],
    is_2fa_enabled BOOLEAN DEFAULT false,
    -- 보안 관련
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMPTZ,
    last_login TIMESTAMPTZ,
    -- 메타데이터
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- ========================================
-- 3. 생산 관련 테이블
-- ========================================

-- 3.1. production_models 테이블 (생산 모델)
CREATE TABLE IF NOT EXISTS production_models (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    model_no TEXT UNIQUE NOT NULL,
    model_name TEXT NOT NULL,
    process TEXT NOT NULL,
    notes TEXT,
    -- 추가 필드
    specification TEXT,
    drawing_number TEXT,
    material TEXT,
    target_quantity INTEGER,
    cycle_time_minutes INTEGER,
    -- 상태 관리
    is_active BOOLEAN DEFAULT true,
    -- 메타데이터
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 3.2. inspectors 테이블 (검사자)
CREATE TABLE IF NOT EXISTS inspectors (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    employee_id TEXT UNIQUE,
    department TEXT DEFAULT '품질관리부',
    phone TEXT,
    position TEXT,
    certification_level TEXT, -- 자격 수준
    is_active BOOLEAN DEFAULT true,
    notes TEXT,
    -- 메타데이터
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- ========================================
-- 4. 검사 관련 테이블
-- ========================================

-- 4.1. defect_types 테이블 (불량 유형)
CREATE TABLE IF NOT EXISTS defect_types (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    severity_level TEXT DEFAULT 'medium' CHECK (severity_level IN ('low', 'medium', 'high', 'critical')),
    category TEXT, -- 분류 (치수, 외관, 기능 등)
    is_active BOOLEAN DEFAULT true,
    -- 메타데이터
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 4.2. inspection_data 테이블 (검사 실적)
CREATE TABLE IF NOT EXISTS inspection_data (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    -- 기본 정보
    inspection_date DATE NOT NULL,
    inspector_id UUID REFERENCES inspectors(id) ON DELETE SET NULL,
    model_id UUID REFERENCES production_models(id) ON DELETE SET NULL,
    
    -- 검사 결과
    result TEXT CHECK (result IN ('합격', '불합격')) NOT NULL,
    
    -- 수량 정보
    planned_quantity INTEGER,
    total_inspected INTEGER,
    defect_quantity INTEGER DEFAULT 0,
    pass_quantity INTEGER,
    
    -- 추가 정보
    lot_number TEXT,
    process TEXT,
    work_time_minutes INTEGER,
    shift TEXT, -- 근무조
    equipment_id TEXT, -- 설비 ID
    
    -- 메모 및 비고
    notes TEXT,
    
    -- 메타데이터
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 4.3. defects 테이블 (불량 상세 정보)
CREATE TABLE IF NOT EXISTS defects (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    inspection_id UUID REFERENCES inspection_data(id) ON DELETE CASCADE,
    defect_type_id UUID REFERENCES defect_types(id) ON DELETE CASCADE,
    defect_count INTEGER NOT NULL DEFAULT 1,
    location TEXT, -- 불량 발생 위치
    severity TEXT DEFAULT 'medium' CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    root_cause TEXT, -- 근본 원인
    corrective_action TEXT, -- 시정 조치
    action_status TEXT DEFAULT 'pending' CHECK (action_status IN ('pending', 'in_progress', 'completed')),
    notes TEXT,
    -- 첨부파일 경로 (향후 구현)
    photo_path TEXT,
    document_path TEXT,
    -- 메타데이터
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- ========================================
-- 5. 인덱스 생성 (성능 최적화)
-- ========================================

-- users 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_employee_id ON users(employee_id);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

-- admins 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_admins_email ON admins(email);
CREATE INDEX IF NOT EXISTS idx_admins_role ON admins(role);

-- production_models 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_production_models_model_no ON production_models(model_no);
CREATE INDEX IF NOT EXISTS idx_production_models_model_name ON production_models(model_name);
CREATE INDEX IF NOT EXISTS idx_production_models_process ON production_models(process);
CREATE INDEX IF NOT EXISTS idx_production_models_is_active ON production_models(is_active);

-- inspectors 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_inspectors_employee_id ON inspectors(employee_id);
CREATE INDEX IF NOT EXISTS idx_inspectors_is_active ON inspectors(is_active);

-- defect_types 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_defect_types_name ON defect_types(name);
CREATE INDEX IF NOT EXISTS idx_defect_types_category ON defect_types(category);

-- inspection_data 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_inspection_data_date ON inspection_data(inspection_date);
CREATE INDEX IF NOT EXISTS idx_inspection_data_inspector_id ON inspection_data(inspector_id);
CREATE INDEX IF NOT EXISTS idx_inspection_data_model_id ON inspection_data(model_id);
CREATE INDEX IF NOT EXISTS idx_inspection_data_result ON inspection_data(result);
CREATE INDEX IF NOT EXISTS idx_inspection_data_lot_number ON inspection_data(lot_number);
CREATE INDEX IF NOT EXISTS idx_inspection_data_process ON inspection_data(process);

-- defects 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_defects_inspection_id ON defects(inspection_id);
CREATE INDEX IF NOT EXISTS idx_defects_defect_type_id ON defects(defect_type_id);
CREATE INDEX IF NOT EXISTS idx_defects_severity ON defects(severity);

-- ========================================
-- 6. RLS (Row Level Security) 비활성화 (개발 환경용)
-- ========================================

ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE admins DISABLE ROW LEVEL SECURITY;
ALTER TABLE production_models DISABLE ROW LEVEL SECURITY;
ALTER TABLE inspectors DISABLE ROW LEVEL SECURITY;
ALTER TABLE defect_types DISABLE ROW LEVEL SECURITY;
ALTER TABLE inspection_data DISABLE ROW LEVEL SECURITY;
ALTER TABLE defects DISABLE ROW LEVEL SECURITY;

-- ========================================
-- 7. 기본 데이터 삽입
-- ========================================

-- 7.1. 기본 관리자 계정 (패스워드: admin123)
INSERT INTO admins (name, email, employee_id, role, password_hash, is_active) 
VALUES (
    '시스템 관리자', 
    'admin@company.com', 
    'A001', 
    'superadmin',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/yDWrYgWbZPbqY8j7W', -- admin123
    true
) ON CONFLICT (email) DO NOTHING;

-- 7.2. 기본 사용자 계정
INSERT INTO users (name, email, employee_id, department, role, password_hash, is_active) 
VALUES 
('검사자1', 'inspector1@company.com', 'I001', '품질관리부', 'inspector', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/yDWrYgWbZPbqY8j7W', true),
('검사자2', 'inspector2@company.com', 'I002', '품질관리부', 'inspector', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/yDWrYgWbZPbqY8j7W', true),
('사용자1', 'user1@company.com', 'U001', '생산관리부', 'user', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/yDWrYgWbZPbqY8j7W', true)
ON CONFLICT (email) DO NOTHING;

-- 7.3. 기본 검사자 정보
INSERT INTO inspectors (name, employee_id, department, position, certification_level) 
VALUES 
('김검사', 'I001', '품질관리부', '선임검사원', '고급'),
('이품질', 'I002', '품질관리부', '검사원', '중급'),
('박정밀', 'I003', '품질관리부', '수석검사원', '전문가')
ON CONFLICT (employee_id) DO NOTHING;

-- 7.4. 기본 생산 모델
INSERT INTO production_models (model_no, model_name, process, material, notes) 
VALUES 
('MODEL-001', 'PA1', 'CNC2_PQC', 'AL6061', '표준 생산 모델'),
('MODEL-002', 'PA2', 'OQC', 'STS304', '품질 검사 모델'),
('MODEL-003', 'PA3', 'CNC1_PQC', 'AL7075', '고급 생산 모델'),
('MODEL-004', 'B6', 'C1', 'AL6061', '기본 모델'),
('MODEL-005', 'B6M', 'C2', 'STS316', '개선된 모델')
ON CONFLICT (model_no) DO NOTHING;

-- 7.5. 기본 불량 유형
INSERT INTO defect_types (name, description, category, severity_level) 
VALUES 
('치수 불량', '제품의 치수가 규격을 벗어남', '치수', 'high'),
('표면 결함', '제품 표면의 긁힘, 찍힘 등의 결함', '외관', 'medium'),
('가공 불량', '가공 공정에서 발생한 불량', '가공', 'high'),
('재료 결함', '원자재의 결함으로 인한 불량', '재료', 'critical'),
('조립 불량', '조립 과정에서 발생한 불량', '조립', 'medium'),
('기타', '기타 불량 유형', '기타', 'low')
ON CONFLICT (name) DO NOTHING;

-- ========================================
-- 8. 샘플 검사 데이터 (최근 30일)
-- ========================================

INSERT INTO inspection_data (
    inspection_date, 
    inspector_id, 
    model_id, 
    result, 
    planned_quantity,
    total_inspected, 
    defect_quantity,
    pass_quantity,
    lot_number,
    process,
    notes
) 
SELECT 
    CURRENT_DATE - (random() * 30)::integer AS inspection_date,
    (SELECT id FROM inspectors ORDER BY random() LIMIT 1) AS inspector_id,
    (SELECT id FROM production_models ORDER BY random() LIMIT 1) AS model_id,
    CASE 
        WHEN random() < 0.85 THEN '합격'
        ELSE '불합격'
    END AS result,
    (50 + random() * 200)::integer AS planned_quantity,
    (40 + random() * 160)::integer AS total_inspected,
    CASE 
        WHEN random() < 0.85 THEN 0
        ELSE (1 + random() * 5)::integer
    END AS defect_quantity,
    NULL AS pass_quantity, -- 계산 필드
    'LOT-' || LPAD((random() * 9999)::integer::text, 4, '0') AS lot_number,
    (ARRAY['CNC1_PQC', 'CNC2_PQC', 'OQC', 'IQC', 'FQC'])[floor(random() * 5 + 1)] AS process,
    '샘플 검사 데이터' AS notes
FROM generate_series(1, 50); -- 50개의 샘플 데이터 생성

-- pass_quantity 계산 업데이트
UPDATE inspection_data 
SET pass_quantity = total_inspected - COALESCE(defect_quantity, 0)
WHERE pass_quantity IS NULL;

-- ========================================
-- 9. 검증 쿼리
-- ========================================

-- 테이블별 데이터 개수 확인
SELECT 
    'users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 
    'admins' as table_name, COUNT(*) as count FROM admins
UNION ALL
SELECT 
    'inspectors' as table_name, COUNT(*) as count FROM inspectors
UNION ALL
SELECT 
    'production_models' as table_name, COUNT(*) as count FROM production_models
UNION ALL
SELECT 
    'defect_types' as table_name, COUNT(*) as count FROM defect_types
UNION ALL
SELECT 
    'inspection_data' as table_name, COUNT(*) as count FROM inspection_data
UNION ALL
SELECT 
    'defects' as table_name, COUNT(*) as count FROM defects
ORDER BY table_name;

-- ========================================
-- 완료 메시지
-- ========================================

SELECT '🎉 CNC QC KPI 시스템 데이터베이스 스키마 통합 완료!' as status,
       '모든 테이블과 기본 데이터가 성공적으로 생성되었습니다.' as message; 