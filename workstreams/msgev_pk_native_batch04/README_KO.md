# PK 이벤트 문장 직접 번역 4차

`MSG_PK/SC/msgev.bin`의 정확한 번역 대상 중 batch03 다음의 안전한 의미 문장
175개를 파일 전용 한국어 오버레이로 작성한 작업 단위다. 루트 README, 진행률
카탈로그, 게임 설치본과 글꼴은 이 작업에서 수정하지 않는다.

## 범위

- 이전 누적 번역 대상 점유: 11,930 / 12,906
- 이번 번역: 175개
- 적용 후 누적 예상: 12,105 / 12,906
- 적용 후 잔여 예상: 801개
- 선택 ID: 10,292~10,469
- 런타임 동적 치환 보존: 10,359, 10,367
- 누적 안전 제외: 138개

batch03 오버레이는 루트 진행률 등록 여부와 무관하게 정확한 해시로 한 번만
선행 점유에 포함한다. batch03 미등록, batch03 등록, batch04 자기 등록 및
후속 오버레이 등록 상태에서 선택과 산출물의 결정성이 유지된다.

## 산출물

- `public/msgev_ko_pk_native_batch04_175.v1.json`: 한국어 175개 오버레이
- `evidence/msgev_pk_native_batch04_alignment.v1.json`: 다국어 원문 해시와 선택 근거
- `review/msgev_pk_native_batch04_review.v1.json`: 번역·제외 검토 상태
- `validation.v1.json`: 재구축, 결정성, 안전성 검증 결과
- `translations.py`: 한국어 번역표

오버레이 SHA-256:
`90C1220FC4D40F218C70A01813B0A993AA61C365DC49A2649592528F0AD2F4BA`

재구축 후보 SHA-256:
`0222E804BA0A92F2D944957B179A1A736ABEBE2B542AAFB43F52F80A4712B88B`

선택 ID SHA-256:
`E7B57EC218015B8622FCB539F22D24AC678BDB7CA3B2A65AA01FB596D3419A37`

## 재현과 검증

```powershell
python -B workstreams/msgev_pk_native_batch04/build_msgev_pk_native_batch04.py
python -B -m unittest discover -s workstreams/msgev_pk_native_batch04/tests -p "test_*.py" -v
```

12개 테스트가 ESC 순서, 줄바꿈, 사용자 정의 토큰, 한글 유효성, 번역 대상
멤버십, 선행 오버레이와의 ID 및 SC 원문 해시 중복 0건, 비선택 행 보존,
원문 문자 비포함, 격리 A/B 재현 빌드를 검증한다.
