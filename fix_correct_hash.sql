-- 올바른 SHA-256 해시로 업데이트
-- 입력 비밀번호 '01100110'의 정확한 SHA-256 해시값 사용

UPDATE admins 
SET password_hash = 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3'
WHERE email = 'diwjddyd83@gmail.com';

-- 확인
SELECT email, name, password_hash 
FROM admins 
WHERE email = 'diwjddyd83@gmail.com'; 