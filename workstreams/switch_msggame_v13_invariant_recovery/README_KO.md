# Switch v1.3 → PK `msggame` 형식 복구 580개

이 작업은 `snake7594/nobunaga-shinsei-korean-patch` v1.3의 한국어 `msggame.bin`을 PC PK 간체중문 경로에 그대로 복사하지 않고, 출처가 고정된 텍스트만 파일 전용 overlay로 복구한다. 게임 EXE, DLL, 메모리, 레지스트리와 설치된 게임 파일은 수정하지 않는다.

## 입력 고정값

- 출처 저장소: <https://github.com/snake7594/nobunaga-shinsei-korean-patch>
- v1.3 ZIP SHA-256: `F4D2563C1B32DB450165C8CCF61C6947DEA904233581036E179AFA1D6A918CC4`
- v1.1 ZIP SHA-256: `931E7C5BDECD724E44987D722E71A12161448A1A583DFFB4A569A4FA58EC46F6`
- 두 릴리스의 `MSG/JP/msggame.bin` SHA-256: `89CC6412B8548CA5CCADB6A2AB406D0EC4ED3ABCEBB8B703C4E324C0EAAB2F67`
- PC PK/SC 원본 SHA-256: `BD7B33FCC7495B855B0828C7FE4E5F7ADB2DE656A9B12E20259750F94EE665D6`

v1.3과 v1.1의 `msggame` 텍스트는 바이트 단위로 동일하다. 빌더는 두 ZIP을 읽기 전용으로 대조하며 ZIP이나 원본 게임 자원을 저장소에 추출하지 않는다.

## 선별 결과

현재 공개 `msggame` 9,318좌표와 겹치지 않는 실제 PK target 미완료 후보 2,459개를 검사했다.

| 분류 | 확정 수 | 증명 조건 |
| --- | ---: | --- |
| SC 앞뒤 공백 템플릿 복구 | 407 | 복구 뒤 printf, ESC, 제어문자, 줄바꿈, PUA, 앞뒤 공백과 구분자 역할열 일치 |
| Switch 아이콘 → PC PUA | 15 | 고정 컨트롤 아이콘 표를 적용한 뒤 같은 형식 조건 일치 |
| 기존 공개 KO 공백 변형 | 7 | 공백을 정규화한 의미열이 같고 SC 형식에 맞는 공개 변형이 정확히 하나 |
| 목록점 정규화 | 151 | 언어 문자가 아닌 `U+30FB`만 `U+00B7`로 치환하고 구분자 open/close 역할열 일치 |
| 합계 | **580** | exact target catalog 내부, 기존 overlay와 불겹침 |

나머지 1,879개는 자동 번역으로 처리하지 않는다.

- 1,877개: 내부 줄바꿈 또는 리터럴 조각 재배치가 남아 단순 좌표 이식이 위험함
- 2개: 실제 표의문자 주석이 남아 사람 번역이 필요함

이 좌표는 `review/switch_v13_pk_msggame_invariant_recovery_review.v1.json`에 `excluded`로 고정되어 있다.

## 공개 산출물

- `public/msggame_ko_switch_v13_invariant_recovery_580.v1.json`: source-free PK/SC overlay 580개
- `evidence/switch_v13_pk_msggame_invariant_recovery_evidence.v1.json`: 좌표·해시·형식 증명
- `review/switch_v13_pk_msggame_invariant_recovery_review.v1.json`: translated 580개와 제외 1,879개
- `switch_v13_pk_msggame_invariant_recovery_validation.v1.json`: 클래스별 좌표 해시, 오프라인 재구성 결과, 안전성

원문 일본어·간체중문, Switch ZIP, 완성 게임 바이너리는 공개 산출물에 포함되지 않는다.

## 재현

```powershell
python -B workstreams/switch_msggame_v13_invariant_recovery/build_switch_msggame_v13_invariant_recovery.py
python -B -m unittest workstreams.switch_msggame_v13_invariant_recovery.tests.test_switch_msggame_v13_invariant_recovery -v
```

테스트는 격리 A/B 재생성, 4개 selection class의 좌표 수·해시, exact target 교집합, 기존 overlay와의 불겹침, 1,879개 exclusion 합계, v1.3/v1.1 텍스트 동일성, 오프라인 PK 바이너리 재구성을 확인한다. progress에 이 overlay가 아직 없을 때와 정확히 한 번 등록됐을 때도 selection과 모든 산출물이 바이트 단위로 같아야 한다.
