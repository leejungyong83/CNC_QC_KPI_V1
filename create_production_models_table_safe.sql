-- production_models 테이블 생성 SQL (안전한 버전)
-- 기존 데이터를 보존하면서 테이블 구조만 생성/수정

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
    '현재 저장된 데이터:' as status,
    COUNT(*) as total_count 
FROM production_models;

-- 5. 현재 데이터 표시
SELECT * FROM production_models ORDER BY created_at DESC;

-- 6. 추가 샘플 데이터 삽입 (중복 방지)
-- 기존 데이터와 겹치지 않는 새로운 샘플 데이터만 추가

INSERT INTO production_models (model_no, model_name, process, notes) 
SELECT * FROM (VALUES
    ('MODEL-003', 'PA3', 'CNC1_PQC', '고급 생산 모델'),
    ('MODEL-004', 'B6', 'C1', '기본 모델'),
    ('MODEL-005', 'B6M', 'C2', '개선된 모델'),
    ('MODEL-006', 'B6S6', 'IQC', '특수 모델'),
    ('MODEL-007', 'E1', 'FQC', '최종 검사 모델')
) AS new_data(model_no, model_name, process, notes)
WHERE NOT EXISTS (
    SELECT 1 FROM production_models p 
    WHERE p.model_no = new_data.model_no
);

-- 7. 최종 결과 확인
SELECT 
    '업데이트 완료!' as status,
    COUNT(*) as total_count 
FROM production_models;

SELECT * FROM production_models ORDER BY created_at DESC; 