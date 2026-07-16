# Steam JP 1.1.7 v0.10.0 화면 제목 이미지 후보

이 workstream은 Steam 1.1.7 일본어(`JP`) 경로의 v0.9.0 정확한 14파일 ZIP과
manifest를 바이트 단위로 고정한 뒤, `RES_JP/res_lang.bin` 하나만 화면 제목 이미지
후보로 교체하여 **오프라인 v0.10.0 후보**를 조립한다.

교체 파일은 `RES_JP/res_lang.bin`의 `/3/0..107` 제목 슬롯 108개를 PC 형식으로
재구성한 후보이며, `/3/108`, `/3/109`와 나머지 outer entry 보존 검증을 통과한
입력만 허용한다. 나머지 13파일은 v0.9.0 ZIP의 payload hash와 정확히 일치해야 한다.

## 고정 입력과 범위

- v0.9.0 정확한 14파일 ZIP
  - `NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.9.0.zip`
  - SHA-256: `1BCC92A3CD7025D307AF9B193BDDD8F1448451024630C8414FC218F0C49FE829`
- v0.9.0 manifest (`candidate_manifest.v6.json`)
  - SHA-256: `5D93C83B817E67408A9F8A160B8437E37DE4EF332AB7C76D69855D2F705A8F3B`
- 제목 이미지 후보 `RES_JP/res_lang.bin`
  - SHA-256: `D045B42BC3D4A4D4C501C5A0E010698AAE95AAE227775306A1272D5259E0888B`
- 결과 ZIP에는 JP 경로의 14파일만 들어간다. PNG, 보고서, Switch 컨테이너,
  `exefs`/`romfs`, 실행 파일은 포함할 수 없다.

기본 v0.9 입력은 다음의 **상속 ACL 공유 입력 버킷**이다. elevated 검증과 일반
검증이 같은 고정 입력을 읽도록, owner-only 임시 후보 디렉터리를 기본값으로 쓰지
않는다.

```text
tmp\steam_jp_117_image_candidate_v1_inputs\v0.9.0\candidate_manifest.v6.json
tmp\steam_jp_117_image_candidate_v1_inputs\v0.9.0\NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.9.0.zip
```

두 파일은 위 SHA-256과 파일명까지 일치해야 하며, ZIP·manifest·제목 이미지 입력은
서로 다른 일반 파일이어야 한다. 심볼릭 링크나 바뀐 ZIP은 즉시 거부한다. 다른 위치의
동일한 공개 입력을 써야 할 경우에만 `--baseline-zip`, `--baseline-manifest`,
`--title-candidate`를 함께 명시한다.

조립 중에는 Steam 설치 폴더의 14개 대상 리소스와 `NOBU16.exe`, `NOBU16PK.exe`를
전후로 읽어서 hash가 완전히 같은지 확인한다. 이 workstream에는 게임 파일을 쓰거나,
실행 파일·레지스트리·메모리·DLL·후킹을 변경하는 명령이 없다. 결과물은 항상 저장소
`tmp/` 아래에만 생성된다.

## 명령

```powershell
$py = 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'

& $py -B workstreams\steam_jp_117_image_candidate_v1\build_steam_jp_117_image_candidate_v1.py bootstrap `
  --proposal tmp\steam_jp_117_image_candidate_v1_bootstrap.json

& $py -B workstreams\steam_jp_117_image_candidate_v1\build_steam_jp_117_image_candidate_v1.py verify `
  --scratch-root tmp\steam_jp_117_image_candidate_v1_verify

& $py -B workstreams\steam_jp_117_image_candidate_v1\build_steam_jp_117_image_candidate_v1.py build `
  --output-root tmp\steam_jp_117_image_candidate_v1_final
```

`bootstrap`은 추적용 검증 JSON 초안을 `tmp/`에만 만든다. `verify`와 `build`는
추적된 `verification.v1.json`과 정확히 같을 때만 성공한다. `build` 출력에는
`candidate/`, `candidate_manifest.v1.json`, 그리고 결정론적 v0.10.0 ZIP만 존재한다.

## 테스트

```powershell
& $py -B -m unittest workstreams\steam_jp_117_image_candidate_v1\test_steam_jp_117_image_candidate_v1.py -v
```
