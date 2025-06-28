-- inspection_data 테이블 구조 개선 SQL
-- 사용자 요청사항에 맞게 필드 추가

-- 1. 현재 테이블 구조 확인
SELECT 
    '=== 현재 inspection_data 테이블 구조 ===' as info;
    
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'inspection_data' 
ORDER BY ordinal_position;

-- 2. 필요한 컬럼들 추가
ALTER TABLE inspection_data 
ADD COLUMN IF NOT EXISTS lot_number TEXT;

ALTER TABLE inspection_data 
ADD COLUMN IF NOT EXISTS process TEXT;

ALTER TABLE inspection_data 
ADD COLUMN IF NOT EXISTS work_time_minutes INTEGER;

ALTER TABLE inspection_data 
ADD COLUMN IF NOT EXISTS planned_quantity INTEGER;

ALTER TABLE inspection_data 
ADD COLUMN IF NOT EXISTS total_inspected INTEGER;

ALTER TABLE inspection_data 
ADD COLUMN IF NOT EXISTS defect_quantity INTEGER DEFAULT 0;

-- 3. 기존 quantity 필드를 total_inspected로 통일하기 위한 데이터 마이그레이션
UPDATE inspection_data 
SET total_inspected = quantity 
WHERE total_inspected IS NULL AND quantity IS NOT NULL;

-- 4. 인덱스 추가 (성능 향상)
CREATE INDEX IF NOT EXISTS idx_inspection_data_lot_number ON inspection_data(lot_number);
CREATE INDEX IF NOT EXISTS idx_inspection_data_process ON inspection_data(process);
CREATE INDEX IF NOT EXISTS idx_inspection_data_inspection_date ON inspection_data(inspection_date);

-- 5. 수정된 테이블 구조 확인
SELECT 
    '=== 수정된 inspection_data 테이블 구조 ===' as info;
    
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'inspection_data' 
ORDER BY ordinal_position;

-- 6. 현재 데이터 확인
SELECT 
    '=== 현재 저장된 데이터 ===' as info,
    COUNT(*) as total_count 
FROM inspection_data;

SELECT * FROM inspection_data ORDER BY created_at DESC LIMIT 5; 