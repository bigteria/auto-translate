# 데이터 전처리 지침서 (SOP)

이 지침서는 자동번역기 프로젝트의 지식 베이스(Knowledge Base)를 구축하기 위한 데이터 전처리 과정을 설명합니다.

## 1. 개요
기존 번역 자산(엑셀 파일)을 분석하여 시맨틱 캐싱 및 RAG(Retrieval-Augmented Generation)에 사용할 수 있는 JSON 형식으로 변환합니다.

## 2. 입력 데이터 구조
- **파일명**: `Weverse Global_공지문 (2026 ver.).xlsx`
- **형식**: 여러 시트로 구성된 엑셀 파일
- **핵심 컬럼**: 국문(KO), 영문(EN), 일문(JA), 중문(ZH) 번역 쌍

## 3. 실행 방법
`execution/preprocess_kb.py` 스크립트를 실행합니다.
```bash
python execution/preprocess_kb.py
```

## 4. 처리 로직
1. 엑셀 파일의 모든 시트를 순회합니다.
2. "국문" 키워드가 포함된 헤더 행을 찾습니다.
3. 해당 행 이후의 데이터를 읽어 KO, EN, JA, ZH 번역 쌍을 추출합니다.
4. 빈 값이나 불필요한 공백을 제거합니다.
5. `.tmp/kb_data.json` 파일로 저장합니다.

## 5. 결과물
- **경로**: `.tmp/kb_data.json`
- **구조**: `[{"ko": "...", "en": "...", "ja": "...", "zh": "...", "source": "..."}, ...]`
