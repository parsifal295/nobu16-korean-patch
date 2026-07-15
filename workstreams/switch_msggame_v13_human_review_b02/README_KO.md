# Switch v1.3 PK `msggame` 문맥 검토 B02 68개

직전 자동 복구의 제외 좌표를 정렬한 뒤 B01의 첫 100개를 건너뛰고, 101번째부터 200번째까지 정확히 100좌표를 검토했다. Switch 한국어 의미와 PK JP/SC 전체 레코드 문맥을 함께 확인하고, 좌표 경계가 확정되는 68개만 번역했다. 동적 값 경계나 인접 조각 때문에 한국어 어순이 확정되지 않는 32개는 제외했다.

- 번역 확정: 68좌표
- 모호하여 유지: 32좌표
- 기존 공개 번역과 B01을 합친 9,951좌표와 중복: 0
- 정확한 PK 대상 카탈로그 밖 좌표: 0

모든 번역은 원본 PK/SC 좌표의 줄바꿈과 앞뒤 공백, 제어 문자, printf/ESC/PUA, 괄호 및 인용부호 역할을 보존한다. 공개 JSON에는 상용 원문을 넣지 않았다.

산출물:

- `public/msggame_ko_switch_v13_semantic_review_b02_68.v1.json`
- `evidence/switch_v13_pk_msggame_semantic_review_b02_evidence.v1.json`
- `review/switch_v13_pk_msggame_semantic_review_b02_review.v1.json`
- `switch_v13_pk_msggame_semantic_review_b02_validation.v1.json`

재현 명령:

```powershell
python -X utf8 workstreams/switch_msggame_v13_human_review_b02/build_switch_msggame_v13_human_review_b02.py
python -X utf8 -m unittest workstreams.switch_msggame_v13_human_review_b02.tests.test_switch_msggame_v13_human_review_b02 -v
```

빌더는 B01이 progress에 등록되기 전후를 같은 기존 좌표 집합으로 정규화한다. B02 자신이 progress에 없거나 정확히 한 번 등록된 두 상태에서도 selection과 산출물이 동일하다. 게임 설치 파일과 루트 progress/README는 수정하지 않는다.
