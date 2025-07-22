"""
에러 핸들링 모듈
사용자 친화적인 에러 메시지와 복구 방안을 제공하는 시스템
"""

import streamlit as st
import traceback
import logging
from datetime import datetime
from typing import Optional, Dict, Any, Callable
import functools
import os


class ErrorHandler:
    """통합 에러 핸들러 클래스"""
    
    def __init__(self):
        self.setup_logging()
        self.error_count = 0
        self.last_errors = []
        
    def setup_logging(self):
        """로깅 설정"""
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'{log_dir}/app_errors.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def handle_error(self, error: Exception, context: str = "", user_action: str = "", show_details: bool = False):
        """에러 처리 및 사용자 친화적 메시지 표시"""
        
        # 에러 카운트 증가
        self.error_count += 1
        
        # 에러 정보 수집
        error_info = {
            'timestamp': datetime.now(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'user_action': user_action,
            'traceback': traceback.format_exc()
        }
        
        # 최근 에러 목록에 추가 (최대 10개 유지)
        self.last_errors.append(error_info)
        if len(self.last_errors) > 10:
            self.last_errors.pop(0)
        
        # 로그 기록
        self.logger.error(f"Error in {context}: {error_info['error_message']}", exc_info=True)
        
        # 에러 유형별 사용자 메시지 생성
        user_message = self._generate_user_message(error_info)
        
        # 화면에 에러 메시지 표시
        self._display_error_message(user_message, error_info, show_details)
        
        return error_info
    
    def _generate_user_message(self, error_info: Dict[str, Any]) -> Dict[str, str]:
        """에러 유형별 사용자 친화적 메시지 생성"""
        
        error_type = error_info['error_type']
        error_message = error_info['error_message'].lower()
        context = error_info['context']
        
        # 데이터베이스 관련 에러
        if 'supabase' in context.lower() or 'database' in context.lower():
            if 'connection' in error_message or 'network' in error_message:
                return {
                    'title': '🔌 데이터베이스 연결 오류',
                    'message': '데이터베이스에 연결할 수 없습니다.',
                    'cause': '네트워크 연결 불안정 또는 서버 일시 중단',
                    'solutions': [
                        '인터넷 연결 상태를 확인하세요',
                        '잠시 후 다시 시도하세요',
                        '브라우저를 새로고침하세요',
                        'Supabase 서비스 상태를 확인하세요'
                    ],
                    'priority': 'high'
                }
            elif 'does not exist' in error_message or 'table' in error_message:
                return {
                    'title': '📋 데이터베이스 테이블 오류',
                    'message': '필요한 데이터베이스 테이블이 존재하지 않습니다.',
                    'cause': '데이터베이스 초기 설정이 완료되지 않음',
                    'solutions': [
                        'Supabase SQL Editor에서 database_schema_unified.sql 실행',
                        '관리자에게 문의하여 데이터베이스 설정 확인',
                        'Supabase 설정 메뉴에서 연결 테스트 실행'
                    ],
                    'priority': 'critical'
                }
            elif 'permission' in error_message or 'unauthorized' in error_message:
                return {
                    'title': '🔐 권한 오류',
                    'message': '데이터베이스 접근 권한이 없습니다.',
                    'cause': 'API 키 또는 권한 설정 문제',
                    'solutions': [
                        'Supabase API 키 확인',
                        'RLS(Row Level Security) 정책 확인',
                        '관리자에게 권한 요청'
                    ],
                    'priority': 'high'
                }
        
        # 파일 관련 에러
        elif 'file' in context.lower() or 'upload' in context.lower():
            if 'size' in error_message:
                return {
                    'title': '📁 파일 크기 오류',
                    'message': '업로드하려는 파일이 너무 큽니다.',
                    'cause': '파일 크기가 허용 한도(10MB)를 초과',
                    'solutions': [
                        '파일 크기를 10MB 이하로 줄이세요',
                        '이미지의 경우 압축하세요',
                        '여러 파일로 나누어 업로드하세요'
                    ],
                    'priority': 'medium'
                }
            elif 'format' in error_message or 'type' in error_message:
                return {
                    'title': '🎨 파일 형식 오류',
                    'message': '지원하지 않는 파일 형식입니다.',
                    'cause': '허용되지 않은 파일 확장자',
                    'solutions': [
                        '지원 형식: PNG, JPG, JPEG, GIF, BMP',
                        '파일 확장자를 확인하세요',
                        '다른 형식으로 변환 후 업로드하세요'
                    ],
                    'priority': 'medium'
                }
        
        # 인증 관련 에러
        elif 'auth' in context.lower() or 'login' in context.lower():
            return {
                'title': '🔑 인증 오류',
                'message': '로그인에 실패했습니다.',
                'cause': '잘못된 계정 정보 또는 세션 만료',
                'solutions': [
                    '계정 정보를 다시 확인하세요',
                    '비밀번호를 재설정하세요',
                    '브라우저 쿠키를 삭제하고 다시 로그인하세요',
                    '관리자에게 계정 상태를 문의하세요'
                ],
                'priority': 'high'
            }
        
        # 일반적인 에러
        else:
            return {
                'title': '⚠️ 시스템 오류',
                'message': '예상치 못한 오류가 발생했습니다.',
                'cause': '시스템 내부 오류',
                'solutions': [
                    '페이지를 새로고침하세요',
                    '잠시 후 다시 시도하세요',
                    '문제가 계속되면 관리자에게 문의하세요',
                    '브라우저 캐시를 삭제해보세요'
                ],
                'priority': 'medium'
            }
    
    def _display_error_message(self, user_message: Dict[str, str], error_info: Dict[str, Any], show_details: bool):
        """에러 메시지를 화면에 표시"""
        
        priority = user_message.get('priority', 'medium')
        
        # 우선순위에 따른 스타일링
        if priority == 'critical':
            st.error(f"🚨 **{user_message['title']}**")
        elif priority == 'high':
            st.error(f"❌ **{user_message['title']}**")
        elif priority == 'medium':
            st.warning(f"⚠️ **{user_message['title']}**")
        else:
            st.info(f"ℹ️ **{user_message['title']}**")
        
        # 메시지 및 원인
        st.write(f"**문제 상황**: {user_message['message']}")
        st.write(f"**원인**: {user_message['cause']}")
        
        # 해결 방안
        st.write("**해결 방법**:")
        for i, solution in enumerate(user_message['solutions'], 1):
            st.write(f"{i}. {solution}")
        
        # 상세 정보 (선택적)
        if show_details:
            with st.expander("🔍 기술 세부 정보 (개발자용)"):
                st.write(f"**에러 타입**: {error_info['error_type']}")
                st.write(f"**발생 시간**: {error_info['timestamp']}")
                st.write(f"**컨텍스트**: {error_info['context']}")
                st.write(f"**사용자 액션**: {error_info['user_action']}")
                st.code(error_info['error_message'])
                if st.checkbox("전체 스택 트레이스 보기"):
                    st.code(error_info['traceback'])
    
    def get_error_stats(self) -> Dict[str, Any]:
        """에러 통계 반환"""
        if not self.last_errors:
            return {
                'total_errors': 0,
                'recent_errors': 0,
                'error_types': {},
                'last_error_time': None
            }
        
        # 에러 타입별 집계
        error_types = {}
        for error in self.last_errors:
            error_type = error['error_type']
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        # 최근 1시간 에러 수
        recent_errors = sum(1 for error in self.last_errors 
                          if (datetime.now() - error['timestamp']).seconds < 3600)
        
        return {
            'total_errors': self.error_count,
            'recent_errors': recent_errors,
            'error_types': error_types,
            'last_error_time': self.last_errors[-1]['timestamp'] if self.last_errors else None
        }
    
    def show_error_dashboard(self):
        """에러 대시보드 표시"""
        st.subheader("🛠️ 시스템 상태 및 에러 모니터링")
        
        stats = self.get_error_stats()
        
        # 에러 통계 메트릭
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("총 에러 수", stats['total_errors'])
        
        with col2:
            st.metric("최근 1시간", stats['recent_errors'])
        
        with col3:
            error_types_count = len(stats['error_types'])
            st.metric("에러 유형", f"{error_types_count}개")
        
        with col4:
            if stats['last_error_time']:
                time_diff = datetime.now() - stats['last_error_time']
                if time_diff.seconds < 60:
                    last_error = f"{time_diff.seconds}초 전"
                elif time_diff.seconds < 3600:
                    last_error = f"{time_diff.seconds//60}분 전"
                else:
                    last_error = f"{time_diff.seconds//3600}시간 전"
                st.metric("마지막 에러", last_error)
            else:
                st.metric("마지막 에러", "없음")
        
        # 에러 유형별 분포
        if stats['error_types']:
            st.write("**에러 유형별 분포:**")
            for error_type, count in stats['error_types'].items():
                st.write(f"- **{error_type}**: {count}회")
        
        # 최근 에러 목록
        if self.last_errors:
            with st.expander(f"📋 최근 에러 목록 ({len(self.last_errors)}개)"):
                for i, error in enumerate(reversed(self.last_errors[-5:]), 1):
                    st.write(f"**{i}. {error['error_type']}** - {error['timestamp'].strftime('%H:%M:%S')}")
                    st.write(f"   컨텍스트: {error['context']}")
                    st.write(f"   메시지: {error['error_message']}")
                    st.write("---")


def safe_execute(func: Callable, context: str = "", user_action: str = "", show_details: bool = False):
    """함수를 안전하게 실행하는 데코레이터"""
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_handler = get_error_handler()
            error_handler.handle_error(e, context, user_action, show_details)
            return None
    
    return wrapper


def get_error_handler() -> ErrorHandler:
    """글로벌 에러 핸들러 인스턴스 반환"""
    if 'error_handler' not in st.session_state:
        st.session_state.error_handler = ErrorHandler()
    return st.session_state.error_handler


def show_error_recovery_guide():
    """에러 복구 가이드 표시"""
    st.subheader("🔧 문제 해결 가이드")
    
    with st.expander("🔌 연결 문제 해결"):
        st.write("**인터넷 연결 확인:**")
        st.write("1. 다른 웹사이트가 정상 작동하는지 확인")
        st.write("2. Wi-Fi 또는 유선 연결 상태 점검")
        st.write("3. 방화벽이나 보안 프로그램 설정 확인")
        
        st.write("**브라우저 문제 해결:**")
        st.write("1. 브라우저 새로고침 (Ctrl+F5)")
        st.write("2. 브라우저 캐시 및 쿠키 삭제")
        st.write("3. 시크릿/개인정보 보호 모드에서 접속 시도")
        st.write("4. 다른 브라우저에서 접속 시도")
    
    with st.expander("📊 데이터 문제 해결"):
        st.write("**데이터베이스 연결 문제:**")
        st.write("1. Supabase 서비스 상태 확인")
        st.write("2. API 키 및 URL 설정 확인")
        st.write("3. 관리자에게 서버 상태 문의")
        
        st.write("**데이터 입력 문제:**")
        st.write("1. 필수 필드가 모두 입력되었는지 확인")
        st.write("2. 입력 형식이 올바른지 확인")
        st.write("3. 특수문자나 이모지 사용 피하기")
    
    with st.expander("📱 모바일 사용 문제"):
        st.write("**모바일 최적화:**")
        st.write("1. 브라우저 설정에서 '데스크톱 사이트' 해제")
        st.write("2. 화면 회전 후 새로고침")
        st.write("3. 모바일 모드로 전환")
        
        st.write("**터치 입력 문제:**")
        st.write("1. 화면을 정확히 터치했는지 확인")
        st.write("2. 더블 탭이나 길게 누르기 시도")
        st.write("3. 키보드가 화면을 가리지 않도록 조정")
    
    # 즉시 도움받기 버튼
    st.write("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 페이지 새로고침", use_container_width=True):
            st.rerun()
    
    with col2:
        if st.button("🧹 캐시 초기화", use_container_width=True):
            # 세션 상태 초기화
            for key in list(st.session_state.keys()):
                if not key.startswith('error_'):
                    del st.session_state[key]
            st.success("✅ 캐시가 초기화되었습니다.")
            st.rerun()
    
    with col3:
        if st.button("📞 관리자 연락", use_container_width=True):
            st.info("📧 **관리자 연락처**\n\n이메일: admin@company.com\n전화: 02-1234-5678")


if __name__ == "__main__":
    # 테스트용 에러 핸들러
    error_handler = ErrorHandler()
    error_handler.show_error_dashboard() 