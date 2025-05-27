-- 샘플 검사실적 데이터 삽입 스크립트
-- 이 스크립트는 Supabase SQL Editor에서 실행하세요

-- 1. 먼저 기존 검사실적 데이터 확인
SELECT COUNT(*) as current_inspection_count FROM inspection_data;

-- 2. 검사자와 생산모델 데이터 확인
SELECT 'inspectors' as table_name, COUNT(*) as count FROM inspectors
UNION ALL
SELECT 'production_models' as table_name, COUNT(*) as count FROM production_models;

-- 3. 샘플 검사실적 데이터 삽입
-- 주의: 실제 존재하는 inspector_id와 model_id를 사용해야 합니다

-- 검사자 ID와 모델 ID 조회 (참고용)
SELECT 'Available Inspectors:' as info;
SELECT id, name, employee_id FROM inspectors LIMIT 5;

SELECT 'Available Models:' as info;
SELECT id, model_name, model_no FROM production_models LIMIT 5;

-- 실제 검사실적 데이터 삽입
-- 아래 UUID들은 실제 데이터베이스의 ID로 교체해야 합니다
INSERT INTO inspection_data (inspection_date, inspector_id, model_id, result, quantity, notes) VALUES
-- 최근 30일간의 검사실적 데이터
('2025-01-15', (SELECT id FROM inspectors LIMIT 1), (SELECT id FROM production_models WHERE model_name = 'PA1' LIMIT 1), '합격', 150, '정상 검사 완료'),
('2025-01-16', (SELECT id FROM inspectors LIMIT 1), (SELECT id FROM production_models WHERE model_name = 'PA2' LIMIT 1), '합격', 120, '품질 양호'),
('2025-01-17', (SELECT id FROM inspectors OFFSET 1 LIMIT 1), (SELECT id FROM production_models WHERE model_name = 'PA1' LIMIT 1), '불합격', 80, '치수 불량 발견'),
('2025-01-18', (SELECT id FROM inspectors LIMIT 1), (SELECT id FROM production_models WHERE model_name = 'PA2' LIMIT 1), '합격', 200, '대량 검사 완료'),
('2025-01-19', (SELECT id FROM inspectors OFFSET 1 LIMIT 1), (SELECT id FROM production_models WHERE model_name = 'PA1' LIMIT 1), '합격', 175, '정상'),
('2025-01-20', (SELECT id FROM inspectors LIMIT 1), (SELECT id FROM production_models WHERE model_name = 'PA2' LIMIT 1), '합격', 160, '품질 우수'),
('2025-01-21', (SELECT id FROM inspectors OFFSET 1 LIMIT 1), (SELECT id FROM production_models WHERE model_name = 'PA1' LIMIT 1), '합격', 140, '정상 검사'),
('2025-01-22', (SELECT id FROM inspectors LIMIT 1), (SELECT id FROM production_models WHERE model_name = 'PA2' LIMIT 1), '불합격', 90, '표면 결함'),
('2025-01-23', (SELECT id FROM inspectors OFFSET 1 LIMIT 1), (SELECT id FROM production_models WHERE model_name = 'PA1' LIMIT 1), '합격', 185, '품질 양호'),
('2025-01-24', (SELECT id FROM inspectors LIMIT 1), (SELECT id FROM production_models WHERE model_name = 'PA2' LIMIT 1), '합격', 170, '정상 완료'),
('2025-01-25', (SELECT id FROM inspectors OFFSET 1 LIMIT 1), (SELECT id FROM production_models WHERE model_name = 'PA1' LIMIT 1), '합격', 155, '검사 완료'),
('2025-01-26', (SELECT id FROM inspectors LIMIT 1), (SELECT id FROM production_models WHERE model_name = 'PA2' LIMIT 1), '합격', 190, '우수 품질'),
('2025-01-27', (SELECT id FROM inspectors OFFSET 1 LIMIT 1), (SELECT id FROM production_models WHERE model_name = 'PA1' LIMIT 1), '합격', 165, '정상'),
('2025-01-28', (SELECT id FROM inspectors LIMIT 1), (SELECT id FROM production_models WHERE model_name = 'PA2' LIMIT 1), '합격', 145, '품질 양호'),
('2025-01-29', (SELECT id FROM inspectors OFFSET 1 LIMIT 1), (SELECT id FROM production_models WHERE model_name = 'PA1' LIMIT 1), '불합격', 75, '가공 불량'),
('2025-01-30', (SELECT id FROM inspectors LIMIT 1), (SELECT id FROM production_models WHERE model_name = 'PA2' LIMIT 1), '합격', 180, '정상 검사'),
('2025-01-31', (SELECT id FROM inspectors OFFSET 1 LIMIT 1), (SELECT id FROM production_models WHERE model_name = 'PA1' LIMIT 1), '합격', 195, '품질 우수'),
('2025-02-01', (SELECT id FROM inspectors LIMIT 1), (SELECT id FROM production_models WHERE model_name = 'PA2' LIMIT 1), '합격', 160, '정상'),
('2025-02-02', (SELECT id FROM inspectors OFFSET 1 LIMIT 1), (SELECT id FROM production_models WHERE model_name = 'PA1' LIMIT 1), '합격', 175, '검사 완료'),
('2025-02-03', (SELECT id FROM inspectors LIMIT 1), (SELECT id FROM production_models WHERE model_name = 'PA2' LIMIT 1), '합격', 150, '품질 양호'),
('2025-02-04', (SELECT id FROM inspectors OFFSET 1 LIMIT 1), (SELECT id FROM production_models WHERE model_name = 'PA1' LIMIT 1), '합격', 185, '정상 완료'),
('2025-02-05', (SELECT id FROM inspectors LIMIT 1), (SELECT id FROM production_models WHERE model_name = 'PA2' LIMIT 1), '불합격', 85, '재료 결함'),
('2025-02-06', (SELECT id FROM inspectors OFFSET 1 LIMIT 1), (SELECT id FROM production_models WHERE model_name = 'PA1' LIMIT 1), '합격', 170, '품질 우수'),
('2025-02-07', (SELECT id FROM inspectors LIMIT 1), (SELECT id FROM production_models WHERE model_name = 'PA2' LIMIT 1), '합격', 165, '정상'),
('2025-02-08', (SELECT id FROM inspectors OFFSET 1 LIMIT 1), (SELECT id FROM production_models WHERE model_name = 'PA1' LIMIT 1), '합격', 190, '검사 완료'),
('2025-02-09', (SELECT id FROM inspectors LIMIT 1), (SELECT id FROM production_models WHERE model_name = 'PA2' LIMIT 1), '합격', 155, '품질 양호'),
('2025-02-10', (SELECT id FROM inspectors OFFSET 1 LIMIT 1), (SELECT id FROM production_models WHERE model_name = 'PA1' LIMIT 1), '합격', 180, '정상 완료'),
('2025-02-11', (SELECT id FROM inspectors LIMIT 1), (SELECT id FROM production_models WHERE model_name = 'PA2' LIMIT 1), '합격', 175, '우수 품질'),
('2025-02-12', (SELECT id FROM inspectors OFFSET 1 LIMIT 1), (SELECT id FROM production_models WHERE model_name = 'PA1' LIMIT 1), '합격', 160, '정상'),
('2025-02-13', (SELECT id FROM inspectors LIMIT 1), (SELECT id FROM production_models WHERE model_name = 'PA2' LIMIT 1), '합격', 195, '검사 완료');

-- 4. 삽입된 데이터 확인
SELECT COUNT(*) as total_inspections FROM inspection_data;

-- 5. 최근 검사실적 조회 (JOIN 포함)
SELECT 
    i.inspection_date,
    insp.name as inspector_name,
    pm.model_name,
    i.result,
    i.quantity,
    i.notes
FROM inspection_data i
LEFT JOIN inspectors insp ON i.inspector_id = insp.id
LEFT JOIN production_models pm ON i.model_id = pm.id
ORDER BY i.inspection_date DESC
LIMIT 10;

-- 6. 통계 조회
SELECT 
    result,
    COUNT(*) as count,
    SUM(quantity) as total_quantity,
    ROUND(AVG(quantity), 1) as avg_quantity
FROM inspection_data 
GROUP BY result;

-- 7. 검사원별 통계
SELECT 
    insp.name as inspector_name,
    COUNT(*) as inspection_count,
    SUM(i.quantity) as total_quantity,
    ROUND(AVG(i.quantity), 1) as avg_quantity,
    ROUND(
        (COUNT(CASE WHEN i.result = '합격' THEN 1 END) * 100.0 / COUNT(*)), 1
    ) as pass_rate_percent
FROM inspection_data i
LEFT JOIN inspectors insp ON i.inspector_id = insp.id
GROUP BY insp.name
ORDER BY inspection_count DESC;

-- 8. 모델별 통계
SELECT 
    pm.model_name,
    COUNT(*) as inspection_count,
    SUM(i.quantity) as total_quantity,
    ROUND(AVG(i.quantity), 1) as avg_quantity,
    ROUND(
        (COUNT(CASE WHEN i.result = '합격' THEN 1 END) * 100.0 / COUNT(*)), 1
    ) as pass_rate_percent
FROM inspection_data i
LEFT JOIN production_models pm ON i.model_id = pm.id
GROUP BY pm.model_name
ORDER BY inspection_count DESC; 