# Wave 50 NPC/비무장명 정적 private 후보

이 작업물은 W45 Steam PC 한국어 상태에서 시작하는 private 후보이다. 대상은 정확히 16개 레코드뿐이며, 게임 설치본에 적용하거나 Steam transaction을 수행하지 않는다.

입력과 근거는 다음으로 고정한다.

- 현재 한국어 입력: `F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msgdata.bin`, `msgev.bin` (W45 hash 고정)
- 원문 근거: pristine Steam PC JP backup의 동일 `MSG_PK\JP` 두 파일
- 보조 근거: Steam PC EN의 동일 두 파일
- 912px 검사는 현재 Steam PC 글꼴을 읽는 QA 전용이며, 번역/원문 근거로 사용하지 않는다.

Switch/SC와 작업공간 오버레이 경로는 열거나 사용하지 않는다. 빌더는 승인된 Steam PC 및 pristine PC JP backup 루트 밖의 외부 입력을 거부한다.

## 범위

- `msgdata.bin`: 405, 17197, 17235, 17352
- `msgev.bin`: 291, 292, 293, 2412, 2421, 2450, 2477, 2521, 2529, 2544, 2567, 3960

W49의 기존 `msgev` 3949, 3951, 3953, 3954, 3957은 명시적인 overlap guard로 차단하며, 이 후보에는 절대로 포함하지 않는다.

3960은 색상 태그 안에서 수동 LF가 분리된 레코드이다. 이 후보는 이름 토큰 `이노에`만 `이노우에`로 바꾸고 LF, 색상 태그, runtime token을 바꾸지 않는다. 따라서 향후 tag-LF reflow 작업은 3960과 겹칠 수 있으므로, 그 작업은 이 후보와 별도로 충돌 검토와 재검증을 해야 한다.

3956은 **명시적 hold**다. 이름만 바꾸면 첫 줄이 W45의 888px에서 936px로 늘어나 912px 제한을 넘는다. 이 후보는 3956을 UTF-16LE byte-identical로 보존한다. 3956은 이름 교정, semantic reflow, 실제 게임 QA를 하나의 검토 대상으로 묶은 후에만 별도 후보로 다룬다. 912px 예외는 허용하지 않는다.

## 검증 계약

각 레코드는 다음을 fail-closed로 검증한다.

- W45 Korean preimage와 UTF-16LE hash
- pristine PC JP / PC EN anchor 및 각각의 레코드ㆍanchor hash
- 정확한 토큰 교체 횟수와 target UTF-16LE hash
- tag, 색상 ESC, runtime/printf token, control, 수동 LF topology 불변
- 줄 수 1~3 및 모든 줄 912px 이하
- 3956 hold의 W45/이름만 바꾼 가상 target 폭(888→936px)과 candidate byte-identical 보존
- 실제 changed-ID scope, packed/raw table hash, LZ4/table round trip
- private output tree guard와 audit/manifest binding

후보 출력은 `tmp/pc_npc_name_quality_wave50_v1/candidate/` 아래에만 생성된다. Steam 적용, Git, 네트워크, 릴리스 기능은 구현하지 않는다.

## 실행

```powershell
python -B .\build_pc_npc_name_quality_wave50_v1.py build
python -B .\build_pc_npc_name_quality_wave50_v1.py verify-private
python -B -m unittest -v .\test_pc_npc_name_quality_wave50_v1.py
```
