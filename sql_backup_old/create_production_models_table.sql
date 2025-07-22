-- production_models 테이블 생성 SQL
-- Supabase SQL Editor에서 이 코드를 실행하세요

-- 1. 기존 테이블이 있다면 삭제 (주의: 데이터도 같이 삭제됩니다)
-- DROP TABLE IF EXISTS production_models;

-- 2. production_models 테이블 생성
CREATE TABLE IF NOT EXISTS production_models (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    model_no TEXT UNIQUE NOT NULL,
    model_name TEXT NOT NULL,
    process TEXT NOT NULL,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 3. 인덱스 생성 (성능 향상)
CREATE INDEX IF NOT EXISTS idx_production_models_model_no ON production_models(model_no);
CREATE INDEX IF NOT EXISTS idx_production_models_model_name ON production_models(model_name);
CREATE INDEX IF NOT EXISTS idx_production_models_process ON production_models(process);
CREATE INDEX IF NOT EXISTS idx_production_models_created_at ON production_models(created_at);

-- 4. RLS (Row Level Security) 비활성화 (개발 환경용)
ALTER TABLE production_models DISABLE ROW LEVEL SECURITY;

-- 5. 샘플 데이터 삽입 (기존 데이터 클리어 후)
TRUNCATE TABLE production_models;

INSERT INTO production_models (model_no, model_name, process, notes) VALUES
('MODEL-001', 'PA1', 'CNC2_PQC', '표준 생산 모델'),
('MODEL-002', 'PA2', 'OQC', '품질 검사 모델'),
('MODEL-003', 'PA3', 'CNC1_PQC', '고급 생산 모델'),
('MODEL-004', 'B6', 'C1', '기본 모델'),
('MODEL-005', 'B6M', 'C2', '개선된 모델'),
('MODEL-006', 'B6S6', 'IQC', '특수 모델'),
('MODEL-007', 'E1', 'FQC', '최종 검사 모델');

-- 6. 테이블 권한 설정 (필요시)
-- GRANT ALL ON production_models TO authenticated;
-- GRANT SELECT ON production_models TO anon;

-- 7. 확인 쿼리
SELECT * FROM production_models ORDER BY created_at DESC; 