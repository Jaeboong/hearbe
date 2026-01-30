# 이미지 전처리 모듈 (OCR 정확도 향상)
import cv2
import numpy as np
from PIL import Image
from typing import Union


def enhance_for_ocr(
    image_input: Union[str, np.ndarray, Image.Image],
    clip_limit: float = 2.0,
    tile_grid_size: tuple = (8, 8)
) -> np.ndarray:
    """
    OCR 정확도 향상을 위한 이미지 전처리 (Level 1: 기본)

    Args:
        image_input: 이미지 경로(str), NumPy 배열, 또는 PIL Image
        clip_limit: CLAHE 대비 제한 (기본 2.0, 높을수록 대비 강함)
        tile_grid_size: CLAHE 타일 크기 (기본 8x8)

    Returns:
        전처리된 NumPy 배열 (그레이스케일)

    처리 단계:
        1. 그레이스케일 변환 (텍스트 인식에 색상 불필요)
        2. CLAHE (Contrast Limited Adaptive Histogram Equalization)
           - 국소 영역별로 대비 향상
           - 표의 밝은/어두운 부분 모두 개선
    """
    # 1. 입력을 NumPy 배열로 변환
    if isinstance(image_input, str):
        # 파일 경로인 경우
        img = cv2.imread(image_input)
        if img is None:
            raise ValueError(f"이미지를 로드할 수 없습니다: {image_input}")
    elif isinstance(image_input, Image.Image):
        # PIL Image인 경우
        img = cv2.cvtColor(np.array(image_input), cv2.COLOR_RGB2BGR)
    elif isinstance(image_input, np.ndarray):
        # 이미 NumPy 배열인 경우
        img = image_input
    else:
        raise TypeError(f"지원하지 않는 입력 타입: {type(image_input)}")

    # 2. 그레이스케일 변환
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img

    # 3. CLAHE (Contrast Limited Adaptive Histogram Equalization) 적용
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    enhanced = clahe.apply(gray)

    return enhanced
