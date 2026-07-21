# Wave 98 — block 13/14 정적 문구 정정

이 작업은 최신 Wave 97 private candidate만 한국어 입력으로 사용해, block 13/14의
정적 MSGGAME 문구 다섯 literal을 교정한다. 후보 산출물은
`tmp/pc_dialogue_quality_wave98_blocks13_14_static_v1/candidate/` 아래에만 생성한다.
Steam 게임 파일, Git, 네트워크, 릴리스 작업은 이 작업에 포함하지 않는다.

## 대상

- `MSG/JP/msggame.bin` — `13:213` (1 literal)
- `MSG_PK/JP/msggame.bin` — `13:213`, `13:563`, `13:573`, `13:590` (각 1 literal)

따라서 `13:213`이 Base와 PK에 각각 존재하더라도 실제 변경 literal 수는 **총 5개**다.
모든 대상은 marker topology, opaque span, 제어 코드, 종료 코드와 literal slot 수를
그대로 보존한다.

## 레이아웃 계약

### Base/PK `13:213`

이 행은 fixed person-dialogue 계약을 적용한다.

- 원본 G1N advance: 전각 48px / 반각 24px
- 허용 폭: 한 줄 888px 이하
- 최대 줄 수: 3줄
- 대상 raw G1N 폭: `768 / 672 / 720px` — 모두 통과

`가능해\n집니다`처럼 한국어 어절을 끊던 배치를 없애고, 문장 축약 없이 세 줄로
재배치한다.

### PK `13:563`, `13:573`, `13:590`

이 세 행은 합전·공성전의 다문장 튜토리얼/도움말 literal이다. 원본 및 현재 레코드의
수동 줄 수와 빈 줄 위치를 그대로 보존하며, fixed person-dialogue의 3줄/888px 계약을
이식하지 않는다.

- `13:563`, `13:573`: 4줄, 2번째 줄은 빈 줄
- `13:590`: 8줄, 6번째 줄은 빈 줄

이 세 행은 Steam 적용 전에 실제 게임 UI에서 별도 위젯의 줄바꿈·스크롤·잘림을
확인해야 한다. audit에는 각 줄의 표시 문자열, raw G1N 폭, 전각/반각 수, 888px 초과
여부를 기록하지만, 초과는 fixed-person 실패가 아니라 별도 위젯 QA 경고로 기록한다.

## 번역 정정

- `13:213`: 군 개발이 진행되면 더 효과가 큰 성하 시설의 건설이 가능해진다는 뜻과
  한국어 어절을 복원했다.
- `13:563`, `13:573`: `判断を求めてくる` / “request your commands”를 단순한 도움
  요청이 아니라 플레이어의 **판단을 구해 오는** 것으로 바로잡았다.
- `13:590`: `威風が発生する`, `敵城の寝返りは起こらない` 및 방위 거점의 확산 차단을
  원문 의미대로 복원했다.

## 검증

```powershell
python -B -X utf8 .\workstreams\pc_dialogue_quality_wave98_blocks13_14_static_v1\build_pc_dialogue_quality_wave98_blocks13_14_static_v1.py build
python -B -X utf8 .\workstreams\pc_dialogue_quality_wave98_blocks13_14_static_v1\build_pc_dialogue_quality_wave98_blocks13_14_static_v1.py verify-private
python -B -X utf8 .\workstreams\pc_dialogue_quality_wave98_blocks13_14_static_v1\test_pc_dialogue_quality_wave98_blocks13_14_static_v1.py
```

`audit.v1.json`에는 direct PC JP/EN/SC/TC 근거와 줄별 폭 보고서를,
`build_manifest.v1.json`에는 Wave 97 입력 및 candidate 출력 SHA-256을 기록한다.
