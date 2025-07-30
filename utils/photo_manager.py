"""
📷 사진 첨부 관리 시스템
2025-07-30 추가

QC 검사에서 사진 첨부 기능을 관리하는 모듈입니다.
- 로컬 파일 저장
- 이미지 리사이징
- 썸네일 생성
- 메타데이터 관리
"""

import os
import uuid
import hashlib
import streamlit as st
from datetime import datetime
from PIL import Image
import io
from typing import Dict, List, Optional, Tuple
import json

class PhotoManager:
    """사진 첨부 관리 클래스"""
    
    def __init__(self):
        self.upload_dir = "uploads/photos"
        self.thumbnail_dir = "uploads/thumbnails"
        self.metadata_dir = "uploads/metadata"
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.allowed_types = ['jpg', 'jpeg', 'png', 'webp']
        self.thumbnail_size = (200, 200)
        
        # 디렉토리 생성
        self._ensure_directories()
    
    def _ensure_directories(self):
        """필요한 디렉토리들을 생성합니다."""
        for directory in [self.upload_dir, self.thumbnail_dir, self.metadata_dir]:
            os.makedirs(directory, exist_ok=True)
    
    def _generate_file_id(self) -> str:
        """고유한 파일 ID를 생성합니다."""
        return str(uuid.uuid4())
    
    def _get_file_hash(self, file_content: bytes) -> str:
        """파일의 해시값을 계산합니다."""
        return hashlib.md5(file_content).hexdigest()
    
    def _validate_file(self, uploaded_file) -> Tuple[bool, str]:
        """업로드된 파일을 검증합니다."""
        try:
            # 파일 크기 검사
            if uploaded_file.size > self.max_file_size:
                return False, f"파일 크기가 너무 큽니다. 최대 {self.max_file_size // 1024 // 1024}MB까지 가능합니다."
            
            # 파일 확장자 검사
            file_extension = uploaded_file.name.split('.')[-1].lower()
            if file_extension not in self.allowed_types:
                return False, f"지원하지 않는 파일 형식입니다. 허용 형식: {', '.join(self.allowed_types)}"
            
            # 이미지 파일인지 검사
            try:
                image = Image.open(uploaded_file)
                image.verify()
                uploaded_file.seek(0)  # 파일 포인터 초기화
                return True, "검증 완료"
            except Exception:
                return False, "올바른 이미지 파일이 아닙니다."
                
        except Exception as e:
            return False, f"파일 검증 중 오류가 발생했습니다: {str(e)}"
    
    def _create_thumbnail(self, image: Image.Image) -> Image.Image:
        """썸네일 이미지를 생성합니다."""
        thumbnail = image.copy()
        thumbnail.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)
        return thumbnail
    
    def _save_metadata(self, file_id: str, metadata: Dict) -> bool:
        """메타데이터를 JSON 파일로 저장합니다."""
        try:
            metadata_path = os.path.join(self.metadata_dir, f"{file_id}.json")
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2, default=str)
            return True
        except Exception as e:
            st.error(f"메타데이터 저장 실패: {str(e)}")
            return False
    
    def upload_photo(self, 
                    uploaded_file, 
                    inspection_id: str,
                    photo_type: str = "inspection",
                    description: str = "",
                    capture_location: str = "",
                    uploaded_by: str = "") -> Optional[Dict]:
        """
        사진을 업로드하고 저장합니다.
        
        Args:
            uploaded_file: Streamlit 업로드 파일 객체
            inspection_id: 검사 데이터 ID
            photo_type: 사진 유형 (inspection, defect, equipment, process)
            description: 사진 설명
            capture_location: 촬영 위치
            uploaded_by: 업로드한 사용자
            
        Returns:
            성공시 파일 정보 딕셔너리, 실패시 None
        """
        try:
            # 파일 검증
            is_valid, message = self._validate_file(uploaded_file)
            if not is_valid:
                st.error(f"❌ {message}")
                return None
            
            # 파일 ID 생성
            file_id = self._generate_file_id()
            
            # 파일 내용 읽기
            file_content = uploaded_file.read()
            uploaded_file.seek(0)
            
            # 파일 해시 계산
            file_hash = self._get_file_hash(file_content)
            
            # 이미지 처리
            image = Image.open(io.BytesIO(file_content))
            
            # 원본 파일 저장
            file_extension = uploaded_file.name.split('.')[-1].lower()
            original_filename = f"{file_id}.{file_extension}"
            original_path = os.path.join(self.upload_dir, original_filename)
            
            with open(original_path, 'wb') as f:
                f.write(file_content)
            
            # 썸네일 생성 및 저장
            thumbnail = self._create_thumbnail(image)
            thumbnail_filename = f"{file_id}_thumb.{file_extension}"
            thumbnail_path = os.path.join(self.thumbnail_dir, thumbnail_filename)
            thumbnail.save(thumbnail_path)
            
            # 메타데이터 생성
            metadata = {
                'id': file_id,
                'inspection_id': inspection_id,
                'original_filename': uploaded_file.name,
                'stored_filename': original_filename,
                'thumbnail_filename': thumbnail_filename,
                'file_size': len(file_content),
                'file_type': uploaded_file.type,
                'file_hash': file_hash,
                'photo_type': photo_type,
                'description': description,
                'capture_location': capture_location,
                'width': image.width,
                'height': image.height,
                'uploaded_by': uploaded_by,
                'uploaded_at': datetime.now(),
                'is_active': True
            }
            
            # 메타데이터 저장
            if self._save_metadata(file_id, metadata):
                st.success(f"✅ '{uploaded_file.name}' 업로드 완료!")
                return metadata
            else:
                # 업로드된 파일들 정리
                for path in [original_path, thumbnail_path]:
                    if os.path.exists(path):
                        os.remove(path)
                return None
                
        except Exception as e:
            st.error(f"❌ 사진 업로드 실패: {str(e)}")
            return None
    
    def get_photos(self, inspection_id: str) -> List[Dict]:
        """특정 검사의 모든 사진을 조회합니다."""
        photos = []
        try:
            if os.path.exists(self.metadata_dir):
                for filename in os.listdir(self.metadata_dir):
                    if filename.endswith('.json'):
                        file_path = os.path.join(self.metadata_dir, filename)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                metadata = json.load(f)
                                if metadata.get('inspection_id') == inspection_id and metadata.get('is_active', True):
                                    photos.append(metadata)
                        except Exception:
                            continue
            
            # 업로드 시간 순으로 정렬
            photos.sort(key=lambda x: x.get('uploaded_at', ''), reverse=True)
            return photos
            
        except Exception as e:
            st.error(f"사진 조회 실패: {str(e)}")
            return []
    
    def get_photo_path(self, file_id: str, thumbnail: bool = False) -> Optional[str]:
        """사진 파일 경로를 반환합니다."""
        try:
            metadata_path = os.path.join(self.metadata_dir, f"{file_id}.json")
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                if thumbnail:
                    return os.path.join(self.thumbnail_dir, metadata['thumbnail_filename'])
                else:
                    return os.path.join(self.upload_dir, metadata['stored_filename'])
            
            return None
            
        except Exception:
            return None
    
    def delete_photo(self, file_id: str) -> bool:
        """사진을 삭제합니다."""
        try:
            metadata_path = os.path.join(self.metadata_dir, f"{file_id}.json")
            if os.path.exists(metadata_path):
                # 메타데이터 로드
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                # 파일들 삭제
                original_path = os.path.join(self.upload_dir, metadata['stored_filename'])
                thumbnail_path = os.path.join(self.thumbnail_dir, metadata['thumbnail_filename'])
                
                for path in [original_path, thumbnail_path, metadata_path]:
                    if os.path.exists(path):
                        os.remove(path)
                
                return True
            
            return False
            
        except Exception as e:
            st.error(f"사진 삭제 실패: {str(e)}")
            return False
    
    def get_storage_stats(self) -> Dict:
        """저장소 통계를 반환합니다."""
        try:
            total_files = 0
            total_size = 0
            
            for directory in [self.upload_dir, self.thumbnail_dir]:
                if os.path.exists(directory):
                    for filename in os.listdir(directory):
                        file_path = os.path.join(directory, filename)
                        if os.path.isfile(file_path):
                            total_files += 1
                            total_size += os.path.getsize(file_path)
            
            return {
                'total_files': total_files,
                'total_size': total_size,
                'total_size_mb': round(total_size / 1024 / 1024, 2)
            }
            
        except Exception:
            return {'total_files': 0, 'total_size': 0, 'total_size_mb': 0}


# 전역 인스턴스
_photo_manager = None

def get_photo_manager() -> PhotoManager:
    """PhotoManager 싱글톤 인스턴스를 반환합니다."""
    global _photo_manager
    if _photo_manager is None:
        _photo_manager = PhotoManager()
    return _photo_manager


def render_photo_upload_tab(inspection_id: str, current_user: str = ""):
    """사진 업로드 탭을 렌더링합니다."""
    manager = get_photo_manager()
    
    st.subheader("📷 사진 첨부")
    
    # 업로드 섹션
    with st.expander("🔄 새 사진 업로드", expanded=True):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_file = st.file_uploader(
                "사진을 선택하세요",
                type=['jpg', 'jpeg', 'png', 'webp'],
                help="최대 10MB까지 업로드 가능합니다."
            )
        
        with col2:
            photo_type = st.selectbox(
                "사진 유형",
                ["inspection", "defect", "equipment", "process"],
                format_func=lambda x: {
                    "inspection": "🔍 검사",
                    "defect": "⚠️ 불량",
                    "equipment": "🔧 장비",
                    "process": "⚙️ 공정"
                }.get(x, x)
            )
        
        description = st.text_area("사진 설명", placeholder="이 사진에 대한 설명을 입력하세요...")
        capture_location = st.text_input("촬영 위치", placeholder="예: 1번 라인, A구역, 상단부")
        
        if uploaded_file is not None:
            if st.button("📤 업로드", type="primary"):
                result = manager.upload_photo(
                    uploaded_file=uploaded_file,
                    inspection_id=inspection_id,
                    photo_type=photo_type,
                    description=description,
                    capture_location=capture_location,
                    uploaded_by=current_user
                )
                
                if result:
                    st.rerun()
    
    # 업로드된 사진 목록
    st.subheader("📸 업로드된 사진")
    photos = manager.get_photos(inspection_id)
    
    if photos:
        for i, photo in enumerate(photos):
            with st.expander(f"📷 {photo['original_filename']}", expanded=i < 2):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    # 썸네일 표시
                    thumbnail_path = manager.get_photo_path(photo['id'], thumbnail=True)
                    if thumbnail_path and os.path.exists(thumbnail_path):
                        st.image(thumbnail_path, use_column_width=True)
                
                with col2:
                    st.write(f"**사진 유형:** {photo.get('photo_type', 'unknown')}")
                    st.write(f"**파일 크기:** {photo.get('file_size', 0) // 1024} KB")
                    st.write(f"**해상도:** {photo.get('width', 0)} × {photo.get('height', 0)}")
                    st.write(f"**업로드 시간:** {photo.get('uploaded_at', 'unknown')}")
                    
                    if photo.get('description'):
                        st.write(f"**설명:** {photo['description']}")
                    
                    if photo.get('capture_location'):
                        st.write(f"**촬영 위치:** {photo['capture_location']}")
                    
                    # 원본 이미지 보기 버튼
                    if st.button(f"🔍 원본 보기", key=f"view_{photo['id']}"):
                        original_path = manager.get_photo_path(photo['id'], thumbnail=False)
                        if original_path and os.path.exists(original_path):
                            st.image(original_path, caption=photo['original_filename'])
                    
                    # 삭제 버튼
                    if st.button(f"🗑️ 삭제", key=f"delete_{photo['id']}", type="secondary"):
                        if manager.delete_photo(photo['id']):
                            st.success("사진이 삭제되었습니다.")
                            st.rerun()
    else:
        st.info("업로드된 사진이 없습니다.")
    
    # 저장소 통계
    with st.expander("📊 저장소 통계"):
        stats = manager.get_storage_stats()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("총 파일 수", stats['total_files'])
        with col2:
            st.metric("사용 용량", f"{stats['total_size_mb']} MB")
        with col3:
            st.metric("평균 파일 크기", f"{stats['total_size_mb'] / max(1, stats['total_files']):.1f} MB")