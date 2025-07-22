-- production_models 테이블 생성 SQL (최종 수정 버전)
-- notes 컬럼 문제 해결

-- 1. 먼저 현재 테이블 구조 확인
SELECT 
    '=== 현재 테이블 구조 ===' as info;
    
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'production_models' 
ORDER BY ordinal_position;

-- 2. notes 컬럼 추가 (없는 경우만)
ALTER TABLE production_models 
ADD COLUMN IF NOT EXISTS notes TEXT;

-- 3. updated_at 컬럼 추가 (없는 경우만)  
ALTER TABLE production_models 
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT now();

-- 4. 인덱스 생성 (성능 향상) - 이미 있다면 무시
CREATE INDEX IF NOT EXISTS idx_production_models_model_no ON production_models(model_no);
CREATE INDEX IF NOT EXISTS idx_production_models_model_name ON production_models(model_name);
CREATE INDEX IF NOT EXISTS idx_production_models_process ON production_models(process);
CREATE INDEX IF NOT EXISTS idx_production_models_created_at ON production_models(created_at);

-- 5. RLS (Row Level Security) 비활성화 (개발 환경용)
ALTER TABLE production_models DISABLE ROW LEVEL SECURITY;

-- 6. 기존 데이터 확인
SELECT 
    '=== 현재 저장된 데이터 ===' as info,
    COUNT(*) as total_count 
FROM production_models;

SELECT '=== 기존 데이터 목록 ===' as info;
SELECT * FROM production_models ORDER BY created_at DESC;

-- 7. 기존 데이터 삭제 (TRUNCATE 대신 DELETE 사용)
DELETE FROM production_models WHERE 1=1;

-- 8. 새로운 샘플 데이터 삽입 (notes 컬럼 포함)
INSERT INTO production_models (model_no, model_name, process, notes) VALUES
('MODEL-001', 'PA1', 'CNC2_PQC', '표준 생산 모델'),
('MODEL-002', 'PA2', 'OQC', '품질 검사 모델'),
('MODEL-003', 'PA3', 'CNC1_PQC', '고급 생산 모델'),
('MODEL-004', 'B6', 'C1', '기본 모델'),
('MODEL-005', 'B6M', 'C2', '개선된 모델'),
('MODEL-006', 'B6S6', 'IQC', '특수 모델'),
('MODEL-007', 'E1', 'FQC', '최종 검사 모델');

-- 9. 최종 결과 확인
SELECT 
    '=== 업데이트 완료! ===' as info,
    COUNT(*) as total_count 
FROM production_models;

SELECT '=== 새로운 데이터 목록 ===' as info;
SELECT * FROM production_models ORDER BY created_at DESC;

-- 10. 최종 테이블 구조 확인
SELECT 
    '=== 최종 테이블 구조 ===' as info;
    
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'production_models' 
ORDER BY ordinal_position; 