#!/usr/bin/env python3
"""
월요일 언어전환 기능 개발을 위한 자동 설치 스크립트
필요한 패키지 설치 및 기본 설정 완료
"""

import subprocess
import sys
import os
from typing import List, Tuple

def run_command(command: str) -> Tuple[bool, str]:
    """명령어 실행 및 결과 반환"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True,
            timeout=300  # 5분 타임아웃
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "명령어 실행 시간 초과"
    except Exception as e:
        return False, str(e)

def install_packages() -> bool:
    """필요한 패키지들 설치"""
    print("🚀 언어전환 기능 필요 패키지 설치 시작...")
    
    packages = [
        "googletrans==4.0.0rc1",
        "langdetect==1.0.9", 
        "streamlit-option-menu==0.3.6",
        "pycountry==22.3.5"
    ]
    
    all_success = True
    
    for package in packages:
        print(f"📦 {package} 설치 중...")
        success, output = run_command(f"pip install {package}")
        
        if success:
            print(f"✅ {package} 설치 완료")
        else:
            print(f"❌ {package} 설치 실패: {output}")
            all_success = False
    
    return all_success

def verify_installations() -> bool:
    """설치된 패키지 검증"""
    print("\n🔍 설치 검증 중...")
    
    tests = [
        ("googletrans", "from googletrans import Translator; print('✅ Google Translate 설치 확인')"),
        ("langdetect", "import langdetect; print('✅ Language Detect 설치 확인')"),
        ("streamlit_option_menu", "from streamlit_option_menu import option_menu; print('✅ Option Menu 설치 확인')"),
        ("pycountry", "import pycountry; print('✅ PyCountry 설치 확인')")
    ]
    
    all_verified = True
    
    for package_name, test_code in tests:
        success, output = run_command(f'python -c "{test_code}"')
        
        if success:
            print(output.strip())
        else:
            print(f"❌ {package_name} 검증 실패: {output}")
            all_verified = False
    
    return all_verified

def check_existing_modules() -> bool:
    """기존 모듈 상태 확인"""
    print("\n📋 기존 프로젝트 모듈 확인...")
    
    required_files = [
        "utils/language_manager.py",
        "utils/translation_ui.py",
        "utils/vietnam_timezone.py",
        "utils/shift_manager.py",
        "app.py",
        "requirements.txt"
    ]
    
    all_exist = True
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} 존재 확인")
        else:
            print(f"❌ {file_path} 누락!")
            all_exist = False
    
    return all_exist

def update_requirements_txt() -> bool:
    """requirements.txt 업데이트"""
    print("\n📝 requirements.txt 업데이트...")
    
    new_packages = [
        "googletrans==4.0.0rc1",
        "langdetect==1.0.9",
        "streamlit-option-menu==0.3.6", 
        "pycountry==22.3.5"
    ]
    
    try:
        # 기존 requirements.txt 읽기
        if os.path.exists("requirements.txt"):
            with open("requirements.txt", "r", encoding="utf-8") as f:
                existing_content = f.read()
        else:
            existing_content = ""
        
        # 새 패키지 추가
        with open("requirements.txt", "a", encoding="utf-8") as f:
            f.write("\n# 언어전환 기능 패키지 (2025-07-29 추가)\n")
            for package in new_packages:
                if package not in existing_content:
                    f.write(f"{package}\n")
                    print(f"✅ {package} requirements.txt에 추가")
                else:
                    print(f"⚠️ {package} 이미 존재")
        
        print("✅ requirements.txt 업데이트 완료")
        return True
        
    except Exception as e:
        print(f"❌ requirements.txt 업데이트 실패: {e}")
        return False

def create_backup() -> bool:
    """현재 상태 백업"""
    print("\n💾 현재 상태 백업 생성...")
    
    try:
        success, output = run_command("git add . && git commit -m 'backup: 언어전환 기능 개발 전 백업'")
        
        if success:
            print("✅ Git 백업 완료")
            return True
        else:
            print(f"⚠️ Git 백업 실패 (변경사항 없음?): {output}")
            return True  # 변경사항이 없을 수 있으므로 계속 진행
            
    except Exception as e:
        print(f"❌ 백업 실패: {e}")
        return False

def main():
    """메인 설치 프로세스"""
    print("=" * 60)
    print("🌐 QC KPI 언어전환 기능 개발 환경 설정")
    print("📅 2025년 7월 29일 (월요일 준비)")
    print("=" * 60)
    
    steps = [
        ("기존 모듈 확인", check_existing_modules),
        ("현재 상태 백업", create_backup),
        ("패키지 설치", install_packages),
        ("설치 검증", verify_installations),
        ("requirements.txt 업데이트", update_requirements_txt)
    ]
    
    success_count = 0
    total_steps = len(steps)
    
    for step_name, step_function in steps:
        print(f"\n🔄 {step_name} 진행 중...")
        
        if step_function():
            print(f"✅ {step_name} 완료")
            success_count += 1
        else:
            print(f"❌ {step_name} 실패")
    
    # 최종 결과
    print("\n" + "=" * 60)
    print(f"📊 설치 결과: {success_count}/{total_steps} 단계 완료")
    print(f"성공률: {success_count/total_steps*100:.1f}%")
    
    if success_count == total_steps:
        print("🎉 모든 준비 완료! 월요일 언어전환 기능 개발 시작 가능!")
        print("\n📋 다음 단계:")
        print("1. monday_setup_guide.md 파일 확인")
        print("2. utils/google_translator.py 생성")
        print("3. utils/translation_cache.py 생성")
        print("4. app.py 언어 선택기 통합")
        print("5. 각 페이지 다국어화 작업")
        return 0
    else:
        print("⚠️ 일부 단계가 실패했습니다. 수동으로 확인이 필요합니다.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 