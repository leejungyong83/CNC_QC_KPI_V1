-- 실제 사용자의 비밀번호 해시를 SHA256으로 업데이트
-- 비밀번호: 01100110
-- SHA256 해시: 7b158f7df9bf300bcd68345e7e1f91df41d15bf7072323d6c78800e90c196548

UPDATE users 
SET password_hash = '7b158f7df9bf300bcd68345e7e1f91df41d15bf7072323d6c78800e90c196548'
WHERE email = 'diwjddyd83@gmail.com';

-- 다른 사용자들도 동일한 비밀번호로 설정 (테스트용)
UPDATE users 
SET password_hash = '7b158f7df9bf300bcd68345e7e1f91df41d15bf7072323d6c78800e90c196548'
WHERE email = 'zetooo1972@gmail.com';

UPDATE users 
SET password_hash = '7b158f7df9bf300bcd68345e7e1f91df41d15bf7072323d6c78800e90c196548'
WHERE email = 'jinuk.cho@gmail.com';

-- 업데이트 확인
SELECT email, name, role, password_hash FROM users; 