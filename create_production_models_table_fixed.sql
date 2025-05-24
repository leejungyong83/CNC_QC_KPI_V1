-- production_models 테이블 생성 SQL (외래키 제약조건 해결 버전)
-- 기존 데이터 및 참조 관계를 고려한 안전한 처리

-- 1. production_models 테이블 생성 (이미 있다면 무시)
CREATE TABLE IF NOT EXISTS production_models (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    model_no TEXT UNIQUE NOT NULL,
    model_name TEXT NOT NULL,
    process TEXT NOT NULL,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 2. 인덱스 생성 (성능 향상) - 이미 있다면 무시
CREATE INDEX IF NOT EXISTS idx_production_models_model_no ON production_models(model_no);
CREATE INDEX IF NOT EXISTS idx_production_models_model_name ON production_models(model_name);
CREATE INDEX IF NOT EXISTS idx_production_models_process ON production_models(process);
CREATE INDEX IF NOT EXISTS idx_production_models_created_at ON production_models(created_at);

-- 3. RLS (Row Level Security) 비활성화 (개발 환경용)
ALTER TABLE production_models DISABLE ROW LEVEL SECURITY;

-- 4. 기존 데이터 확인
SELECT 
    '=== 현재 저장된 데이터 ===' as info,
    COUNT(*) as total_count 
FROM production_models;

-- 5. 현재 데이터 표시
SELECT '=== 기존 데이터 목록 ===' as info;
SELECT * FROM production_models ORDER BY created_at DESC;

-- 6. 기존 데이터 삭제 (TRUNCATE 대신 DELETE 사용)
-- 외래키 제약조건이 있어도 안전하게 처리
DELETE FROM production_models WHERE 1=1;

-- 7. 새로운 샘플 데이터 삽입
INSERT INTO production_models (model_no, model_name, process, notes) VALUES
('MODEL-001', 'PA1', 'CNC2_PQC', '표준 생산 모델'),
('MODEL-002', 'PA2', 'OQC', '품질 검사 모델'),
('MODEL-003', 'PA3', 'CNC1_PQC', '고급 생산 모델'),
('MODEL-004', 'B6', 'C1', '기본 모델'),
('MODEL-005', 'B6M', 'C2', '개선된 모델'),
('MODEL-006', 'B6S6', 'IQC', '특수 모델'),
('MODEL-007', 'E1', 'FQC', '최종 검사 모델');

-- 8. 최종 결과 확인
SELECT 
    '=== 업데이트 완료! ===' as info,
    COUNT(*) as total_count 
FROM production_models;

SELECT '=== 새로운 데이터 목록 ===' as info;
SELECT * FROM production_models ORDER BY created_at DESC;

-- 9. 테이블 정보 확인
SELECT 
    '=== 테이블 구조 정보 ===' as info;
    
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'production_models' 
ORDER BY ordinal_position; 