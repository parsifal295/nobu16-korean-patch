# block 13·14 보류 항목 재감사

이 작업선은 Wave 51의 block 13·14 제외·보류 95행을 최신 Wave 97 PC
dialogue private candidate와 direct PC JP/EN/SC/TC로 다시 대조하는
**read-only** 보고서다. MSGGAME 바이너리를 만들지 않으며 Steam 설치본,
Git, 릴리스, 네트워크에는 쓰지 않는다.

## 분류 결과

- `a_static_high_confidence`: 20행
  - 실제 정적 텍스트 정정·재개행 준비 완료: 5행
    - Base/PK 13:213
    - PK 13:563, 573, 590
  - 나머지 15행은 小姓=`시동`이라는 기존 프로젝트 용어 정책이 이미
    원문과 맞는다는 정적 확인이다. `시종`으로 바꾸는 후보는 만들지 않는다.
- `b_semantic_retranslation`: 3행
  - PK 14:97, 98, 221
  - 내용이 여러 절에서 바뀌었으므로 단순 치환이 아니라 의미 재번역과 이후
    표/도움말 레이아웃 검토가 필요하다.
- `c_runtime_or_real_game_ui_evidence`: 72행
  - 02xx/0143 형태소·런타임 경로, 고정 도움말/표 폭, 또는 PC 언어권 원문 간
    조건 충돌 때문에 텍스트 후보 전에 실게임·UI·게임 규칙 근거가 필요하다.

## 핵심 판정

- PK 13:563·573: `判断を求めてくる`는 도움을 요청한다는 뜻이 아니라
  플레이어의 판단·지시를 구한다는 뜻이다. 정적 정정 문안은
  `판단을 구해 오기도 합니다.`이다.
- PK 13:590: `威風が発生する`, `敵城の寝返りは起こらない`에 맞춰
  위풍의 **발생**과 적 성의 **배반 불발**을 복원할 수 있다.
- Base/PK 13:213: `가능해\n집니다`의 어절 분리만 고치면 된다.
  의미를 줄이지 않는 3줄 문안은 공개 보고서에 기록한다.
- PK 14:97·98: `통상 보고/세력 목표 보고/소목표 보고`는 JP `具申`의
  건의 구조와, 특히 `小目標具申`의 세력 발전 소목표 의미를 잃었다.
- PK 14:221: 역사상 패배한 세력을 **플레이어가 조작**하는 경우와
  승리 시의 게임 고유 전개가 `조작되는 상황/원작 체험`으로 바뀌었다.
- PK 14:156·157: `족경대장`은 `足軽大将`과 맞지 않고, `시대장`은
  `侍大将`과 맞지 않는다. 각각 `아시가루대장`, `사무라이대장`이지만
  고정 표 폭 때문에 실제 UI 검증 뒤에만 적용한다.
- Base 14:112 및 PK 14:154–155: JP는 마지막 조건을 `知略 70`으로,
  EN/SC/TC는 `정무/POL 70`으로 적어 서로 충돌한다. 게임 조건을 확인하기
  전에는 어느 문안도 채택하지 않는다.

## 재현

```powershell
python -B -X utf8 workstreams\pc_dialogue_blocks13_14_hold_reaudit_v1\build_pc_dialogue_blocks13_14_hold_reaudit_v1.py validate
python -B -X utf8 workstreams\pc_dialogue_blocks13_14_hold_reaudit_v1\build_pc_dialogue_blocks13_14_hold_reaudit_v1.py build
python -B -X utf8 workstreams\pc_dialogue_blocks13_14_hold_reaudit_v1\test_pc_dialogue_blocks13_14_hold_reaudit_v1.py
```

공개 보고서는 [pc_dialogue_blocks13_14_hold_reaudit.v1.json](public/pc_dialogue_blocks13_14_hold_reaudit.v1.json)에 생성된다.
