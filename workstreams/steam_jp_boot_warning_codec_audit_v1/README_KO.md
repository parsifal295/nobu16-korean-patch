# Steam JP 부트 경고 이미지 `format 0x01` 코덱 감사 v1

이 작업은 Steam 1.1.7 일본어 경로의 `RES_JP/res_lang.bin /1`만 읽어서 조사한다. 이 번들은 게임 시작 직후 표시되는 저작권·불법 배포 경고 계열 이미지 여섯 장으로 구성되어 있다.

패치 파일, PNG, G1T, LZ4 wrapper, Switch 원본, SC 원본은 이 디렉터리에 넣지 않는다. 게임 설치본도 쓰지 않는다.

## 결론

PC Steam JP에서 관찰된 좁은 범위의 `GT1G0600` `format 0x01`은 다음 조건에서는 선형 행 우선 `RGBA8`이다.

| 조건 | 관찰값 |
| --- | --- |
| G1T platform | `0x0A` (PC) |
| texture 수 | 1 |
| mip 수 | 1 (`packed_info = 0x10`) |
| extra header | version `0x10`, length `12` |
| pixel payload | 정확히 `width × height × 4` bytes |
| canvas | `2048×2048` 3장, `4096×4096` 3장 |
| pixel 순서 | linear row-major `RGBA8` |

`RGBA8`로 사적 미리보기를 만든 뒤 slot 0의 일본어 `ご注意` 경고와 본문이 읽히는 것을 확인했다. R/B를 바꾼 비교본은 색 표현이 틀린다. 이 결론은 **이 PC JP 변형에만 적용**되며, 일반 G1T `0x01`, Switch, SC의 포맷 규격이라고 주장하지 않는다.

## 안전 경계

- Steam JP 설치 파일은 SHA-256 전후 비교로 읽기만 한다.
- Switch/SC의 raw container·wrapper·G1T·PNG를 PC JP에 복사하지 않는다.
- 이 감사는 decoder/identity proof만 제공하고, 게임 파일을 쓰는 mutator나 후보 패치를 제공하지 않는다.
- 사적 PNG는 `KR_PATCH_WORK/tmp/steam_jp_boot_warning_codec_audit_v1/` 아래에만 생성하며 Git에 넣지 않는다.
- 메모리 패치, DLL 주입, 후킹, EXE/레지스트리 변경을 사용하지 않는다.

## 실행

```powershell
$py = 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'

& $py -B workstreams\steam_jp_boot_warning_codec_audit_v1\build_steam_jp_boot_warning_codec_audit_v1.py audit `
  --game-root F:\SteamLibrary\steamapps\common\NOBU16

& $py -B workstreams\steam_jp_boot_warning_codec_audit_v1\build_steam_jp_boot_warning_codec_audit_v1.py verify

# ignored tmp 안에서만 생성된다.
& $py -B workstreams\steam_jp_boot_warning_codec_audit_v1\build_steam_jp_boot_warning_codec_audit_v1.py private-preview

& $py -B -m unittest workstreams\steam_jp_boot_warning_codec_audit_v1\test_steam_jp_boot_warning_codec_audit_v1.py -q
```

## 다음 단계 게이트

1. 경고 문구의 한국어 번역·법적 문안을 확정한다.
2. 별도 후보 빌더에서 각 PC canvas 크기에 맞게 RGBA8로 렌더한다.
3. G1T header, wrapper prefix, 비대상 nested/outer 바이트 보존과 여섯 slot의 decode/encode 검증을 모두 통과시킨다.
4. 게임을 종료한 상태에서 후보만 구조 검증하고 시작 경고 화면을 캡처한다.
5. 그 뒤에만 사전·사후 SHA-256과 복원 백업을 가진 파일 전용 트랜잭션으로 적용을 검토한다.

이 workstream 자체는 배포물·게임 적용물·릴리즈 후보가 아니다.
