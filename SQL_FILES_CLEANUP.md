# SQL 파일 정리 가이드

## 📁 **통합 완료**

**`database_schema_unified.sql`** 파일이 모든 SQL 기능을 통합했습니다.

---

## 🗑️ **삭제 대상 SQL 파일들**

다음 파일들은 `database_schema_unified.sql`로 통합되어 더 이상 필요하지 않습니다:

### 생산모델 관련 (7개 파일)
- ❌ `create_production_models_simple.sql` - 기본 기능만 포함
- ❌ `create_production_models_final.sql` - 완성도 높지만 부분적
- ❌ `create_production_models_preserve.sql` - 기존 데이터 보존용
- ❌ `create_production_models_table_fixed.sql` - 외래키 문제 해결용
- ❌ `create_production_models_table_safe.sql` - 안전한 버전
- ❌ `create_production_models_table.sql` - 기본 버전
- ❌ `insert_production_models_data.sql` - 데이터만 삽입

### 검사 테이블 관련 (2개 파일)
- ❌ `enhance_inspection_table.sql` - 테이블 구조 개선
- ❌ `insert_sample_inspection_data.sql` - 샘플 데이터만 삽입

### 디버그/수정 관련 (8개 파일)
- ❌ `fix_correct_hash.sql` - 패스워드 해시 수정
- ❌ `final_debug.sql` - 디버그용
- ❌ `fix_password_hash.sql` - 패스워드 해시 수정
- ❌ `debug_check.sql` - 디버그 체크
- ❌ `update_admins_password.sql` - 관리자 패스워드 업데이트
- ❌ `update_password_hash.sql` - 패스워드 해시 업데이트

---

## ✅ **새로운 통합 스키마의 장점**

### 🎯 **완전성**
- 모든 테이블을 하나의 파일에서 관리
- 외래키 관계 명확히 정의
- 인덱스와 제약조건 포함

### 🔒 **보안**
- 2FA 지원 컬럼 포함
- 패스워드 해시 및 Salt 필드
- 로그인 시도 제한 기능

### 📊 **확장성**
- 미래 기능을 위한 추가 컬럼
- 파일 첨부 경로 준비
- 심각도 레벨 및 상태 관리

### 🚀 **성능**
- 최적화된 인덱스 설계
- 효율적인 조회를 위한 구조

---

## 🔄 **마이그레이션 방법**

### 1. 새 환경 설정 시
```sql
-- Supabase SQL Editor에서 실행
-- database_schema_unified.sql 전체 복사 후 실행
```

### 2. 기존 환경 업그레이드 시
```sql
-- 1. 기존 데이터 백업
-- 2. DROP 문 주석 해제하여 기존 테이블 삭제
-- 3. database_schema_unified.sql 실행
-- 4. 백업 데이터 복원
```

---

## 📋 **사용 방법**

1. **개발 환경**: `database_schema_unified.sql` 전체 실행
2. **운영 환경**: DROP 문은 주석 처리하고 실행
3. **테스트 환경**: 샘플 데이터 포함하여 전체 실행

---

## 🧹 **정리 명령어**

기존 SQL 파일들을 정리하려면:

```bash
# 백업용 폴더 생성
mkdir sql_backup_old

# 기존 SQL 파일들을 백업 폴더로 이동
mv create_production_models*.sql sql_backup_old/
mv insert_*.sql sql_backup_old/
mv enhance_*.sql sql_backup_old/
mv fix_*.sql sql_backup_old/
mv debug_*.sql sql_backup_old/
mv update_*.sql sql_backup_old/
mv final_*.sql sql_backup_old/

echo "✅ SQL 파일 정리 완료!"
``` 