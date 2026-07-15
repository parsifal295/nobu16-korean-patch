# PK 이벤트 문장 직접 번역 5차

`MSG_PK/SC/msgev.bin`의 batch04 다음 안전 의미 행 300개를 직접 한국어로
번역한 파일 전용 작업 단위다. 루트 README·진행률 카탈로그·게임 설치본·글꼴과
기존 workstream은 수정하지 않는다.

## 범위

- 이전 누적 번역 대상 점유: 12,105 / 12,906
- 이번 직접 번역: 300개
- 적용 후 누적 예상: 12,405 / 12,906
- 적용 후 잔여 예상: 501개
- 선택 ID 범위: 10,470~10,785
- 이번 구두점 전용 안전 제외: 10,703, 10,708, 10,709, 10,716, 10,764
- 누적 안전 제외: 143개

batch04 오버레이는 루트 진행률 등록 여부와 무관하게 고정 SHA-256으로 한 번만
선행 점유에 포함한다. batch04 미등록·등록, batch05 자기 등록과 후속 등록
상태에서도 선택 및 산출물 바이트가 바뀌지 않는다.

## 산출물

- `public/msgev_ko_pk_native_batch05_300.v1.json`
- `evidence/msgev_pk_native_batch05_alignment.v1.json`
- `review/msgev_pk_native_batch05_review.v1.json`
- `validation.v1.json`
- `translations.py`

오버레이 SHA-256:
`CED113C16D01202BEB63B7F66B62BDFA8478149313C2A20A539FB2B4EF599EC2`

재구축 후보 SHA-256:
`319A3B31D11B5155B4E248CB19D9629DC19061E673480AF52D03ADBA5F29CF1F`

선택 ID SHA-256:
`99F42EAAD16A336A384292221A40ADA1457413D550A50C4B3F7D906335E7E0BD`

## 재현과 검증

```powershell
python -B workstreams/msgev_pk_native_batch05/build_msgev_pk_native_batch05.py
python -B -m unittest discover -s workstreams/msgev_pk_native_batch05/tests -p "test_*.py" -v
```

12개 테스트가 선행 오버레이와의 ID 중복 0건, 각 ID의 고정 SC 원문 해시,
ESC 순서, 줄바꿈, 사용자 정의 토큰, 한글 유효성, 비선택 행 보존, 원문 문자와
NUL 비포함, 격리 A/B 결정적 재현을 검증한다.
