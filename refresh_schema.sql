-- Supabase 스키마 새로고침 및 inspection_data 테이블 확인
-- 2025-07-23

-- 테이블 존재 확인
SELECT table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'inspection_data' 
ORDER BY ordinal_position;

-- updated_at 컬럼이 없다면 추가 (안전하게)
ALTER TABLE inspection_data 
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT now();

-- 트리거 생성 (updated_at 자동 업데이트)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 트리거 적용
DROP TRIGGER IF EXISTS update_inspection_data_updated_at ON inspection_data;
CREATE TRIGGER update_inspection_data_updated_at
    BEFORE UPDATE ON inspection_data
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 다른 테이블들도 동일하게 처리
ALTER TABLE defects 
ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT now();

ALTER TABLE defects 
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT now();

-- 스키마 확인 완료 메시지
SELECT 'Schema refresh completed' as status; 