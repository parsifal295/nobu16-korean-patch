# Switch v1.3 PK `msggame` 문맥 검토 1차 53개

직전 자동 복구에서 제외된 1,879좌표 가운데 좌표순 첫 100개를 다시 검토했다. Switch 한국어의 전체 의미와 PK JP/SC 레코드 문맥을 함께 읽고, 동적 값 사이의 문장 조각을 PK/SC 좌표에 맞게 다시 작성했다.

- 번역 확정: 53좌표
- 모호하여 유지: 47좌표
- 기존 PK `msggame` 공개 번역 9,898좌표와 겹침: 0
- 정확한 PK 대상 카탈로그 밖 좌표: 0

각 번역은 원본 SC 좌표의 줄바꿈, 앞뒤 공백, 제어 문자, printf/ESC/PUA, 괄호와 인용부호 역할을 그대로 보존한다. 단순 자동 분할은 사용하지 않았다. 동적 값 경계가 불명확하거나 기존 인접 조각과 충돌하는 좌표는 번역 수를 늘리기 위해 억지로 넣지 않고 review의 `excluded`로 남겼다.

공개 산출물은 다음과 같다.

- `public/msggame_ko_switch_v13_semantic_review_b01_53.v1.json`: source-free PK/SC overlay
- `evidence/switch_v13_pk_msggame_semantic_review_b01_evidence.v1.json`: 좌표별 해시와 구조 계약 증거
- `review/switch_v13_pk_msggame_semantic_review_b01_review.v1.json`: 첫 100좌표의 translated/excluded 판정
- `switch_v13_pk_msggame_semantic_review_b01_validation.v1.json`: 오프라인 재구성과 안전성 검증

재현 명령:

```powershell
python -X utf8 workstreams/switch_msggame_v13_human_review_b01/build_switch_msggame_v13_human_review_b01.py
python -X utf8 -m unittest workstreams.switch_msggame_v13_human_review_b01.tests.test_switch_msggame_v13_human_review_b01 -v
```

빌더는 progress에 이 overlay가 아직 없거나 정확히 한 번 등록된 두 상태를 모두 허용하되, 자기 자신은 기존 좌표 집합에서 제외한다. 어느 상태에서도 selection과 공개 산출물은 바이트 단위로 동일하다. 게임 설치 파일, EXE, DLL, 메모리, 레지스트리는 수정하지 않는다.
