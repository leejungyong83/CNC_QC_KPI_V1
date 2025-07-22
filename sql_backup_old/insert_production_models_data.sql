-- production_models 데이터 삽입 SQL
-- 테이블 구조가 이미 완성되어 있으므로 데이터만 삽입

-- 1. RLS (Row Level Security) 비활성화 (확실히 하기 위해)
ALTER TABLE production_models DISABLE ROW LEVEL SECURITY;

-- 2. 기존 데이터 확인
SELECT 
    '=== 현재 저장된 데이터 ===' as info,
    COUNT(*) as total_count 
FROM production_models;

SELECT '=== 기존 데이터 목록 ===' as info;
SELECT * FROM production_models ORDER BY created_at DESC;

-- 3. 기존 데이터 삭제 (깔끔한 시작을 위해)
DELETE FROM production_models WHERE 1=1;

-- 4. 새로운 샘플 데이터 삽입
INSERT INTO production_models (model_no, model_name, process, notes) VALUES
('MODEL-001', 'PA1', 'CNC2_PQC', '표준 생산 모델'),
('MODEL-002', 'PA2', 'OQC', '품질 검사 모델'),
('MODEL-003', 'PA3', 'CNC1_PQC', '고급 생산 모델'),
('MODEL-004', 'B6', 'C1', '기본 모델'),
('MODEL-005', 'B6M', 'C2', '개선된 모델'),
('MODEL-006', 'B6S6', 'IQC', '특수 모델'),
('MODEL-007', 'E1', 'FQC', '최종 검사 모델');

-- 5. 최종 결과 확인
SELECT 
    '=== 데이터 삽입 완료! ===' as info,
    COUNT(*) as total_count 
FROM production_models;

SELECT '=== 새로운 데이터 목록 ===' as info;
SELECT 
    model_no,
    model_name,
    process,
    notes,
    created_at
FROM production_models 
ORDER BY created_at DESC;

-- 6. 성공 메시지
SELECT '🎉 production_models 테이블 설정 완료!' as success_message; 