"""
CNC 품질 검사 KPI 앱 실행 스크립트
"""
import os
import subprocess
import sys

def install_requirements():
    """필요한 패키지 설치"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("필요한 패키지 설치 완료")
        return True
    except subprocess.CalledProcessError:
        print("패키지 설치 중 오류가 발생했습니다. requirements.txt 파일을 확인하세요.")
        return False

def run_app():
    """앱 실행"""
    try:
        cmd = [sys.executable, "-m", "streamlit", "run", "app.py"]
        subprocess.run(cmd)
    except Exception as e:
        print(f"앱 실행 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    print("CNC 품질 검사 KPI 앱 시작하기")
    
    # 패키지 설치 확인
    install = input("필요한 패키지를 설치하시겠습니까? (y/n): ").strip().lower()
    
    if install == "y":
        success = install_requirements()
        if not success:
            print("패키지 설치에 실패했습니다. 앱 실행을 중단합니다.")
            sys.exit(1)
    
    # 앱 실행
    print("앱을 실행합니다...")
    run_app() 