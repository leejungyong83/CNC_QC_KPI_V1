#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CNC KPI 프로젝트 개요 보고서 저장 스크립트
README_NEW.md 파일의 내용을 텍스트 파일로 저장합니다.
"""

import os
from datetime import datetime

def convert_markdown_to_text(markdown_content):
    """마크다운 내용을 일반 텍스트로 변환합니다."""
    lines = markdown_content.split('\n')
    text_lines = []
    
    for line in lines:
        # 마크다운 문법 제거
        line = line.replace('**', '')  # 볼드 제거
        line = line.replace('*', '')   # 이탤릭 제거
        line = line.replace('`', '')   # 코드 블록 제거
        
        # 헤더 변환
        if line.startswith('# '):
            text_lines.append('=' * 60)
            text_lines.append(line[2:].strip())
            text_lines.append('=' * 60)
        elif line.startswith('## '):
            text_lines.append('')
            text_lines.append('-' * 40)
            text_lines.append(line[3:].strip())
            text_lines.append('-' * 40)
        elif line.startswith('### '):
            text_lines.append('')
            text_lines.append(f"▶ {line[4:].strip()}")
            text_lines.append('')
        elif line.startswith('#### '):
            text_lines.append(f"  • {line[5:].strip()}")
        else:
            # 일반 텍스트
            text_lines.append(line)
    
    return '\n'.join(text_lines)

def save_project_report():
    """프로젝트 개요 보고서를 텍스트 파일로 저장합니다."""
    try:
        # README_NEW.md 파일 읽기
        with open('README_NEW.md', 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # 마크다운을 텍스트로 변환
        text_content = convert_markdown_to_text(markdown_content)
        
        # 헤더 추가
        header = f"""
============================================================
CNC 품질 검사 KPI 앱 - 전체 프로젝트 개요 보고서
============================================================
생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
파일명: CNC_KPI_프로젝트_개요_보고서.txt
============================================================

"""
        
        # 푸터 추가
        footer = f"""

============================================================
보고서 생성 완료
생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
============================================================
"""
        
        # 최종 내용 조합
        final_content = header + text_content + footer
        
        # 파일명 생성 (현재 날짜 포함)
        current_date = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"CNC_KPI_프로젝트_개요_보고서_{current_date}.txt"
        
        # 텍스트 파일로 저장
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        print(f"✅ 프로젝트 개요 보고서가 성공적으로 저장되었습니다!")
        print(f"📁 파일명: {filename}")
        print(f"📍 위치: {os.path.abspath(filename)}")
        print(f"📄 파일 크기: {len(final_content.encode('utf-8'))} bytes")
        
        return filename
        
    except FileNotFoundError:
        print("❌ README_NEW.md 파일을 찾을 수 없습니다.")
        print("현재 디렉토리에 README_NEW.md 파일이 있는지 확인해주세요.")
        return None
        
    except Exception as e:
        print(f"❌ 오류가 발생했습니다: {str(e)}")
        return None

def main():
    """메인 함수"""
    print("🔧 CNC KPI 프로젝트 개요 보고서 저장 도구")
    print("=" * 50)
    
    # 현재 디렉토리 확인
    current_dir = os.getcwd()
    print(f"📂 현재 작업 디렉토리: {current_dir}")
    
    # README_NEW.md 파일 존재 확인
    if os.path.exists('README_NEW.md'):
        print("✅ README_NEW.md 파일을 찾았습니다.")
        
        # 사용자 확인
        response = input("\n📝 프로젝트 개요 보고서를 텍스트 파일로 저장하시겠습니까? (y/n): ")
        
        if response.lower() in ['y', 'yes', '예', 'ㅇ']:
            filename = save_project_report()
            
            if filename:
                print(f"\n🎉 완료! 노트패드로 '{filename}' 파일을 열어보세요.")
                
                # Windows에서 노트패드로 파일 열기 시도
                try:
                    os.system(f'notepad "{filename}"')
                except:
                    print("💡 수동으로 노트패드에서 파일을 열어주세요.")
        else:
            print("❌ 작업이 취소되었습니다.")
    else:
        print("❌ README_NEW.md 파일을 찾을 수 없습니다.")
        print("QC_KPI 프로젝트 폴더에서 이 스크립트를 실행해주세요.")

if __name__ == "__main__":
    main() 