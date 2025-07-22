-- production_models 테이블 생성 SQL (간단 버전)
-- notes 컬럼 없이 기본 컬럼만 사용

-- 1. 현재 테이블 구조 확인
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

-- 2. RLS (Row Level Security) 비활성화
ALTER TABLE production_models DISABLE ROW LEVEL SECURITY;

-- 3. 기존 데이터 확인
SELECT 
    '=== 현재 저장된 데이터 ===' as info,
    COUNT(*) as total_count 
FROM production_models;

SELECT '=== 기존 데이터 목록 ===' as info;
SELECT * FROM production_models ORDER BY created_at DESC;

-- 4. 기존 데이터 삭제
DELETE FROM production_models WHERE 1=1;

-- 5. 새로운 샘플 데이터 삽입 (기본 컬럼만 사용)
INSERT INTO production_models (model_no, model_name, process) VALUES
('MODEL-001', 'PA1', 'CNC2_PQC'),
('MODEL-002', 'PA2', 'OQC'),
('MODEL-003', 'PA3', 'CNC1_PQC'),
('MODEL-004', 'B6', 'C1'),
('MODEL-005', 'B6M', 'C2'),
('MODEL-006', 'B6S6', 'IQC'),
('MODEL-007', 'E1', 'FQC');

-- 6. 최종 결과 확인
SELECT 
    '=== 업데이트 완료! ===' as info,
    COUNT(*) as total_count 
FROM production_models;

SELECT '=== 새로운 데이터 목록 ===' as info;
SELECT * FROM production_models ORDER BY created_at DESC; 