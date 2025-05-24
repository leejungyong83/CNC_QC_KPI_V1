# 🔧 Supabase 설정 완전 가이드

## 📋 1단계: Supabase 대시보드 접속

1. **브라우저에서 접속**: https://app.supabase.com
2. **로그인** 또는 **회원가입**
3. **프로젝트 선택** (없으면 새로 생성)

## 🔑 2단계: API 설정 정보 찾기

1. **프로젝트 대시보드**에서 왼쪽 메뉴 확인
2. **⚙️ Settings** 클릭
3. **🔌 API** 탭 선택
4. 다음 정보 복사:

### **필요한 정보**
```
📍 Project URL: https://your-project-id.supabase.co
🔑 anon key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## ⚠️ 3단계: 올바른 복사 방법

### **URL 복사**
- **Project URL** 전체를 복사 (https://로 시작)
- 끝에 슬래시(/) 있으면 제거

### **API Key 복사**
- **anon** 키를 복사 (public key)
- **service_role** 키는 사용하지 마세요! (보안 위험)
- 전체 키를 정확히 복사 (매우 긴 문자열)

## 🚀 4단계: 앱에서 설정

1. **CNC 앱** → **Supabase 설정** 메뉴
2. **URL과 Key 입력**
3. **"설정 저장 (영구 보존)" 버튼 클릭**
4. **연결 테스트**로 확인

## 🔍 5단계: 문제 해결

### **자주 발생하는 문제**
- **Invalid API Key**: 키를 잘못 복사함
- **URL 형식 오류**: https:// 누락
- **빈 공간**: 복사 시 앞뒤 공백 포함
- **잘못된 키**: service_role 키 사용

### **해결 방법**
1. **키를 다시 복사**: Supabase에서 anon key 재복사
2. **공백 제거**: 앞뒤 공백 확인
3. **새 프로젝트**: 필요시 새 Supabase 프로젝트 생성 