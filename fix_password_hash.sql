-- password_hash를 앱에서 기대하는 값으로 수정

-- 1. admins 테이블의 password_hash 수정
UPDATE admins 
SET password_hash = 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3'
WHERE email = 'diwjddyd83@gmail.com';

-- 2. users 테이블의 password_hash도 수정 (있다면)
UPDATE users 
SET password_hash = 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3'
WHERE email = 'diwjddyd83@gmail.com';

-- 3. 확인 (password 컬럼 제외)
SELECT email, name, password_hash
FROM admins 
WHERE email = 'diwjddyd83@gmail.com'; 