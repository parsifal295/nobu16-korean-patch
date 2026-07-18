# Steam PC Wave9 결합 트랜잭션

이 작업 스트림은 Wave8 11파일 프로필을 정확히 확인한 뒤 Wave9 후보 세
리소스를 하나의 완전한 후보 프로필로 결합한다. 빌더는 Steam 게임 폴더에
쓰지 않고 이 작업 스트림의 tmp 아래에만 후보와 매니페스트를 만든다.

변경 경로는 정확히 다음 세 개다.

- MSG/JP/ev_strdata.bin
- MSG_PK/JP/msgev.bin
- MSG_PK/JP/msggame.bin

나머지 여덟 경로는 Wave8 해시를 그대로 유지한다.

## 입력과 목표

입력은 Wave8 전체 프로필 11개 해시다. 결합 목표의 변경 해시는 다음과 같다.

| 경로 | Wave8 입력 | Wave9 목표 |
| --- | --- | --- |
| MSG/JP/ev_strdata.bin | 25D9C029...0D5834 | 3A7BE17B...657A22 |
| MSG_PK/JP/msgev.bin | 1880A805...AB55C5 | 73DEC80A...2CB8F3 |
| MSG_PK/JP/msggame.bin | 454A18B0...E24A32 | 209B96CA...6E9930 |

결합 빌더는 다음 두 기존 후보의 매니페스트, 후보 파일, 입력 계약을 모두
검증한다.

- pc_dialogue_runtime_wave9_candidate_v1: PK msggame 전체 11파일 후보
- pc_event_linebreak_wave9_candidate_v1: Base ev_strdata와 PK msgev 후보

## tmp 전용 후보 생성

    $py='C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
    & $py -B workstreams\steam_jp_wave9_combined_transaction_v1\build_steam_jp_wave9_combined_transaction_v1.py verify
    & $py -B workstreams\steam_jp_wave9_combined_transaction_v1\build_steam_jp_wave9_combined_transaction_v1.py build

생성 위치:

- tmp/steam_jp_wave9_combined_transaction_v1/candidate-build-1
- tmp/steam_jp_wave9_combined_transaction_v1/build_manifest.v1.json

## 별도 Steam 트랜잭션 스크립트

invoke_steam_jp_wave9_combined_transaction_v1.ps1은 후보 빌더와 분리된
명시적 writer다. APPLY와 RESTORE 모두 다음 안전 조건을 강제한다.

- Steam 11파일 전체 프로필이 정확히 Wave8 입력 또는 Wave9 목표인지 확인
- 게임과 공식 런처 프로세스가 모두 종료됐는지 확인
- 첫 교체 전에 세 변경 파일 전부를 백업하고 해시 확인
- 같은 디렉터리의 임시 파일과 File.Replace로 원자적 교체
- 중간 실패 시 이미 쓴 경로를 역순으로 즉시 롤백
- 백업 상태와 입력/목표 해시를 다시 확인하는 RESTORE
- DryRun에서는 Steam이나 백업 경로에 쓰지 않음

실제 APPLY는 이 작업 스트림에서 실행하지 않았다. 실제 적용 전에는
실게임 QA와 명시적 승인 후에만 아래 형식으로 호출한다.

    powershell -NoProfile -ExecutionPolicy Bypass -File workstreams\steam_jp_wave9_combined_transaction_v1\invoke_steam_jp_wave9_combined_transaction_v1.ps1 -Operation APPLY -SteamRoot F:\SteamLibrary\steamapps\common\NOBU16 -CandidateRoot F:\Games\NOBU16\KR_PATCH_WORK\tmp\steam_jp_wave9_combined_transaction_v1\candidate-build-1 -ManifestPath F:\Games\NOBU16\KR_PATCH_WORK\tmp\steam_jp_wave9_combined_transaction_v1\build_manifest.v1.json -BackupRoot F:\Games\NOBU16\KR_PATCH_WORK\tmp\steam_jp_wave9_combined_transaction_v1\backups\wave9-apply

## 안전한 dry-run

DryRun 검증은 실제 Steam 경로가 아니라 Wave8 비공개 후보 사본을 SteamRoot로
사용한다. 그래서 전체 입력 프로필과 후보 매니페스트를 검증하지만 파일이나
백업 폴더를 전혀 만들지 않는다.

    powershell -NoProfile -ExecutionPolicy Bypass -File workstreams\steam_jp_wave9_combined_transaction_v1\invoke_steam_jp_wave9_combined_transaction_v1.ps1 -Operation APPLY -SteamRoot F:\Games\NOBU16\KR_PATCH_WORK\tmp\pc_dialogue_quality_wave8_candidate_v1\candidate-build-1 -CandidateRoot F:\Games\NOBU16\KR_PATCH_WORK\tmp\steam_jp_wave9_combined_transaction_v1\candidate-build-1 -ManifestPath F:\Games\NOBU16\KR_PATCH_WORK\tmp\steam_jp_wave9_combined_transaction_v1\build_manifest.v1.json -BackupRoot F:\Games\NOBU16\KR_PATCH_WORK\tmp\steam_jp_wave9_combined_transaction_v1\backups\dry-run-wave8-input -DryRun
