# 나만의 용돈 기입장 (Budget App)

이 프로젝트는 파이썬 파일 입출력, 제너레이터, 데코레이터 등을 활용하여 만든 터미널 기반의 가계부 애플리케이션입니다.

## 실행 방법
```bash
python -m budget_app <command> [options]
```

## 저장 파일 위치 및 형식
- 기본 저장 폴더: `./data/` (`--data-dir` 옵션으로 변경 가능)
- `transactions.jsonl`: 거래 내역 (JSONL 포맷)
- `categories.jsonl`: 카테고리
- `budgets.jsonl`: 월별 예산

## 주요 명령 예시
- **거래 추가**: `python -m budget_app add` (대화형)
- **거래 목록**: `python -m budget_app list --limit 5`
- **검색**: `python -m budget_app search --category food --from 2024-01-01`
- **카테고리 추가**: `python -m budget_app category add food`
- **요약**: `python -m budget_app summary --month 2024-01`
- **예산 설정**: `python -m budget_app budget set --month 2024-01 --amount 500000`

## import/export CSV 스키마
| column | required | 설명 |
| --- | --- | --- |
| date | Y | YYYY-MM-DD |
| type | Y | income / expense |
| category | Y | 등록된 카테고리 |
| amount | Y | 양수 정수 |
| memo | N | 문자열 |
| tags | N | 쉼표(,) 구분 문자열 |
