-- inspection_data 테이블에 shift 컬럼 추가
-- 교대조 정보를 저장하기 위한 컬럼

-- shift 컬럼이 없는 경우에만 추가
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'inspection_data' 
        AND column_name = 'shift'
    ) THEN
        ALTER TABLE inspection_data 
        ADD COLUMN shift VARCHAR(50);
        
        -- 컬럼 설명 추가
        COMMENT ON COLUMN inspection_data.shift IS '교대조 정보 (예: A조 주간, B조 야간)';
        
        RAISE NOTICE 'shift 컬럼이 inspection_data 테이블에 추가되었습니다.';
    ELSE
        RAISE NOTICE 'shift 컬럼이 이미 존재합니다.';
    END IF;
END $$;

-- 인덱스 추가 (성능 최적화)
CREATE INDEX IF NOT EXISTS idx_inspection_data_shift 
ON inspection_data(shift);

-- 교대조별 조회를 위한 복합 인덱스
CREATE INDEX IF NOT EXISTS idx_inspection_data_date_shift 
ON inspection_data(inspection_date, shift);

-- 시간 기준 교대조 조회를 위한 인덱스  
CREATE INDEX IF NOT EXISTS idx_inspection_data_created_shift 
ON inspection_data(created_at, shift);

-- 현재 데이터 확인
SELECT 
    COUNT(*) as total_records,
    COUNT(shift) as records_with_shift,
    COUNT(*) - COUNT(shift) as records_without_shift
FROM inspection_data;

COMMIT; 