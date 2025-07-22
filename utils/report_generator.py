"""
자동 보고서 생성 시스템
일별/주별/월별 보고서 자동 생성 및 이메일 발송 기능
"""

import streamlit as st
import pandas as pd
import io
import os
import smtplib
import ssl
from datetime import datetime, timedelta, date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Optional, Tuple
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import base64
from utils.supabase_client import get_supabase_client
from utils.performance_optimizer import cached


class ReportGenerator:
    """자동 보고서 생성 클래스"""
    
    def __init__(self):
        self.supabase = None
        try:
            self.supabase = get_supabase_client()
        except Exception:
            pass
    
    @cached(ttl=3600, key_prefix="report_")  # 1시간 캐시
    def get_report_data(self, start_date: date, end_date: date) -> Dict:
        """보고서용 데이터 조회"""
        if not self.supabase:
            return self._get_sample_data()
        
        try:
            # 기간별 검사 데이터 조회
            inspection_result = self.supabase.table('inspection_data') \
                .select('*, inspectors(name, employee_id), production_models(model_name, model_no)') \
                .gte('inspection_date', start_date.strftime('%Y-%m-%d')) \
                .lte('inspection_date', end_date.strftime('%Y-%m-%d')) \
                .order('inspection_date', desc=True) \
                .execute()
            
            inspections = inspection_result.data if inspection_result.data else []
            
            # 불량 상세 정보 조회
            defect_result = self.supabase.table('defects') \
                .select('*, defect_types(name, category), inspection_data(inspection_date)') \
                .execute()
            
            defects = defect_result.data if defect_result.data else []
            
            return {
                'inspections': inspections,
                'defects': defects,
                'period': f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}"
            }
            
        except Exception as e:
            st.warning(f"데이터 조회 실패: {str(e)}")
            return self._get_sample_data()
    
    def _get_sample_data(self) -> Dict:
        """샘플 데이터 반환 (DB 연결 실패 시)"""
        today = date.today()
        return {
            'inspections': [
                {
                    'inspection_date': today.strftime('%Y-%m-%d'),
                    'result': '합격',
                    'total_inspected': 100,
                    'defect_quantity': 2,
                    'pass_quantity': 98,
                    'inspectors': {'name': '김검사', 'employee_id': 'I001'},
                    'production_models': {'model_name': 'PA1', 'model_no': 'MODEL-001'}
                }
            ],
            'defects': [],
            'period': f"{today.strftime('%Y-%m-%d')} ~ {today.strftime('%Y-%m-%d')}"
        }
    
    def calculate_report_metrics(self, data: Dict) -> Dict:
        """보고서 메트릭 계산"""
        inspections = data['inspections']
        
        if not inspections:
            return {
                'total_inspections': 0,
                'total_inspected_qty': 0,
                'total_defect_qty': 0,
                'total_pass_qty': 0,
                'defect_rate': 0.0,
                'pass_rate': 0.0,
                'inspection_efficiency': 0.0,
                'daily_average': 0.0,
                'top_models': [],
                'top_inspectors': [],
                'defect_trends': []
            }
        
        # 기본 메트릭 계산
        total_inspections = len(inspections)
        total_inspected_qty = sum(i.get('total_inspected', 0) for i in inspections)
        total_defect_qty = sum(i.get('defect_quantity', 0) for i in inspections)
        total_pass_qty = sum(i.get('pass_quantity', 0) for i in inspections)
        
        defect_rate = (total_defect_qty / total_inspected_qty * 100) if total_inspected_qty > 0 else 0.0
        pass_rate = (total_pass_qty / total_inspected_qty * 100) if total_inspected_qty > 0 else 0.0
        
        pass_inspections = len([i for i in inspections if i.get('result') == '합격'])
        inspection_efficiency = (pass_inspections / total_inspections * 100) if total_inspections > 0 else 0.0
        
        # 일일 평균 계산
        unique_dates = len(set(i.get('inspection_date') for i in inspections))
        daily_average = total_inspections / unique_dates if unique_dates > 0 else 0.0
        
        # 상위 모델 분석
        model_stats = {}
        for inspection in inspections:
            model_info = inspection.get('production_models', {})
            model_name = model_info.get('model_name', 'Unknown') if model_info else 'Unknown'
            
            if model_name not in model_stats:
                model_stats[model_name] = {
                    'count': 0,
                    'total_qty': 0,
                    'defect_qty': 0
                }
            
            model_stats[model_name]['count'] += 1
            model_stats[model_name]['total_qty'] += inspection.get('total_inspected', 0)
            model_stats[model_name]['defect_qty'] += inspection.get('defect_quantity', 0)
        
        top_models = []
        for model_name, stats in model_stats.items():
            defect_rate_model = (stats['defect_qty'] / stats['total_qty'] * 100) if stats['total_qty'] > 0 else 0.0
            top_models.append({
                'model': model_name,
                'inspections': stats['count'],
                'defect_rate': round(defect_rate_model, 2)
            })
        
        top_models.sort(key=lambda x: x['inspections'], reverse=True)
        top_models = top_models[:5]
        
        # 상위 검사자 분석
        inspector_stats = {}
        for inspection in inspections:
            inspector_info = inspection.get('inspectors', {})
            inspector_name = inspector_info.get('name', 'Unknown') if inspector_info else 'Unknown'
            
            if inspector_name not in inspector_stats:
                inspector_stats[inspector_name] = {
                    'count': 0,
                    'pass_count': 0
                }
            
            inspector_stats[inspector_name]['count'] += 1
            if inspection.get('result') == '합격':
                inspector_stats[inspector_name]['pass_count'] += 1
        
        top_inspectors = []
        for inspector_name, stats in inspector_stats.items():
            pass_rate_inspector = (stats['pass_count'] / stats['count'] * 100) if stats['count'] > 0 else 0.0
            top_inspectors.append({
                'inspector': inspector_name,
                'inspections': stats['count'],
                'pass_rate': round(pass_rate_inspector, 1)
            })
        
        top_inspectors.sort(key=lambda x: x['pass_rate'], reverse=True)
        top_inspectors = top_inspectors[:5]
        
        return {
            'total_inspections': total_inspections,
            'total_inspected_qty': total_inspected_qty,
            'total_defect_qty': total_defect_qty,
            'total_pass_qty': total_pass_qty,
            'defect_rate': round(defect_rate, 3),
            'pass_rate': round(pass_rate, 1),
            'inspection_efficiency': round(inspection_efficiency, 1),
            'daily_average': round(daily_average, 1),
            'top_models': top_models,
            'top_inspectors': top_inspectors,
            'defect_trends': self._calculate_defect_trends(inspections)
        }
    
    def _calculate_defect_trends(self, inspections: List) -> List:
        """불량 트렌드 계산"""
        date_stats = {}
        
        for inspection in inspections:
            inspection_date = inspection.get('inspection_date')
            if inspection_date not in date_stats:
                date_stats[inspection_date] = {
                    'total_qty': 0,
                    'defect_qty': 0
                }
            
            date_stats[inspection_date]['total_qty'] += inspection.get('total_inspected', 0)
            date_stats[inspection_date]['defect_qty'] += inspection.get('defect_quantity', 0)
        
        trends = []
        for date_str, stats in sorted(date_stats.items()):
            defect_rate = (stats['defect_qty'] / stats['total_qty'] * 100) if stats['total_qty'] > 0 else 0.0
            trends.append({
                'date': date_str,
                'defect_rate': round(defect_rate, 2)
            })
        
        return trends
    
    def generate_daily_report(self, target_date: date) -> Tuple[str, bytes]:
        """일별 보고서 생성"""
        data = self.get_report_data(target_date, target_date)
        metrics = self.calculate_report_metrics(data)
        
        # HTML 보고서 생성
        html_content = self._generate_html_report(
            title=f"일별 검사 보고서 - {target_date.strftime('%Y년 %m월 %d일')}",
            period=target_date.strftime('%Y-%m-%d'),
            metrics=metrics,
            data=data,
            report_type="daily"
        )
        
        # PDF 변환 (간단한 HTML 저장)
        pdf_bytes = html_content.encode('utf-8')
        
        return html_content, pdf_bytes
    
    def generate_weekly_report(self, end_date: date) -> Tuple[str, bytes]:
        """주별 보고서 생성"""
        start_date = end_date - timedelta(days=6)
        data = self.get_report_data(start_date, end_date)
        metrics = self.calculate_report_metrics(data)
        
        # HTML 보고서 생성
        html_content = self._generate_html_report(
            title=f"주별 검사 보고서 - {start_date.strftime('%m/%d')} ~ {end_date.strftime('%m/%d')}",
            period=f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}",
            metrics=metrics,
            data=data,
            report_type="weekly"
        )
        
        pdf_bytes = html_content.encode('utf-8')
        
        return html_content, pdf_bytes
    
    def generate_monthly_report(self, year: int, month: int) -> Tuple[str, bytes]:
        """월별 보고서 생성"""
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        data = self.get_report_data(start_date, end_date)
        metrics = self.calculate_report_metrics(data)
        
        # HTML 보고서 생성
        html_content = self._generate_html_report(
            title=f"월별 검사 보고서 - {year}년 {month}월",
            period=f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}",
            metrics=metrics,
            data=data,
            report_type="monthly"
        )
        
        pdf_bytes = html_content.encode('utf-8')
        
        return html_content, pdf_bytes
    
    def _generate_html_report(self, title: str, period: str, metrics: Dict, data: Dict, report_type: str) -> str:
        """HTML 보고서 생성"""
        
        # 차트 생성 (간단한 텍스트 기반)
        defect_trend_text = ""
        if metrics['defect_trends']:
            defect_trend_text = "<h4>📈 불량률 추이</h4><ul>"
            for trend in metrics['defect_trends'][-7:]:  # 최근 7일
                defect_trend_text += f"<li>{trend['date']}: {trend['defect_rate']}%</li>"
            defect_trend_text += "</ul>"
        
        top_models_text = ""
        if metrics['top_models']:
            top_models_text = "<h4>🏆 주요 생산 모델</h4><ul>"
            for model in metrics['top_models']:
                top_models_text += f"<li>{model['model']}: {model['inspections']}건 (불량률 {model['defect_rate']}%)</li>"
            top_models_text += "</ul>"
        
        top_inspectors_text = ""
        if metrics['top_inspectors']:
            top_inspectors_text = "<h4>👨‍💼 검사자 성과</h4><ul>"
            for inspector in metrics['top_inspectors']:
                top_inspectors_text += f"<li>{inspector['inspector']}: {inspector['inspections']}건 (합격률 {inspector['pass_rate']}%)</li>"
            top_inspectors_text += "</ul>"
        
        html_template = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                body {{
                    font-family: 'Malgun Gothic', Arial, sans-serif;
                    margin: 20px;
                    line-height: 1.6;
                    color: #333;
                }}
                .header {{
                    text-align: center;
                    border-bottom: 3px solid #4CAF50;
                    padding-bottom: 20px;
                    margin-bottom: 30px;
                }}
                .metrics {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .metric-card {{
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    padding: 15px;
                    text-align: center;
                    background: #f9f9f9;
                }}
                .metric-value {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #4CAF50;
                }}
                .metric-label {{
                    font-size: 12px;
                    color: #666;
                    margin-top: 5px;
                }}
                .section {{
                    margin-bottom: 30px;
                    padding: 20px;
                    border: 1px solid #eee;
                    border-radius: 8px;
                }}
                .warning {{
                    background-color: #fff3cd;
                    border-color: #ffeaa7;
                    color: #856404;
                    padding: 10px;
                    border-radius: 5px;
                    margin: 10px 0;
                }}
                .success {{
                    background-color: #d4edda;
                    border-color: #c3e6cb;
                    color: #155724;
                    padding: 10px;
                    border-radius: 5px;
                    margin: 10px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 50px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    color: #666;
                    font-size: 12px;
                }}
                ul {{
                    list-style-type: none;
                    padding: 0;
                }}
                li {{
                    padding: 5px 0;
                    border-bottom: 1px solid #eee;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🏭 {title}</h1>
                <p><strong>기간:</strong> {period}</p>
                <p><strong>생성 시간:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="metrics">
                <div class="metric-card">
                    <div class="metric-value">{metrics['total_inspections']}</div>
                    <div class="metric-label">총 검사 건수</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{metrics['total_inspected_qty']:,}</div>
                    <div class="metric-label">검사 수량</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{metrics['defect_rate']}%</div>
                    <div class="metric-label">불량률</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{metrics['inspection_efficiency']}%</div>
                    <div class="metric-label">검사 효율성</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{metrics['daily_average']}</div>
                    <div class="metric-label">일평균 검사</div>
                </div>
            </div>
            
            <div class="section">
                <h3>📊 주요 지표 분석</h3>
                
                {self._get_kpi_analysis(metrics)}
                
                {top_models_text}
                
                {top_inspectors_text}
                
                {defect_trend_text}
            </div>
            
            <div class="section">
                <h3>💡 개선 권고사항</h3>
                {self._get_recommendations(metrics)}
            </div>
            
            <div class="footer">
                <p>📧 이 보고서는 CNC QC KPI 시스템에서 자동 생성되었습니다.</p>
                <p>문의사항이 있으시면 시스템 관리자에게 연락해주세요.</p>
            </div>
        </body>
        </html>
        """
        
        return html_template
    
    def _get_kpi_analysis(self, metrics: Dict) -> str:
        """KPI 분석 텍스트 생성"""
        analysis = []
        
        # 불량률 분석
        if metrics['defect_rate'] <= 1.0:
            analysis.append('<div class="success">✅ <strong>불량률 우수:</strong> 목표 수준 유지 중입니다.</div>')
        elif metrics['defect_rate'] <= 2.0:
            analysis.append('<div class="warning">⚠️ <strong>불량률 주의:</strong> 개선이 필요합니다.</div>')
        else:
            analysis.append('<div class="warning">🚨 <strong>불량률 위험:</strong> 즉시 개선 조치가 필요합니다.</div>')
        
        # 검사 효율성 분석
        if metrics['inspection_efficiency'] >= 95.0:
            analysis.append('<div class="success">✅ <strong>검사 효율성 우수:</strong> 높은 합격률을 유지하고 있습니다.</div>')
        elif metrics['inspection_efficiency'] >= 90.0:
            analysis.append('<div class="warning">⚠️ <strong>검사 효율성 보통:</strong> 합격률 향상이 필요합니다.</div>')
        else:
            analysis.append('<div class="warning">🚨 <strong>검사 효율성 저조:</strong> 검사 프로세스 점검이 필요합니다.</div>')
        
        return ''.join(analysis)
    
    def _get_recommendations(self, metrics: Dict) -> str:
        """개선 권고사항 생성"""
        recommendations = []
        
        if metrics['defect_rate'] > 2.0:
            recommendations.append("• 불량률이 높습니다. 생산 공정 점검 및 작업자 교육을 실시하세요.")
        
        if metrics['inspection_efficiency'] < 90.0:
            recommendations.append("• 검사 효율성이 낮습니다. 검사 기준 재검토 및 검사자 교육을 진행하세요.")
        
        if metrics['daily_average'] < 5.0:
            recommendations.append("• 검사 빈도가 낮습니다. 정기 검사 스케줄을 수립하세요.")
        
        if not recommendations:
            recommendations.append("• 현재 모든 지표가 양호한 상태입니다. 지속적인 모니터링을 유지하세요.")
        
        return '<ul>' + ''.join(f'<li>{rec}</li>' for rec in recommendations) + '</ul>'


class EmailSender:
    """이메일 발송 클래스"""
    
    def __init__(self):
        self.smtp_server = st.secrets.get("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = st.secrets.get("SMTP_PORT", 587)
        self.email_user = st.secrets.get("EMAIL_USER", "")
        self.email_password = st.secrets.get("EMAIL_PASSWORD", "")
    
    def send_report(self, recipient_email: str, subject: str, html_content: str, 
                   attachment_data: bytes = None, attachment_name: str = None) -> bool:
        """보고서 이메일 발송"""
        
        if not self.email_user or not self.email_password:
            st.warning("이메일 설정이 구성되지 않았습니다. Streamlit secrets에서 EMAIL_USER와 EMAIL_PASSWORD를 설정하세요.")
            return False
        
        try:
            # 이메일 메시지 생성
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_user
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            # HTML 본문 추가
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # 첨부파일 추가
            if attachment_data and attachment_name:
                attachment = MIMEBase('application', 'octet-stream')
                attachment.set_payload(attachment_data)
                encoders.encode_base64(attachment)
                attachment.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {attachment_name}'
                )
                msg.attach(attachment)
            
            # SMTP 서버 연결 및 발송
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            st.error(f"이메일 발송 실패: {str(e)}")
            return False


class AutoReportScheduler:
    """자동 보고서 스케줄러"""
    
    def __init__(self):
        self.report_generator = ReportGenerator()
        self.email_sender = EmailSender()
    
    def schedule_daily_report(self, recipient_emails: List[str], send_time: str = "09:00") -> bool:
        """일별 보고서 스케줄 설정"""
        # Streamlit에서는 실제 스케줄링이 어려우므로 수동 실행 방식으로 구현
        
        try:
            today = date.today()
            html_content, pdf_data = self.report_generator.generate_daily_report(today)
            
            subject = f"[CNC QC] 일별 검사 보고서 - {today.strftime('%Y년 %m월 %d일')}"
            
            success_count = 0
            for email in recipient_emails:
                if self.email_sender.send_report(
                    recipient_email=email,
                    subject=subject,
                    html_content=html_content,
                    attachment_data=pdf_data,
                    attachment_name=f"daily_report_{today.strftime('%Y%m%d')}.html"
                ):
                    success_count += 1
            
            return success_count > 0
            
        except Exception as e:
            st.error(f"일별 보고서 발송 실패: {str(e)}")
            return False
    
    def schedule_weekly_report(self, recipient_emails: List[str]) -> bool:
        """주별 보고서 스케줄 실행"""
        try:
            today = date.today()
            # 지난 주 일요일부터 토요일까지
            days_since_sunday = today.weekday() + 1 if today.weekday() != 6 else 0
            end_date = today - timedelta(days=days_since_sunday)
            
            html_content, pdf_data = self.report_generator.generate_weekly_report(end_date)
            
            subject = f"[CNC QC] 주별 검사 보고서 - {end_date.strftime('%Y년 %m월 %W주차')}"
            
            success_count = 0
            for email in recipient_emails:
                if self.email_sender.send_report(
                    recipient_email=email,
                    subject=subject,
                    html_content=html_content,
                    attachment_data=pdf_data,
                    attachment_name=f"weekly_report_{end_date.strftime('%Y%m%d')}.html"
                ):
                    success_count += 1
            
            return success_count > 0
            
        except Exception as e:
            st.error(f"주별 보고서 발송 실패: {str(e)}")
            return False
    
    def schedule_monthly_report(self, recipient_emails: List[str], year: int = None, month: int = None) -> bool:
        """월별 보고서 스케줄 실행"""
        try:
            if not year or not month:
                # 지난 달 보고서
                today = date.today()
                if today.month == 1:
                    year, month = today.year - 1, 12
                else:
                    year, month = today.year, today.month - 1
            
            html_content, pdf_data = self.report_generator.generate_monthly_report(year, month)
            
            subject = f"[CNC QC] 월별 검사 보고서 - {year}년 {month}월"
            
            success_count = 0
            for email in recipient_emails:
                if self.email_sender.send_report(
                    recipient_email=email,
                    subject=subject,
                    html_content=html_content,
                    attachment_data=pdf_data,
                    attachment_name=f"monthly_report_{year}{month:02d}.html"
                ):
                    success_count += 1
            
            return success_count > 0
            
        except Exception as e:
            st.error(f"월별 보고서 발송 실패: {str(e)}")
            return False


# 전역 인스턴스
report_generator = ReportGenerator()
auto_scheduler = AutoReportScheduler()


if __name__ == "__main__":
    # 테스트 실행
    today = date.today()
    html, pdf = report_generator.generate_daily_report(today)
    print("Daily report generated successfully!") 