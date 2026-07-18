# Steam JP Wave 10--12 결합 텍스트 트랜잭션 후보

Wave 9 Steam JP 11파일 프로필을 입력으로 고정하고, Wave 10·11·12의 텍스트 레코드를 한 번에 결합하는 사설 후보입니다. 이 작업공간의 Python 빌더는 후보 파일만 만들며 Steam에 쓰거나 게임을 실행하지 않습니다.

## 결합 계약

- 입력: Steam Wave 9 전체 프로필 11파일
- 실제 쓰기 대상: `MSG/JP/msggame.bin`, `MSG_PK/JP/msggame.bin` 두 파일만
- Base: Wave 12의 `13:143` 한 레코드
- PK: Wave 10 12개 + Wave 11 8개 + Wave 12 1개 = 21개 물리 레코드
- PK 레코드 중복: `0` 강제
- 나머지 9파일: 입력과 바이트 단위 동일
- 현재 `RES_JP` 폰트 및 HUD 자산은 이 트랜잭션의 수정·검증 범위가 아님

PK 세 Wave는 모두 같은 Wave 9 PK 입력에서 독립적으로 만들어졌습니다. 따라서 단독 후보 파일을 순서대로 덮어쓰지 않고, 21개 비중첩 레코드를 원본에 한 번에 재구축합니다.

| 파일 | 입력 SHA-256 | 결합 출력 SHA-256 |
| --- | --- | --- |
| `MSG/JP/msggame.bin` | `7EB3F61CE008C02BA48C191CE95E162CD0BCA76CF3E1C45482FC6CE92E6E0492` | `C74A5D2382D809FAF3EF6A78751872C6B99DAC15FCAB21CEA73E0C904736A347` |
| `MSG_PK/JP/msggame.bin` | `209B96CADE84D82810A8A79CA362DFA1B6665A8C601D3DB2C3DC0F96986E9930` | `6557733B50CBA6435FB51EC71472FF4B06A321AF92F825EAA3C531DE7722E0A6` |

전체 11파일 입력·출력 해시는 빌더가 만드는 manifest에 함께 고정됩니다. 이로써 두 대상만 쓰더라도 사전·사후 Steam 프로필 전체를 검증할 수 있습니다.

## 후보 생성 및 검증

기본 입력은 다음 Wave 9 전체 후보입니다.

`KR_PATCH_WORK/tmp/steam_jp_wave9_combined_transaction_v1/candidate-build-2`

```powershell
python KR_PATCH_WORK/workstreams/steam_jp_wave10_12_combined_transaction_v1/build_steam_jp_wave10_12_combined_transaction_v1.py verify
python KR_PATCH_WORK/workstreams/steam_jp_wave10_12_combined_transaction_v1/build_steam_jp_wave10_12_combined_transaction_v1.py build
python KR_PATCH_WORK/workstreams/steam_jp_wave10_12_combined_transaction_v1/test_steam_jp_wave10_12_combined_transaction_v1.py
```

기본 빌드 출력은 모두 다음 임시 경로 아래입니다.

`KR_PATCH_WORK/tmp/steam_jp_wave10_12_combined_transaction_v1/`

- `candidate-build-1/`: 목표 11파일 후보 트리
- `audit.v1.json`: 원문을 담지 않는 결합 레코드 감사 계약
- `build_manifest.v1.json`: writer가 검증하는 전체 프로필·2파일 쓰기 계약

기존 Wave 9의 오래된 manifest는 이 트랜잭션에서 사용하지 않습니다.

## 별도 Steam writer

`invoke_steam_jp_wave10_12_combined_transaction_v1.ps1`는 별도 명시 실행이 있어야만 동작합니다. 빌더나 테스트는 이 writer를 호출하지 않습니다.

writer의 보장:

- 적용 전 Steam 11파일 전체가 Wave 9 입력인지 검증
- 후보 manifest와 후보 11파일 전체가 결합 목표와 일치하는지 검증
- 게임 및 공식 런처 프로세스 종료 확인
- 두 변경 파일만 백업하고 각 해시를 검증
- 대상 디렉터리의 임시 파일과 `File.Replace`를 이용한 원자 교체
- 각 파일 교체 후 해시, 마지막 전체 11파일 프로필 재검증
- 적용 실패 시 기록된 파일을 역순으로 원자 복구
- `RESTORE`도 백업·상태·전체 프로필을 재검증
- `-DryRun`은 읽기 전용

예시의 `APPLY`와 `RESTORE`는 의도적으로 수동 실행용이며, 이 작업에서는 실행하지 않습니다.

```powershell
$root = 'F:\SteamLibrary\steamapps\common\NOBU16'
$tmp = 'F:\Games\NOBU16\KR_PATCH_WORK\tmp\steam_jp_wave10_12_combined_transaction_v1'
PowerShell -NoProfile -ExecutionPolicy Bypass -File `
  F:\Games\NOBU16\KR_PATCH_WORK\workstreams\steam_jp_wave10_12_combined_transaction_v1\invoke_steam_jp_wave10_12_combined_transaction_v1.ps1 `
  -Operation APPLY -SteamRoot $root -CandidateRoot "$tmp\candidate-build-1" `
  -ManifestPath "$tmp\build_manifest.v1.json" `
  -BackupRoot "$tmp\backups\manual-wave10-12" -DryRun
```

실제 적용은 `-DryRun`을 빼는 별도 사용자 결정이며, 후보 검증·백업 경로 확인·실게임 QA가 끝난 뒤에만 고려합니다.
