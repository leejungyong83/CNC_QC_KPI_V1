-- 최종 디버깅: 정확한 데이터 상태 확인

-- 1. admins 테이블 컬럼 확인
\d admins

-- 2. admins 테이블의 모든 컬럼 확인
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'admins';

-- 3. diwjddyd83@gmail.com 데이터 확인 (모든 컬럼)
SELECT * FROM admins WHERE email = 'diwjddyd83@gmail.com';

-- 4. users 테이블에도 있는지 확인
SELECT * FROM users WHERE email = 'diwjddyd83@gmail.com';

-- 5. admins 테이블에 password 컬럼이 있는지 확인
SELECT EXISTS (
    SELECT 1 
    FROM information_schema.columns 
    WHERE table_name = 'admins' 
    AND column_name = 'password'
) as has_password_column;

-- 6. admins 테이블에 password_hash 컬럼이 있는지 확인
SELECT EXISTS (
    SELECT 1 
    FROM information_schema.columns 
    WHERE table_name = 'admins' 
    AND column_name = 'password_hash'
) as has_password_hash_column; 