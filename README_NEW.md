# CNC 품질 검사 KPI 앱

CNC 가공 품질 관리를 위한 종합적인 KPI 대시보드 및 데이터 관리 시스템입니다.

## 🚀 주요 기능

### 1. 검사실적 관리 (CRUD) ⭐ **NEW**
- **📋 검사실적 조회**: 기간별, 검사원별, 모델별 필터링 지원
- **➕ 검사실적 추가**: 실시간 검사 데이터 입력
- **✏️ 검사실적 수정**: 기존 검사실적 정보 수정
- **🗑️ 검사실적 삭제**: 안전한 데이터 삭제 (확인 절차 포함)
- **📊 데이터 통계**: 검사원별, 모델별, 일별 통계 및 차트

### 2. 생산모델 관리 (CRUD)
- **모델 등록**: 새로운 생산 모델 추가
- **모델 수정**: 기존 모델 정보 업데이트
- **모델 삭제**: 안전한 모델 삭제
- **모델 조회**: 전체 모델 목록 및 상세 정보

### 3. 검사자 관리 (CRUD)
- **검사자 등록**: 새로운 검사자 추가
- **검사자 수정**: 검사자 정보 업데이트
- **검사자 삭제**: 검사자 데이터 삭제
- **검사자 조회**: 검사자 목록 및 통계

### 4. 불량 유형 관리 (CRUD)
- **불량 유형 등록**: 새로운 불량 유형 추가
- **불량 유형 수정**: 기존 불량 유형 정보 수정
- **불량 유형 삭제**: 불량 유형 삭제
- **불량 유형 조회**: 전체 불량 유형 목록

### 5. 종합 대시보드
- **실시간 KPI**: 검사 통계, 불량률, 합격률
- **차트 및 그래프**: 시각적 데이터 분석
- **기간별 분석**: 일간, 주간, 월간, 연간 리포트

### 6. 데이터베이스 연동
- **Supabase 연동**: 실시간 데이터베이스 연결
- **오프라인 모드**: 연결 실패 시 더미 데이터 사용
- **자동 전환**: 온라인/오프라인 모드 자동 감지

## 🛠️ 기술 스택

- **Frontend**: Streamlit
- **Backend**: Python
- **Database**: Supabase (PostgreSQL)
- **Charts**: Plotly, Streamlit Charts
- **Authentication**: Supabase Auth

## 📦 설치 및 실행

### 1. 프로젝트 클론
```bash
git clone <repository-url>
cd QC_KPI
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경 설정
`.streamlit/secrets.toml` 파일에 Supabase 연결 정보를 입력하세요:

```toml
SUPABASE_URL = "your-supabase-url"
SUPABASE_KEY = "your-supabase-anon-key"
```

### 4. 데이터베이스 초기화
Supabase SQL Editor에서 다음 스크립트들을 순서대로 실행하세요:

1. `create_production_models_final.sql` - 생산모델 테이블 생성
2. `insert_production_models_data.sql` - 생산모델 샘플 데이터 삽입
3. `insert_sample_inspection_data.sql` - 검사실적 샘플 데이터 삽입

### 5. 앱 실행
```bash
streamlit run app.py
```

## 📊 데이터베이스 스키마

### inspection_data (검사실적)
- `id`: UUID (Primary Key)
- `inspection_date`: DATE (검사일자)
- `inspector_id`: UUID (검사자 ID, Foreign Key)
- `model_id`: UUID (모델 ID, Foreign Key)
- `result`: TEXT (검사결과: 합격/불합격)
- `quantity`: INTEGER (검사수량)
- `notes`: TEXT (비고)

### inspectors (검사자)
- `id`: UUID (Primary Key)
- `name`: TEXT (검사자명)
- `employee_id`: TEXT (사번)
- `department`: TEXT (부서)

### production_models (생산모델)
- `id`: UUID (Primary Key)
- `model_no`: TEXT (모델번호)
- `model_name`: TEXT (모델명)
- `process`: TEXT (공정)
- `notes`: TEXT (비고)

### defect_types (불량유형)
- `id`: UUID (Primary Key)
- `name`: TEXT (불량유형명)
- `description`: TEXT (설명)

## 🔧 주요 업데이트 (v2.0)

### 검사실적 관리 CRUD 완전 리뉴얼
- ✅ **조회 기능**: 기간별, 검사원별 필터링 지원
- ✅ **추가 기능**: 실시간 검사실적 입력
- ✅ **수정 기능**: 기존 검사실적 정보 수정
- ✅ **삭제 기능**: 안전한 데이터 삭제 (ID 확인 필요)
- ✅ **통계 기능**: 검사원별, 모델별, 일별 통계 및 차트

### 데이터베이스 연동 개선
- ✅ **실시간 연결**: Supabase 데이터베이스 실시간 연동
- ✅ **연결 상태 표시**: 온라인/오프라인 모드 시각적 표시
- ✅ **자동 전환**: 연결 실패 시 오프라인 모드 자동 전환
- ✅ **에러 처리**: 안정적인 에러 핸들링

### UI/UX 개선
- ✅ **아이콘 추가**: 각 탭에 직관적인 아이콘 적용
- ✅ **상태 표시**: 연결 상태 및 작업 결과 명확한 표시
- ✅ **사용자 안내**: 오프라인 모드 시 안내 메시지 제공

## 🎯 사용 방법

### 1. 검사실적 관리
1. **검사 데이터 입력** 메뉴 선택
2. **검사실적 추가** 탭에서 새로운 검사 데이터 입력
3. **검사실적 조회** 탭에서 기존 데이터 확인
4. **검사실적 수정** 탭에서 데이터 수정
5. **검사실적 삭제** 탭에서 불필요한 데이터 삭제
6. **데이터 통계** 탭에서 통계 분석 확인

### 2. 데이터베이스 설정
1. **Supabase 설정** 메뉴에서 연결 정보 입력
2. 연결 테스트 및 테이블 생성
3. 샘플 데이터 업로드

### 3. 대시보드 활용
1. **종합 대시보드**에서 전체 KPI 확인
2. 기간별 필터링으로 원하는 데이터 분석
3. 차트를 통한 시각적 데이터 분석

## 🔍 문제 해결

### Supabase 연결 문제
- `.streamlit/secrets.toml` 파일의 URL과 키 확인
- Supabase 프로젝트 설정에서 RLS 정책 확인
- 네트워크 연결 상태 확인

### 데이터 표시 문제
- 오프라인 모드에서는 샘플 데이터만 표시됨
- 실제 데이터 확인을 위해 Supabase 연결 필요
- SQL 스크립트로 샘플 데이터 삽입 권장

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여

프로젝트 개선을 위한 기여를 환영합니다. Pull Request나 Issue를 통해 참여해주세요.

---

**개발자**: CNC 품질관리팀  
**버전**: 2.0.0  
**최종 업데이트**: 2025-01-15 