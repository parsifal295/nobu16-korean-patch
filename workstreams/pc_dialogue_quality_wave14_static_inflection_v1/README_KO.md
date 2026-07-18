# Wave 14: 정적 인물 대사의 일본어 활용 명령 제거

현재 Steam PC의 인물 대사 중, 한국어 리터럴 뒤에 일본어 `01 43` 활용 명령만 남아 문장 종결이 깨질 수 있는 **정적 11개 레코드**를 보정한다. 동적 이름·조사·런타임 값이 섞인 레코드는 포함하지 않는다.

## 범위

- Base `MSG/JP/msggame.bin`: 4개
  - `6:3531`, `7:262`, `8:396`, `15:2197`
- PK `MSG_PK/JP/msggame.bin`: 7개
  - `2:349`, `6:3538`, `6:4639`, `6:4643`, `7:266`, `8:408`, `15:2227`

각 레코드는 다음을 모두 만족해야 한다.

- 현재 한국어 비문자 바이트가 정확한 `01 43 <u32>` 활용 명령들과 `05 05 05` 종결자뿐이다.
- 순정 Steam PC 일본어 레코드도 같은 활용 명령을 가진다.
- 해당 PC EN/SC/TC 레코드에는 `01 43`이 없다.
- 한국어 리터럴 안에서 문장을 완결한 뒤, 대상 `01 43`만 제거한다.
- 수동 줄바꿈은 3줄 이하로 유지하고 다른 레코드는 바꾸지 않는다.

예: `즉시 이동하겠`은 `즉시 이동하겠습니다.`로, 맨 앞 쉼표만 남던 항복 문장은 `하하하, 위험을 무릅쓰고…`로 완결한다.

## 입력·출력 고정값

| 파일 | 현재 Steam 입력 SHA-256 | 후보 출력 SHA-256 |
| --- | --- | --- |
| `MSG/JP/msggame.bin` | `C74A5D2382D809FAF3EF6A78751872C6B99DAC15FCAB21CEA73E0C904736A347` | `4D147A4AD73466E882043D8A5E47F0D4DAF37473702A8CEABAEFFBF4E76F2EB8` |
| `MSG_PK/JP/msggame.bin` | `3924ADABF69C9BA72EEBA95E4CE07A3CB8FCD716A31D8F6217ECC5FFAA7B96C5` | `BD789D1C5230159433BDB9F2FCBE4B0ABABF9D84FAD2FE1C16EED45B071CE860` |

나머지 9개 현재 Steam 텍스트 프로필 파일도 바이트 단위로 입력과 동일한지 검증한다. 빌더는 Steam에 쓰지 않고 `tmp/pc_dialogue_quality_wave14_static_inflection_v1/` 아래에만 후보를 만든다.

Switch 한국어·과거 한국어 번역본은 읽지 않는다. 근거는 순정 Steam PC 일본어와 현재 Steam PC EN/SC/TC뿐이다.

## 제외한 보류 항목

- Base `6:2169` / PK `6:2175`: 런타임 세력·인물명 뒤의 조사 및 줄폭 확인이 필요하다.
- Base `6:3506` / PK `6:3513`: 여러 종결을 재구성해야 하고 동좌표 다국어 문맥이 비어 있다.
- PK `9:1828`: 런타임 삽입 명령이 남아 있어 정적화하면 안 된다.

## 검증 및 Steam 적용

```powershell
$py = 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B workstreams\pc_dialogue_quality_wave14_static_inflection_v1\build_pc_dialogue_quality_wave14_static_inflection_v1.py hash
& $py -B -m unittest workstreams\pc_dialogue_quality_wave14_static_inflection_v1\test_pc_dialogue_quality_wave14_static_inflection_v1.py
& $py -B workstreams\pc_dialogue_quality_wave14_static_inflection_v1\build_pc_dialogue_quality_wave14_static_inflection_v1.py build
```

Steam 쓰기는 빌더와 분리한다. 게임과 공식 런처를 종료한 뒤, 공용 fail-closed 트랜잭션으로 전체 11파일 후보 프로필을 dry-run하고 적용한다.

```powershell
$root = 'F:\SteamLibrary\steamapps\common\NOBU16'
$tmp = 'F:\Games\NOBU16\KR_PATCH_WORK\tmp\pc_dialogue_quality_wave14_static_inflection_v1'
$backup = "$root\KR_PATCH_BACKUP\pc-dialogue-quality-wave14-static-inflection-v1"
& $py -B tools\pk_file_only_transaction.py plan --game-root $root --release-id pc-dialogue-quality-wave14-static-inflection-v1 --manifest "$tmp\transaction.v1.json" --candidate-root "$tmp\candidate"
& $py -B tools\pk_file_only_transaction.py dry-run --game-root $root --manifest "$tmp\transaction.v1.json" --backup-root $backup --candidate-root "$tmp\candidate"
& $py -B tools\pk_file_only_transaction.py apply --game-root $root --manifest "$tmp\transaction.v1.json" --backup-root $backup --candidate-root "$tmp\candidate" --confirm APPLY
& $py -B workstreams\pc_dialogue_quality_wave14_static_inflection_v1\build_pc_dialogue_quality_wave14_static_inflection_v1.py verify-installed
```

적용 뒤에는 11개 대사를 실제 게임에서 확인해야 한다. 특히 PK `2:349`는 수동 2줄이지만 보수적 폭 진단이 1008px이므로, 실제 대사 상자에서 자동 줄바꿈과 잘림 여부를 확인한다. 이 작업은 릴리즈를 자동으로 만들지 않는다.
