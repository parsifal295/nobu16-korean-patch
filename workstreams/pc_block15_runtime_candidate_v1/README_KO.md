# PC Block 15 runtime candidate v1

이 workstream은 W45 Steam PC 한국어 `msggame.bin`을 읽어 private candidate만 만드는 재감사용 빌더다. 게임 설치 파일에는 쓰지 않으며, transaction, Git, 네트워크, release 기능도 구현하지 않는다. 출력은 오직 `tmp/pc_block15_runtime_candidate_v1/candidate` 아래에만 생긴다.

허용된 원문 기준은 PC 일본어 Base `F:\Games\NOBU16\MSG\JP\msggame.bin` 및 PK backup `F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP\file_only_transaction\steam-jp-1.1.7-v0.6.0\originals\MSG_PK\JP\msggame.bin`이다. PC EN/SC/TC는 재감사 시 의미 확인 보조로만 사용했으며 빌더 입력이나 후보 바이트의 출처가 아니다.

## 포함된 literal-only 후보

- Base 15:1875:1, 15:1890:1: `마술 훈련` → `승마 훈련`
- Base 15:1899:2 및 PK 15:1929:2: `보고할 수 없` → `보고할 수 있`
- PK 15:2257:1, 15:2258:1: `다음 성을 함락했습니다:` → `를 함락시켜라`
- PK 15:2279:0: `침공할 수 있어` → `침공할 수 없어`
- Base 15:1096:3 및 PK 15:1104:3: `심증이 악화` → `인상이 악화`
- Base 15:1206:2 및 PK 15:1214:2: `심증이 이전보다 좋아졌다` → `인상이 이전보다 좋아졌다`
- Base 15:1657:0, 15:1659:0, 15:1661:0 및 PK 15:1687:0, 15:1689:0, 15:1691:0: `심증은 충분하니` → `호감은 충분하니`

15:1206/15:1214의 실제 슬롯에는 `심증이`와 `이전보다` 사이에 기존 LF가 있다. 빌더는 그 LF를 그대로 둔 채 앞 단어만 바꾸며, LF 수는 전후 동일해야 한다.

## hold

Base 15:1121:2의 `이 절연` → `의 관계가 단절되었습니다.`는 의미상 확정적이지만 후보에 쓰지 않는다. literal-only 형태로는 한 줄이 720px / EAW 30에서 1152px / EAW 48로 커진다. 이 workstream의 보수 상한 912px / EAW 38과 원본 최대 폭을 넘으며, LF를 추가하는 것은 금지되어 있으므로 `hold_width_excess`로 audit에만 남긴다.

## 보호 규칙

모든 적용/hold 행은 좌표, 대상 literal slot, 전체 레코드 SHA-256, literal별 UTF-16LE SHA-256, PC-JP 레코드 SHA-256을 pin한다. 대상 재구성은 literal 사이의 opaque span을 byte-for-byte 복사한다. 따라서 다음은 모두 불변 검증 대상이다.

- literal 개수와 manual LF 개수
- marker topology와 record terminator
- 전체 opaque bytes, `02xx` runtime token, `0143` morphology command
- 같은 줄 수, font pixel 폭, EAW 폭, fallback glyph 부재

W46의 정확한 좌표와 W48/W50/W51/static composite의 보수적 block guard에 걸리면 import 단계에서 즉시 실패한다. 이 후보는 Block 15만 사용하고 W46 Block 15 좌표와도 겹치지 않는다.

## 실행

PowerShell에서 release root를 기준으로 실행한다.

```powershell
python .\workstreams\pc_block15_runtime_candidate_v1\build_pc_block15_runtime_candidate_v1.py build
python .\workstreams\pc_block15_runtime_candidate_v1\build_pc_block15_runtime_candidate_v1.py verify-private
$env:PYTHONDONTWRITEBYTECODE = '1'
python -m unittest .\workstreams\pc_block15_runtime_candidate_v1\test_pc_block15_runtime_candidate_v1.py
python .\workstreams\pc_block15_runtime_candidate_v1\build_pc_block15_runtime_candidate_v1.py diff-check
```

`audit.v1.json`에는 각 행의 current/PC-JP/proposed record 구조, runtime token, 0143 command, LF, pixel/EAW 폭과 hold 판정이 기록된다. `candidate_manifest.v1.json`은 적용 17행과 hold 1행을 분리해 기록한다.

## 실게임 QA는 아직 필요함

이 후보는 실제 게임에 적용하거나 실행하지 않는다. 별도 승인된 적용 절차가 생긴 뒤에는 17개 적용 행의 해당 화면·이벤트를 실게임에서 확인해야 한다. 해상도를 바꾼 뒤 wheel, button, title, banner, tutorial 이미지 또는 텍스트를 판정할 때는 반드시 `NOBU16PK.exe`를 완전히 종료하고 재실행한 뒤 확인한다. QA 결과마다 선택한 해상도와 완전 종료·재실행 완료 여부를 함께 기록한다.
