# Switch v1.3 PK `msggame` 문맥 검토 B03 130개

직전 자동 복구에서 제외된 1,879좌표 가운데 좌표순 201번째부터 350번째까지 150좌표를 검토했다. Switch 한국어 의미와 PK JP/SC 레코드 전체 문맥을 함께 읽고, 공식 SC 경로가 동적 값을 배치하는 순서에 맞춰 130좌표를 다시 작성했다.

- 번역 확정: 130좌표
- 동적 값 경계 때문에 제외: 20좌표
- B02까지의 공개 번역 10,019좌표와 중복: 0
- 정확한 PK 대상 카탈로그 밖 좌표: 0
- B03 등록 후 `msggame` 예상 합계: 10,149 / 16,482
- 남은 Switch 문맥 검토 후보: 1,628좌표

모든 번역은 원본 PK/SC 좌표의 줄바꿈, 앞뒤 공백, 제어 문자, printf/ESC/PUA, 괄호와 인용부호 역할을 보존한다. SC가 JP와 다른 위치에 동적 값을 놓는 레코드는 Switch 조각을 기계적으로 자르지 않고 SC 레코드 문맥에 맞게 고쳤다. 단일 좌표만으로 한국어 어순을 보장할 수 없는 20좌표는 번역 수를 늘리기 위해 억지로 넣지 않았다.

공개 산출물:

- `public/msggame_ko_switch_v13_semantic_review_b03_130.v1.json`
- `evidence/switch_v13_pk_msggame_semantic_review_b03_evidence.v1.json`
- `review/switch_v13_pk_msggame_semantic_review_b03_review.v1.json`
- `switch_v13_pk_msggame_semantic_review_b03_validation.v1.json`

재현 명령:

```powershell
python -X utf8 workstreams/switch_msggame_v13_human_review_b03/build_switch_msggame_v13_human_review_b03.py
python -X utf8 -m unittest workstreams.switch_msggame_v13_human_review_b03.tests.test_switch_msggame_v13_human_review_b03 -v
```

빌더는 B02까지의 정확한 predecessor prefix를 고정한다. 이후 B03 자신이나 후속 overlay가 progress에 추가되어도 selection 입력으로 되먹임하지 않으며, 모든 현재 overlay와 좌표 충돌만 별도로 검사한다. 공개 JSON에는 상용 원문이 없고 게임 설치 파일, EXE, DLL, 메모리, 레지스트리와 루트 progress/README는 수정하지 않는다.
