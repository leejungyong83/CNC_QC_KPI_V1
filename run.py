"""
CNC 품질 검사 KPI 앱 실행 스크립트
"""
import os
import subprocess
import sys
import time
from pathlib import Path

def check_and_install_dependencies():
    """필요한 패키지 설치 확인 및 설치"""
    required_packages = [
        "streamlit", "pandas", "python-dotenv", "supabase", "plotly",
        "xlsxwriter", "openpyxl", "matplotlib", "seaborn"
    ]
    
    print("의존성 패키지 확인 중...")
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package} 패키지가 이미 설치되어 있습니다.")
        except ImportError:
            print(f"⚠️ {package} 패키지를 설치합니다...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} 패키지 설치 완료")

def create_env_file_if_not_exists():
    """환경 변수 파일이 없으면 예제 파일을 복사합니다."""
    env_file = Path(".env")
    env_example_file = Path("env.example")
    
    if not env_file.exists() and env_example_file.exists():
        print("환경 변수 파일이 없습니다. 예제 파일을 복사합니다...")
        with open(env_example_file, "r") as src:
            env_content = src.read()
        
        with open(env_file, "w") as dest:
            dest.write(env_content)
        
        print("✅ .env 파일이 생성되었습니다. 필요한 경우 내용을 수정하세요.")

def run_streamlit_app():
    """Streamlit 앱 실행"""
    print("Streamlit 앱을 시작합니다...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])

if __name__ == "__main__":
    # 필요한 패키지 확인 및 설치
    check_and_install_dependencies()
    
    # 환경 변수 파일 확인
    create_env_file_if_not_exists()
    
    # Streamlit 앱 실행
    run_streamlit_app() 