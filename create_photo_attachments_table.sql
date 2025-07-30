-- ========================================
-- 사진 첨부 시스템을 위한 데이터베이스 스키마
-- 2025-07-30 추가
-- ========================================

-- 5. inspection_attachments 테이블 (검사 첨부 파일)
CREATE TABLE IF NOT EXISTS inspection_attachments (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    
    -- 검사 데이터 연결
    inspection_id UUID REFERENCES inspection_data(id) ON DELETE CASCADE,
    
    -- 파일 정보
    file_name TEXT NOT NULL,              -- 원본 파일명
    file_path TEXT NOT NULL,              -- 저장된 파일 경로
    file_size INTEGER,                    -- 파일 크기 (bytes)
    file_type TEXT NOT NULL,              -- MIME 타입 (image/jpeg, image/png 등)
    
    -- 사진 메타데이터
    photo_type TEXT DEFAULT 'inspection' CHECK (photo_type IN ('inspection', 'defect', 'equipment', 'process')),
    description TEXT,                     -- 사진 설명
    capture_location TEXT,                -- 촬영 위치 (공정단계, 부위 등)
    
    -- 이미지 속성
    width INTEGER,                        -- 이미지 가로 크기
    height INTEGER,                       -- 이미지 세로 크기
    is_thumbnail BOOLEAN DEFAULT false,   -- 썸네일 여부
    
    -- 업로드 정보
    uploaded_by UUID REFERENCES inspectors(id) ON DELETE SET NULL,
    upload_ip TEXT,                       -- 업로드 IP 주소
    upload_user_agent TEXT,               -- 업로드 브라우저 정보
    
    -- 상태 관리
    is_active BOOLEAN DEFAULT true,       -- 활성 상태
    is_public BOOLEAN DEFAULT false,      -- 공개 여부 (보고서 포함 등)
    
    -- 메타데이터
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 6. defect_attachments 테이블 (불량 관련 첨부 파일)
CREATE TABLE IF NOT EXISTS defect_attachments (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    
    -- 불량 데이터 연결
    defect_id UUID REFERENCES defects(id) ON DELETE CASCADE,
    
    -- 파일 정보
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER,
    file_type TEXT NOT NULL,
    
    -- 불량 사진 메타데이터
    defect_area TEXT,                     -- 불량 발생 부위
    defect_severity TEXT CHECK (defect_severity IN ('low', 'medium', 'high', 'critical')),
    before_after TEXT CHECK (before_after IN ('before', 'after', 'during')), -- 조치 전/후/중
    
    -- 분석 정보
    is_root_cause_photo BOOLEAN DEFAULT false,  -- 근본원인 분석용 사진
    analysis_notes TEXT,                         -- 분석 메모
    
    -- 업로드 정보
    uploaded_by UUID REFERENCES inspectors(id) ON DELETE SET NULL,
    
    -- 상태 관리
    is_active BOOLEAN DEFAULT true,
    
    -- 메타데이터
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- ========================================
-- 인덱스 생성 (성능 최적화)
-- ========================================

-- inspection_attachments 인덱스
CREATE INDEX IF NOT EXISTS idx_inspection_attachments_inspection_id ON inspection_attachments(inspection_id);
CREATE INDEX IF NOT EXISTS idx_inspection_attachments_photo_type ON inspection_attachments(photo_type);
CREATE INDEX IF NOT EXISTS idx_inspection_attachments_created_at ON inspection_attachments(created_at);
CREATE INDEX IF NOT EXISTS idx_inspection_attachments_active ON inspection_attachments(is_active);

-- defect_attachments 인덱스
CREATE INDEX IF NOT EXISTS idx_defect_attachments_defect_id ON defect_attachments(defect_id);
CREATE INDEX IF NOT EXISTS idx_defect_attachments_severity ON defect_attachments(defect_severity);
CREATE INDEX IF NOT EXISTS idx_defect_attachments_created_at ON defect_attachments(created_at);

-- ========================================
-- RLS (Row Level Security) 설정
-- ========================================

-- 개발 환경에서는 RLS 비활성화
ALTER TABLE inspection_attachments DISABLE ROW LEVEL SECURITY;
ALTER TABLE defect_attachments DISABLE ROW LEVEL SECURITY;

-- ========================================
-- 스토리지 버킷 생성 (Supabase Storage)
-- ========================================

-- 검사 사진용 버킷
-- 주의: 이 부분은 Supabase 대시보드에서 수동으로 생성해야 함
/*
버킷 이름: inspection-photos
- public: false (인증된 사용자만 접근)
- file_size_limit: 10MB
- allowed_mime_types: ['image/jpeg', 'image/png', 'image/webp']
*/

-- 불량 사진용 버킷
/*
버킷 이름: defect-photos  
- public: false
- file_size_limit: 10MB
- allowed_mime_types: ['image/jpeg', 'image/png', 'image/webp']
*/

-- ========================================
-- 샘플 데이터 및 테스트 쿼리
-- ========================================

-- 테이블 생성 확인
SELECT 
    'inspection_attachments 테이블 구조' as table_info,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'inspection_attachments' 
ORDER BY ordinal_position;

SELECT 
    'defect_attachments 테이블 구조' as table_info,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'defect_attachments' 
ORDER BY ordinal_position;

-- 기본 통계 확인
SELECT 
    '현재 첨부파일 통계' as info,
    (SELECT COUNT(*) FROM inspection_attachments) as inspection_photos,
    (SELECT COUNT(*) FROM defect_attachments) as defect_photos;

-- 완료 메시지
SELECT '✅ 사진 첨부 시스템 데이터베이스 스키마 생성 완료!' as status; 