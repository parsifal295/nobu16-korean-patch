# Steam JP 이벤트 가문 표기 정규화 v1

이 워크스트림은 이슈 #46의 `MSG_PK/JP/msgdata.bin` 이벤트 목록 가문 표기만 보정한다.

- 입력은 Steam 1.1.7의 깨끗한 JP `msgdata.bin`과, 현행 wave08+성씨 보정 기준 후보뿐이다.
- 기준 후보의 packed/raw 해시와 각 대상의 JP·기준 한글 해시를 모두 고정한다.
- 이벤트 가문 영역 ID `14519..14766` 중 끝 글자가 정확히 `가`인 159개만 끝 `가`를 ` 가문`으로 치환한다.
- 이미 정상인 `14542`(`오다 가문`), 비가문 `14603`, 별도 명명 가문 `14767..14776`, 독음 영역 `14777..15034`는 변경하지 않는다.
- 예: `14692`는 `아라키가`에서 `아라키 가문`으로 바뀐다.

공개 overlay에는 프로젝트 작성 한글, ID, SHA-256만 있으며 원문 JP 텍스트나 완전한 게임 바이너리는 포함하지 않는다. `build` 산출물은 `tmp` 아래에서만 만들며, 설치 게임 파일을 수정하지 않는다.

```powershell
$py='C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B workstreams\steam_jp_clan_label_normalization_v1\build_steam_jp_clan_label_normalization_v1.py verify
```

후속 후보 통합은 `build_blob(stock_root)`를 호출해 현행 wave08+성씨 `msgdata.bin`을 기준으로 한 바이트와 메타데이터를 얻는다.
