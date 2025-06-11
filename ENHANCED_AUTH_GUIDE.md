# 🔐 CNC KPI 앱 - 강화된 인증 시스템 가이드

## 📋 개요

CNC KPI 앱에 강화된 인증 시스템을 구현하여 보안을 대폭 향상시켰습니다. 이 가이드는 새로운 보안 기능들의 구현 방법과 사용법을 설명합니다.

## 🔒 새로운 보안 기능

### 1. 강화된 비밀번호 정책
- **최소 8자 이상**
- **대문자, 소문자, 숫자, 특수문자 포함**
- **PBKDF2 해시 알고리즘 사용**
- **Salt 값을 이용한 안전한 저장**

### 2. 로그인 보안 강화
- **로그인 시도 제한**: 5회 실패 시 계정 잠금
- **계정 잠금**: 15분간 로그인 차단
- **세션 타임아웃**: 1시간 후 자동 로그아웃
- **안전한 세션 토큰**: HMAC 기반 토큰 검증

### 3. 2단계 인증 (2FA)
- **TOTP 기반**: Google Authenticator, Microsoft Authenticator 지원
- **QR 코드**: 간편한 설정
- **백업 코드**: 10개의 일회용 백업 코드 제공
- **시간 동기화**: 30초 허용 오차

### 4. 역할 기반 접근 제어 (RBAC)
- **user**: 기본 사용자 (검사 데이터 입력/조회)
- **inspector**: 검사원 (검사 관리)
- **manager**: 매니저 (인력 관리)
- **admin**: 관리자 (시스템 관리)
- **superadmin**: 최고 관리자 (모든 권한)

## 🚀 설치 및 설정

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

새로 추가된 라이브러리:
- `pyotp>=2.8.0`: TOTP 인증
- `qrcode[pil]>=7.4.0`: QR 코드 생성
- `cryptography>=41.0.0`: 암호화
- `bcrypt>=4.0.0`: 비밀번호 해시

### 2. 데이터베이스 스키마 업데이트

기존 `users` 테이블에 보안 관련 컬럼 추가:

```sql
-- 비밀번호 보안 강화
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS salt TEXT;

-- 2FA 관련 컬럼
ALTER TABLE users ADD COLUMN IF NOT EXISTS totp_secret TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS backup_codes TEXT[];
ALTER TABLE users ADD COLUMN IF NOT EXISTS two_factor_enabled BOOLEAN DEFAULT FALSE;

-- 로그인 보안
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMPTZ;
ALTER TABLE users ADD COLUMN IF NOT EXISTS login_attempts INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS locked_until TIMESTAMPTZ;

-- 세션 관리
ALTER TABLE users ADD COLUMN IF NOT EXISTS session_token TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS session_expires_at TIMESTAMPTZ;
```

### 3. 앱 실행

강화된 인증 시스템이 적용된 앱 실행:

```bash
streamlit run app_enhanced_auth.py
```

## 👤 사용자 가이드

### 1. 로그인

#### 기본 로그인
1. 이메일과 비밀번호 입력
2. "로그인" 버튼 클릭
3. 2FA가 활성화된 경우 인증 코드 입력

#### 테스트 계정
```
관리자: admin@company.com / admin123
사용자: user@company.com / user123
검사원: inspector@company.com / inspector123
```

### 2. 2단계 인증 설정

#### 2FA 활성화
1. 로그인 후 사이드바에서 "2단계 인증 설정" 클릭
2. "2FA 설정 시작" 버튼 클릭
3. 단계별 안내에 따라 설정:
   - **1단계**: 인증 앱 설치 (Google Authenticator 등)
   - **2단계**: QR 코드 스캔 또는 수동 키 입력
   - **3단계**: 인증 코드로 설정 확인
4. 백업 코드 안전한 곳에 저장

#### 2FA 로그인
1. 일반 로그인 완료 후
2. 인증 앱에서 6자리 코드 입력
3. 또는 8자리 백업 코드 사용

### 3. 보안 설정

#### 비밀번호 변경
1. "보안 설정" 메뉴 접근
2. "비밀번호 변경" 섹션 확장
3. 현재 비밀번호와 새 비밀번호 입력
4. 비밀번호 정책 준수 확인

#### 세션 관리
- 현재 세션 정보 확인
- 모든 세션 강제 종료 가능

## 🔧 개발자 가이드

### 1. 인증 시스템 구조

```
utils/
├── auth_system.py          # 기본 인증 시스템
├── two_factor_auth.py      # 2FA 시스템
└── supabase_client.py      # 데이터베이스 클라이언트

app_enhanced_auth.py        # 강화된 인증이 적용된 메인 앱
```

### 2. 주요 클래스

#### AuthenticationSystem
```python
from utils.auth_system import AuthenticationSystem

auth = AuthenticationSystem(supabase_client)

# 사용자 인증
success, message, user_data = auth.authenticate_user(email, password)

# 현재 사용자 확인
current_user = auth.get_current_user()

# 권한 확인
has_permission = auth.require_role(['admin', 'superadmin'])
```

#### TwoFactorAuth
```python
from utils.two_factor_auth import TwoFactorAuth

tfa = TwoFactorAuth(supabase_client)

# 2FA 설정
tfa.show_2fa_setup(user_email)

# 2FA 인증
is_verified = tfa.require_2fa_verification(user_email)
```

### 3. 권한 시스템 확장

새로운 역할 추가:

```python
def get_menu_items_by_role(user_role):
    if user_role == 'new_role':
        return {
            "카테고리": ["메뉴1", "메뉴2"]
        }
```

권한 확인 로직 수정:

```python
def has_permission(user_role, menu_item):
    if menu_item == "새_메뉴" and user_role in ['new_role']:
        return True
    return False
```

## 🛡️ 보안 모범 사례

### 1. 비밀번호 정책
- 정기적인 비밀번호 변경 권장
- 사전 단어 사용 금지
- 개인정보 포함 금지

### 2. 2FA 사용
- 모든 관리자 계정에 2FA 필수 적용
- 백업 코드 안전한 곳에 보관
- 정기적인 백업 코드 재생성

### 3. 세션 관리
- 공용 컴퓨터 사용 후 로그아웃
- 장시간 미사용 시 자동 로그아웃
- 의심스러운 활동 시 세션 종료

### 4. 계정 관리
- 불필요한 계정 정기 삭제
- 역할별 최소 권한 원칙
- 정기적인 권한 검토

## 🔍 문제 해결

### 1. 로그인 문제

#### 계정 잠금
- **문제**: 5회 로그인 실패로 계정 잠금
- **해결**: 15분 후 자동 해제 또는 관리자 문의

#### 세션 만료
- **문제**: 1시간 후 자동 로그아웃
- **해결**: 다시 로그인

### 2. 2FA 문제

#### 인증 코드 불일치
- **문제**: 6자리 코드가 맞지 않음
- **해결**: 
  - 기기 시간 동기화 확인
  - 백업 코드 사용
  - 관리자에게 2FA 재설정 요청

#### QR 코드 스캔 실패
- **문제**: QR 코드를 읽을 수 없음
- **해결**: 수동 키 입력 사용

### 3. 권한 문제

#### 페이지 접근 거부
- **문제**: "권한이 없습니다" 메시지
- **해결**: 
  - 현재 역할 확인
  - 관리자에게 권한 요청
  - 올바른 계정으로 로그인

## 📈 향후 개선 계획

### 1. 추가 보안 기능
- **생체 인증**: 지문, 얼굴 인식
- **디바이스 인증**: 신뢰할 수 있는 기기 등록
- **IP 화이트리스트**: 특정 IP에서만 접근 허용
- **감사 로그**: 모든 사용자 활동 기록

### 2. 사용성 개선
- **SSO 연동**: 기업 계정과 연동
- **소셜 로그인**: Google, Microsoft 계정 로그인
- **비밀번호 없는 로그인**: 이메일 링크 인증

### 3. 모니터링 강화
- **실시간 보안 알림**: 의심스러운 활동 감지
- **보안 대시보드**: 보안 상태 모니터링
- **자동 위협 대응**: 자동 계정 잠금, 알림

## 📞 지원

### 기술 지원
- **이메일**: support@company.com
- **내부 문의**: IT팀
- **긴급 상황**: 보안팀 직통

### 문서 업데이트
- **버전**: 1.0.0
- **최종 수정**: 2025-01-15
- **다음 검토**: 2025-04-15

---

**⚠️ 중요**: 이 문서의 보안 정보는 기밀입니다. 외부 유출을 금지합니다. 