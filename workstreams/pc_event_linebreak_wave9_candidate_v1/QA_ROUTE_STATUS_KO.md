# Wave9 이벤트 실게임 QA 경로 상태

이 문서는 Wave9 후보 20건의 **현재 확인 가능한 PC 실게임 QA 경로**만 기록한다. 후보 리소스를 Steam에 적용하거나, Git stage/commit, 릴리스 파일 변경을 수행하지 않는다.

## 근거와 판정 범위

사용한 근거는 다음 PC 전용 산출물이다.

- `../pc_dialogue_quality_wave5_v1/event_linebreak_qa_scene_map.json`
- `../dialogue/build_event_dialogue_batch8.py`, `batch11.py`, `batch13.py`, `batch14.py`, `batch17.py`, `batch19.py`, `batch20.py`, `batch25.py`, `batch26.py`, `batch27.py`
- 현재 PC `FLOW/ENDING_00.bsf`, `FLOW/OPENING_00.bsf`, `FLOW/REKISHI_00.bsf`, `FLOW/TUTORIAL_00.bsf`, `FLOW/TUTORIAL_01.bsf`

Switch 리소스, Switch 한국어 번역, 과거 한국어 번역은 이 경로 판정에 사용하지 않았다.

scene-map의 기존 방법과 동일하게 위 PC FLOW 5개 파일에서 20개 후보 ID의 직접 32-bit little-endian 값을 재검색했다. 직접 일치 항목은 **0건**이다. 이는 발생 조건이 존재하지 않는다는 뜻이 아니라, 정적 FLOW 검색만으로는 트리거를 입증할 수 없다는 뜻이다.

따라서 실제 이벤트 직전 세이브, 시나리오 진입 조건, 디버그 호출 경로가 산출물에 명시되지 않은 경우에는 반드시 `미해결`로 기록했다. 이벤트 이름이나 대사 내용만으로 저장·발생 조건을 추정하지 않는다.

### Wave9 후보 경로 재검증 (읽기 전용)

- `FLOW`와 `FLOW_PK`의 모든 `.bsf`를 N160 헤더의 `count`와 8-byte offset 표로 분리한 뒤, **payload 영역에서만** 후보 20개 ID의 직접 32-bit little-endian 값을 다시 찾았다. 후보별 직접 호출값은 0건이다.
- big-endian 바이트 일치는 호출 근거가 아니다. 예를 들어 `5155=0x1423`, `6662=0x1A06`, `16397=0x400D`는 N160 내부의 파일 데이터 offset으로 해석되며, `16397`은 서로 다른 `REKISHI` 엔트리의 같은 참조 필드에도 반복된다. 따라서 이벤트 ID 호출로 기록하지 않는다.
- `PARAM`/`PARAM_PK`의 little-endian 일치도 이벤트 호출이 아니라 연속된 스키마 키다. 실제로 `4552–4559`, `4654–4660`, `3939–3951`, `4283–4295`처럼 이웃 키가 연속하므로 후보 ID만으로 호출 경로를 만들 수 없다.
- 로컬 `Documents/KoeiTecmo/NOBU16/GRP`의 `autoPK01–20.n16`과 `svdPK01.n16`(총 21개), 그리고 Steam Cloud 두 프로필의 모든 `remote/*.n16`를 후보 ID의 정확한 4-byte little-/big-endian 값으로 대조했다. 후보별 이벤트 직전 저장 또는 호출 표식은 0건이다.
- `16397`은 인접 레코드 `16398–16401`의 관백·태정대신·정이대장군·사퇴하기 선택지로 인해 **엔딩 직책 선택 안내 UI**라는 장면 문맥만 확정된다. 그 UI에 들어가는 저장·발생 조건은 여전히 미확정이다.

## QA 유형

- `1장`: 해당 장면에 도달한 뒤, 대상 3줄과 메시지 박스 전체가 보이는 스크린샷 1장으로 텍스트·개행·색상 확인이 가능한 정적 항목이다.
- `최대 이름`: 런타임 이름 토큰이 있으므로, 한 번의 임의 이름 캡처만으로는 충분하지 않다. 해당 토큰이 표시할 수 있는 최장 이름 폭으로 추가 확인해야 한다.
- 모든 Base 항목은 실제 UI 컨테이너 폭이 정적으로 확정되지 않았으므로, `1장`이라도 반드시 실게임 전체 메시지 박스로 확인한다.
- 해상도를 변경했다면, 게임을 완전히 종료·재실행한 뒤 선택 해상도와 재시작 여부를 QA 기록에 남긴다.

## Base — `MSG/JP/ev_strdata.bin`

| ID | PC 이벤트/장면 레이블 | 정적 범위·앵커 | 실제 진입 경로 | QA 유형 |
| ---: | --- | --- | --- | --- |
| 4558 | `hisahide_rebuilds_shigisan_castle` | 4557–4569 (`build_event_dialogue_batch13.py`) | 미해결 | 1장 |
| 4657 | `death_of_nagano_narimasa` | 4657–4690. 나가노 나리마사의 말년 서술 시작 (`event_linebreak_qa_scene_map.json`) | 미해결. scene-map도 해당 역사 이벤트 직전 세이브/시나리오 경로가 필요하다고 명시 | 최대 이름: `[b1251]` |
| 4769 | `yoshiyori_claims_chunagon_title` | 4769–4799 (`build_event_dialogue_batch14.py`) | 미해결 | 1장 |
| 4781 | `yoshiyori_claims_chunagon_title` | 4769–4799. 아네가코지 가문·우린케·다이나곤 설명 (`event_linebreak_qa_scene_map.json`) | 미해결. scene-map도 이벤트 직전 세이브/시나리오 경로가 필요하다고 명시 | 1장 |
| 5155 | `takenaka_hanbei_seizes_inabayama` | 5137–5160 (`build_event_dialogue_batch17.py`) | 미해결 | 1장 |
| 5403 | `fall_of_nagano_and_minowa` | 5383–5411 (`build_event_dialogue_batch19.py`) | 미해결 | 1장 |
| 5492 | `salt_for_the_enemy` | 5487–5509 (`build_event_dialogue_batch20.py`) | 미해결 | 최대 이름: `[b1448]` |
| 6233 | `todo_takatora_white_mochi` | 6194–6234. 다카토라의 ‘흰 떡 셋’ 깃발 후일담 (`event_linebreak_qa_scene_map.json`) | 미해결. scene-map도 이벤트 직전 세이브/시나리오 경로가 필요하다고 명시 | 1장 |
| 6365 | `sakichi_and_three_cups_of_tea` | 6349–6372 (`build_event_dialogue_batch26.py`) | 미해결 | 1장 |
| 6401 | `ichijo_kanesada_attempts_tosa_return` | 6390–6410 (`build_event_dialogue_batch27.py`) | 미해결 | 1장 |
| 6668 | `ashikaga_yoshiaki_kyoto_return_negotiation_sequence` | 6663–6677. 교 귀환 선택지 확인 대사 (`event_linebreak_qa_scene_map.json`) | 미해결. scene-map이 정적 FLOW 검색으로 조건을 확인하지 못했다고 명시 | 1장 |
| 7475 | `tachibana_ginchiyo_munetora_marriage_discussion_sequence` | 7465–7488. 긴치요 이름 풀이 (`event_linebreak_qa_scene_map.json`) | 미해결. scene-map이 정적 FLOW 검색으로 조건을 확인하지 못했다고 명시 | 1장 |
| 9580 | PC 이벤트/FLOW/scene-map에 장면 레이블 없음 | 확인 가능한 범위 없음 | 미해결 | 1장 |
| 9585 | PC 이벤트/FLOW/scene-map에 장면 레이블 없음 | PK 9585와 같은 문장이나, 발생 경로를 입증하는 자료 없음 | 미해결 | 1장 |
| 16397 | `ending_role_selection_prompt` | 16397–16401. 엔딩 직책 선택과 ‘사퇴하기’ 안내 (`event_linebreak_qa_scene_map.json`) | 부분 확인: **엔딩 직책 선택 화면**에서 캡처 가능. 이 화면으로 진입하는 세이브/조건은 미해결 | 1장 — 안내문과 뒤 4개 선택지를 함께 캡처 |

## PK — `MSG_PK/JP/msgev.bin`

| ID | PC 이벤트/장면 레이블 | 정적 범위·앵커 | 실제 진입 경로 | QA 유형 |
| ---: | --- | --- | --- | --- |
| 3945 | `takeda_toishi_rout` | 3930–3945 (`build_event_dialogue_batch8.py`) | 미해결 | 1장 |
| 4289 | `kagetora_priesthood_disturbance` | 4280–4314 (`build_event_dialogue_batch11.py`) | 미해결 | 최대 이름: `[bs1448]`, `[bm1448]` |
| 6499 | PC 이벤트/FLOW/scene-map에 장면 레이블 없음 | 확인 가능한 범위 없음 | 미해결 | 1장 |
| 6662 | PC 이벤트/FLOW/scene-map에 장면 레이블 없음 | 확인 가능한 범위 없음 | 미해결 | 1장 |
| 9585 | PC 이벤트/FLOW/scene-map에 장면 레이블 없음 | Base 9585와 같은 문장이나, 발생 경로를 입증하는 자료 없음 | 미해결 | 1장 |

## 현재 결론

- 산출물로 확정 가능한 자동 trigger/save 경로는 0건이다.
- UI 장면 자체가 특정된 항목은 `16397`뿐이며, 이 항목도 화면 진입 세이브/발생 조건은 아직 없다.
- 런타임 이름 최대폭 QA가 필요한 항목은 `4657`, `5492`, `4289`이다.
- 나머지 17건은 장면에 도달한 뒤 정적 메시지 박스 1장으로 확인할 수 있지만, **실제 장면 진입 경로는 위 표의 상태대로 미해결**이다.
