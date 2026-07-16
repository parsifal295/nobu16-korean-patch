# Steam JP 전법 독음 정정 v1

이 워크스트림은 이슈 #47의 전법 목록 독음 혼재를 고친다. 대상은 Steam `1.1.7` 일본어 경로의 `MSG_PK/JP/msgdata.bin` 하나이며, 라이브 게임 파일을 입력이나 출력으로 사용하지 않는다.

- 입력 기준은 wave08·성씨·가문 표기 정정 뒤의 `msgdata.bin`이며, packed SHA-256 `E783C492860BDC6229A3A05343635FEB05435D3751BBB2670F691F270DA484B6`을 먼저 고정 검증한다.
- 전법 독음 슬롯 `15485..15550` 중 비어 있지 않은 62개를 검증하고, 그중 라틴/병음으로 남은 정확히 10개 ID `15520, 15521, 15522, 15524..15530`만 바꾼다.
- 바꾼 독음은 `기노사이하이`, `케이스노사이`, `햐쿠세쓰후토`, `쿠로다부시`, `무소야리`, `유시노코코로자시`, `켓시노코로에`, `즈이헨류`, `텐노토키`, `다케다노아카조나에`다.
- 공개 overlay와 JP trace에는 프로젝트 작성 한글·ID·UTF-16LE SHA-256만 들어간다. 일본어 원문과 완전한 게임 바이너리는 추적하지 않는다.
- JP 원문 hash, 직전 한글 baseline hash, 62개 슬롯의 라틴 문자 부재, 비대상 텍스트/테이블 불투명 메타데이터/wrapper prefix 보존을 fail-closed로 확인한다.

검증과 임시 산출물 생성:

```powershell
$py='C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B workstreams\steam_jp_tactics_reading_hotfix_v1\build_steam_jp_tactics_reading_hotfix_v1.py verify
& $py -B workstreams\steam_jp_tactics_reading_hotfix_v1\build_steam_jp_tactics_reading_hotfix_v1.py build --output-root tmp\steam_jp_tactics_reading_hotfix_v1_candidate
```

`build` 산출물은 명시한 `tmp` 하위에만 만들며 설치된 게임 파일을 수정하지 않는다. 상위 후보 조립기는 `build_blob(stock_root)`을 호출해 이 워크스트림을 가문 표기 정정 다음 단계로 합성할 수 있다.
