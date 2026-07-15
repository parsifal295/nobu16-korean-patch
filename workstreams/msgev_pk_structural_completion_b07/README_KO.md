# PK 이벤트 구조 항목 완료 7차

`MSG_PK/SC/msgev.bin`의 정확한 번역 대상 카탈로그에 남아 있던 구조 항목
241개를 전수 분류하고 `reviewed` 상태로 종결하는 파일 전용 작업 단위다.
공유 진행률·루트 README·설치 게임 파일은 수정하지 않는다.

## 결과

- 이전 완료: 12,665 / 12,906
- 이번 구조 검토: 241개
- 적용 후 완료: 12,906 / 12,906
- 정확한 대상 카탈로그 잔여: 0개
- 차단: 0개

분류 결과는 다음과 같다.

- 219개: ASCII 내부 키, 동적 토큰, printf 자리표시자, 구두점 등을 원문과
  바이트 동일하게 보존
- 22개: 동적 인물 토큰이 포함된 서술문을 한국어로 번역하면서 ESC 순서,
  대괄호 토큰, 개행, printf 및 제어문자 계약을 정확히 보존

공개 오버레이·증거·검토·검증 파일에는 중국어·일본어 원문이나 완성 게임
리소스가 포함되지 않는다. 화면 검수는 별도 단계이며
`runtime_screen_reviewed_count=0`으로 명시한다.

## 산출물

- `public/msgev_ko_pk_structural_completion_b07_241.v1.json`
- `evidence/msgev_pk_structural_completion_b07_evidence.v1.json`
- `review/msgev_pk_structural_completion_b07_review.v1.json`
- `validation.v1.json`
- `translations.py`

오버레이 SHA-256:
`4FB377A64306BCE929E22A4271E3AB95FEBF1A937B433C3807C4A9816440550F`

구조 항목 ID SHA-256:
`A58E26CCD1D7DD8F7505B0134FD3354E7001B6C91B27A1D7011EBAD29AA4D2B0`

재구축 후보 SHA-256:
`D62E438F749C1019CC8CD872DB8CEDD675883B00F55C9F5F25127E6C07F95A5D`

## 재현 및 검증

```powershell
python -B workstreams/msgev_pk_structural_completion_b07/build_msgev_pk_structural_completion_b07.py
python -B -m unittest discover -s workstreams/msgev_pk_structural_completion_b07/tests -p "test_*.py" -v
```

12개 테스트가 241개 완전 분류, 선행 점유와 중복 0건, 219개 바이트 동일
보존, 22개 동적 런타임 계약, `reviewed` 상태, 공개 산출물 원문 문자·NUL
비포함, 대상 잔여 0개, 등록 전후 재현성 및 격리 재구축을 검증한다.
