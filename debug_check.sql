-- 디버깅용 체크리스트 SQL

-- 1. admins 테이블이 존재하는지 확인
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('users', 'admins');

-- 2. admins 테이블 구조 확인
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'admins' 
AND table_schema = 'public'
ORDER BY ordinal_position;

-- 3. users 테이블 구조 확인  
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'users' 
AND table_schema = 'public'
ORDER BY ordinal_position;

-- 4. admins 테이블 데이터 확인
SELECT * FROM admins;

-- 5. users 테이블에서 특정 이메일 확인
SELECT * FROM users WHERE email = 'diwjddyd83@gmail.com';

-- 6. admins 테이블에서 특정 이메일 확인 (테이블이 있다면)
SELECT * FROM admins WHERE email = 'diwjddyd83@gmail.com'; 