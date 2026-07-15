# PK 이벤트 문장 직접 번역 6차

`MSG_PK/SC/msgev.bin`에서 batch05 뒤에 남은 안전 의미 문자열 260개를
모두 직접 한국어로 번역한 파일 전용 작업 단위다. 공유 진행률·루트 README·
설치 게임 파일은 수정하지 않는다.

## 범위

- 이전 누적 번역 예상: 12,405 / 12,906
- 이번 직접 번역: 260개
- 적용 후 누적 예상: 12,665 / 12,906
- 적용 후 미점유: 241개
- 미점유 241개: 번역 대상이 아닌 구조 보존 행 전부
- 선택 ID 범위: 10,786~17,879
- 신규 구조 제외: 98개
  - 내부 ASCII 키 62개
  - 런타임 인물 대괄호 토큰 20개
  - 순수 printf 자리표시자 15개
  - 구두점 전용 1개
- 누적 구조 제외: 241개

batch05 오버레이는 루트 진행률 등록 여부와 무관하게 고정 SHA-256으로 정확히
한 번만 선행 점유에 포함한다. batch05 미등록·등록, batch06 자기 등록 및
후속 등록 상태에서도 선택과 산출 바이트가 바뀌지 않도록 검증한다.

## 산출물

- `public/msgev_ko_pk_native_batch06_260.v1.json`
- `evidence/msgev_pk_native_batch06_alignment.v1.json`
- `review/msgev_pk_native_batch06_review.v1.json`
- `validation.v1.json`
- `translations.py`

오버레이 SHA-256:
`94DAF36792E1BCAC12DDB5658DA91785B487D825939E2D7C94D381751C2D0BFF`

선택 ID SHA-256:
`F2372A6D2D9623486D3C1D48B1F03687604718A279C6F43FF22C2F0E6DD9E477`

재구축 후보 SHA-256:
`A7009A4B252ADDFCEEAB34947C06E8B76462E8831EF7A6B6AEE95D0FFFF2B550`

## 재현 및 검증

```powershell
python -B workstreams/msgev_pk_native_batch06/build_msgev_pk_native_batch06.py
python -B -m unittest discover -s workstreams/msgev_pk_native_batch06/tests -p "test_*.py" -v
```

13개 테스트가 선택 완전성, 선행 오버레이와 ID 중복 0건, 공식 PK SC 원문
해시, ESC·개행·printf 계약, 사용자 대괄호 토큰 제외, 한자·가나·NUL 비포함,
반복 다국어 원문 번역 일관성, 비대상 행 무변경, 격리 A/B 재현성을 검증한다.
