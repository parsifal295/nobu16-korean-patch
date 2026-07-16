# Steam JP 1.1.7 v0.9.0 후보 조립

이 작업물은 v0.8.0의 공개된 정확히 14개 파일 ZIP을 검증된 기준점으로 사용하고, 다음 두 JP 기본 리소스만 Wave 11 결과로 교체합니다.

- `MSG/JP/msggame.bin`: 기존 22,924행에 안전 잔여 270행을 더해 총 23,194행
- `MSG/JP/ev_strdata.bin`: 기존 13,045행에 안전 잔여 40행을 더해 총 13,085행

기준 ZIP과 두 Steam 원본은 모두 SHA-256으로 고정됩니다. 현재 설치된 Steam 폴더는 번역 입력으로 사용하지 않습니다. 다만 조립 전·후 14개 대상 파일과 `NOBU16.exe`·`NOBU16PK.exe`의 해시를 비교해 어떤 파일도 바뀌지 않았음을 검증합니다. 나머지 12개 파일(서울한강체가 포함된 네 폰트 경로 포함)은 v0.8.0과 바이트 단위로 같아야 하며, 후보 ZIP은 JP 경로 14개 파일만 담습니다.

`MSG_PK/JP/msgstf_ce.bin`은 크레딧 로딩 경로와 화면 검증 전까지 바꾸지 않습니다.

## 명령

```powershell
$py = 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B workstreams\steam_jp_117_candidate_v6\build_steam_jp_117_candidate_v6.py bootstrap --proposal tmp\steam_jp_117_candidate_v6_bootstrap.json
& $py -B workstreams\steam_jp_117_candidate_v6\build_steam_jp_117_candidate_v6.py verify --scratch-root tmp\steam_jp_117_candidate_v6_verify
& $py -B workstreams\steam_jp_117_candidate_v6\build_steam_jp_117_candidate_v6.py build --output-root tmp\steam_jp_117_candidate_v6_final
```

첫 명령의 결과를 `verification.v6.json`으로 검토·고정한 뒤에만 `verify`와 `build`가 성공합니다. 모든 조립은 `tmp` 아래 임시 후보본에서 이루어지며 설치 게임 파일에는 쓰지 않습니다.

## 사전 입력

- v0.8.0 공개 ZIP: `NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.8.0.zip`, SHA-256 `8167B09DE5DC56C1F195AF0A913336F552D189B0DB320C2A4F5EC863BBC58D08`
- Steam 1.1.7 원본 백업: `F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP\file_only_transaction\steam-jp-1.1.7-v0.8.0\originals` 아래 `MSG\JP\msggame.bin`, `MSG\JP\ev_strdata.bin`
- Switch v1.3 참조 ZIP: `tmp\third_party_switch_v13\NobunagaShinsei_KoreanPatch_v1.3.zip`, SHA-256 `F4D2563C1B32DB450165C8CCF61C6947DEA904233581036E179AFA1D6A918CC4`

위 입력이 없거나 해시가 다르면 조립은 실패합니다. 이 제한은 다른 버전의 Steam 파일을 1.1.7 후보본에 섞지 않기 위한 것입니다.
