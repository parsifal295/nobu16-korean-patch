# msggame PK UI 우선 번역 B04

`MSG_PK/SC/msggame.bin`의 독립 UI·도움말·시스템 메시지 250개를 한국어로 번역한 배치입니다. 기존 등록 오버레이 및 B01~B03과 좌표가 겹치지 않으며, 동적 조각 문자열은 포함하지 않습니다.

- 대상 블록: 6, 7, 8, 9, 12, 13, 14, 15, 17
- 공개 오버레이: `public/msggame_ko_pk_ui_priority_b04_250.v1.json`
- 근거 자료: `evidence/msggame_pk_ui_priority_b04_evidence.v1.json`
- 검토 목록: `review/msggame_pk_ui_priority_b04_review.v1.json`
- 검증 결과: `msggame_pk_ui_priority_b04_validation.v1.json`
- 런타임 화면 검수: 미실시

빌드:

```powershell
python -X utf8 workstreams/msggame_pk_ui_priority_b04/build_msggame_pk_ui_priority_b04.py
```

테스트:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -X utf8 -m unittest workstreams.msggame_pk_ui_priority_b04.tests.test_msggame_pk_ui_priority_b04 -v
```

이 작업 디렉터리는 공유 레지스트리, 루트 README, 실제 게임 파일을 수정하지 않습니다.
