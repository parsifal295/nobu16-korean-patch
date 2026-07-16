# Steam JP `msgev` 잔여 이벤트 Wave09

이 워크스트림은 Steam `1.1.7` 일본어 경로의 `MSG_PK/JP/msgev.bin`에서 Wave08 뒤에도 일본어로 남은, 화면에 노출되는 이벤트 텍스트를 제한된 범위로 번역한다. 라이브 게임 파일은 입력이나 출력으로 사용하지 않는다.

- 대상은 총 66개다. 기존 장면의 잔여 대사 2개와 야스케 대체 혼노지 이벤트 연속 구간 48개, 분기·조건 라벨 16개다.
- 이벤트 본문 대상은 `10959`, `10960`, `10962..11009`이며, 이미 Wave08에서 한글인 `10961`은 명시적으로 제외한다.
- 분기·조건 라벨은 `16437..16448`, `16904`, `16905`, `17456`, `17833`이다. 이벤트 선택지와 조건/해금 표시에 쓰이는 짧은 행만 포함한다.
- 입력은 pristine Steam JP `msgev.bin`과 deterministic Wave08 baseline이다. baseline packed SHA-256은 `39E8FEE6C4A7F1EB5018F01FB9446C9866E85BF13509C2CE099849E7AA3AAECD`로 먼저 고정 검증한다.
- 완성 후보 packed SHA-256은 `A8835C3520B29A076A21014E17B17D7AAABF4AC99D37D65C891415AC17BBF3F5`다. 문자열 수, 비대상 행, 불투명 테이블 메타데이터와 wrapper prefix가 변하지 않는지 확인한다.
- 기존 v1, Wave08 semantic, Wave08 source-equal contract 좌표와의 중복을 모두 차단한다. 대상 행은 Wave08 baseline에서도 pristine JP 원문과 동일해야 한다.
- 각 행은 pristine JP hash, Wave08 baseline hash, 한글 hash, 형식 불변식 hash를 공개한다. `%s`, 줄바꿈, 색상/이름 제어 토큰, 선행 전각 공백의 보존이 실패하면 빌드가 중단된다.
- 공개 overlay·trace에는 프로젝트 작성 한글, ID, SHA-256, 구조 증명만 들어간다. 일본어 원문, SC 리소스, 완전한 게임 바이너리는 추적하지 않는다.

검증과 임시 후보 생성:

```powershell
$py='C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B workstreams\msgev_steam_jp_residual_wave09\build_msgev_steam_jp_residual_wave09.py verify
& $py -B workstreams\msgev_steam_jp_residual_wave09\build_msgev_steam_jp_residual_wave09.py build --output-root tmp\msgev_steam_jp_residual_wave09_candidate
```

`build`는 명시한 `tmp` 하위에만 후보 파일을 만들며 설치된 게임 파일을 수정하지 않는다. 상위 Steam 후보 조립기는 `build_blob(stock_root)`을 호출해 이 `msgev.bin`을 Wave08 다음 단계로 합성할 수 있다.
