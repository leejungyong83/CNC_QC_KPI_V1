-- admins 테이블에 password_hash 컬럼 추가 후 실행할 SQL

-- 1. 기존 관리자들에게 기본 비밀번호 해시 설정
-- '01100110'의 SHA-256 해시: a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3
UPDATE admins 
SET password_hash = 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3'
WHERE password_hash IS NULL OR password_hash = '';

-- 2. 필요한 다른 컬럼들도 추가 (없는 경우)
ALTER TABLE admins ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;
ALTER TABLE admins ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
ALTER TABLE admins ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
ALTER TABLE admins ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMP WITH TIME ZONE;

-- 3. 기본값 설정
UPDATE admins 
SET is_active = true,
    created_at = COALESCE(created_at, NOW()),
    updated_at = NOW()
WHERE is_active IS NULL OR created_at IS NULL;

-- 4. 결과 확인
SELECT 
    id, 
    email, 
    name, 
    role,
    CASE 
        WHEN password_hash IS NOT NULL AND password_hash != '' THEN '비밀번호 설정됨' 
        ELSE '비밀번호 없음' 
    END as password_status,
    is_active,
    created_at
FROM admins 
ORDER BY created_at DESC; 