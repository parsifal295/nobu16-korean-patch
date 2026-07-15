# 일본판 기반 서울한강체 G1N 파이프라인 v1

일본어 경로로 실행하는 PC PK판의 한글 글리프를 파일 전용으로 생성한다. 기준 설치 경로는 `F:/SteamLibrary/steamapps/common/NOBU16`이며, 일반·고해상도 런타임 대응을 위해 다음 네 일본어 리소스를 함께 만든다.

- `RES_JP/res_lang.bin`: LINK 42개, G1N outer entry 6/7
- `RES_JP_PK/res_lang_pk.bin`: LINK 27개, G1N outer entry 16/17
- `RES_JP_PK_PORT/res_lang_pk_port1.bin`: LINK 38개, G1N outer entry 1
- `RES_JP_PK_PORT/res_lang_pk_port2.bin`: LINK 22개, G1N outer entry 0/1

Steam PK 1.1.7의 PORT 리소스에는 64/96px 글꼴이 별도로 존재한다. 이 경로가 빠졌던 v0.6.0은 FHD에서 한글이 나와도 QHD에서 `????`가 될 수 있었다. G1N이 없는 `port3`은 변경하지 않는다.

## 글리프 위계

각 G1N에는 65,536칸 맵이 3개 있다. 12바이트 레코드의 높이와 atlas stride를 교차 검증한 실제 위계는 다음과 같다.

| G1N | table 0 | table 1 | table 2 | 글꼴 배정 |
|---|---:|---:|---:|---|
| base 6 / PK 16 | 48 | 48 | 48 | EB / EB / EB |
| base 7 / PK 17 | 32 | 48 | 32 | B / EB / B |
| PK PORT1 entry 1 | 64 | 96 | 32 | B / EB / B |
| PK PORT2 entry 0 | 96 | 96 | 96 | EB / EB / EB |
| PK PORT2 entry 1 | 64 | 96 | 64 | B / EB / B |

48/96px급은 공식 `SeoulHangangEB.ttf`, 32/64px급은 공식 `SeoulHangangB.ttf`로 렌더한다. 96px EB의 raster 92는 기존 48px EB raster 46의 정확한 2배다. `SeoulHangangM.ttf`도 같은 공식 ZIP의 개별 해시를 고정하지만, 32px보다 작은 실제 테이블이 없으므로 사용하지 않는다.

## 최종 번역 수요 잠금

- 공개 overlay: 124개, 항목 88,062개
- 전체 코드포인트: 1,472개
- 한글 음절: 1,251개
- 일곱 G1N의 append union: 1,450개
- 공식 TTF raster: 1,427개
- JP stock 글리프 재사용: 23개
- 등록 정규화 대상: 11개 overlay

수요 해시는 빌더 상수와 `verification.v1.json` 양쪽에 고정한다. `msgui.bin`, `msggame.bin`, `msgdata.bin`의 11개 대상은 중앙 진행표의 `overlay_globs` 또는 `runtime_overlay_globs` 등록 전후에 같은 순서로 정규화되므로, 등록 시점이 달라도 source catalog와 후보 바이트가 변하지 않는다.

## cmap fallback 차단과 stock 재사용

빌드 전에 EB/B TTF의 Unicode cmap을 직접 파싱한다. append union 1,450개 가운데 두 TTF에서 제공되는 1,427개만 raster하고, cmap에 없는 다음 23개는 JP stock table 0의 metric과 width-packed pixel을 읽어 각 G1N table 2의 새 atlas tail에 복사한다. PORT1의 32px table 2는 팔레트가 다른 일반 JP 픽셀을 복사하지 않고 같은 G1N의 64px 픽셀을 2×2 box average로 축소한다. 기존 pointer를 alias하지 않는다.

`U+22BF`, `U+32A4`, `U+32A8`, `U+3303`, `U+330D`, `U+3314`, `U+3318`, `U+3322`, `U+3323`, `U+3326`, `U+3327`, `U+332B`, `U+3336`, `U+333B`, `U+3349`, `U+334A`, `U+334D`, `U+3351`, `U+3357`, `U+337C`, `U+337D`, `U+337E`, `U+FF65`

- append union: 1,450개, `32EAF6032E7923C8D89DA6D9C1F805C642BF51F49C94049EAEF6A0F66DD40156`
- TTF raster: 1,427개, `96179F0F8B8B7AB34AF4E4CFE8A2459023682E22C7F6DB0F3B4D047595534039`
- stock reuse: 23개, `0BDD77C1301D825618FC9DCF5388DD98B2B590DB1B3228DD7AEE65CCB6C1400E`

누락 집합이 위 23개와 정확히 같지 않으면 빌드를 중단한다. 따라서 GDI나 다른 시스템 글꼴 fallback에 의존하는 경로가 없다.

## 재현 명령

출력은 저장소 `tmp` 아래의 빈 경로에 만들며 설치된 게임 파일을 덮어쓰지 않는다.

```powershell
python workstreams/font_jp_seoulhangang_v1/build_jp_seoulhangang_v1.py build `
  --port-stock-root "F:/SteamLibrary/steamapps/common/NOBU16/KR_PATCH_BACKUP/file_only_transaction/steam-jp-1.1.7-v0.7.0-12file/originals/RES_JP_PK_PORT" `
  --font-eb F:\private\SeoulHangangEB.ttf `
  --font-b F:\private\SeoulHangangB.ttf `
  --output-root F:\repo\tmp\jp_font_candidate
```

`--port-stock-root`는 순정 `res_lang_pk_port1.bin`과 `res_lang_pk_port2.bin`을
보존한 디렉터리를 반드시 명시한다. 아직 패치하지 않은 Steam 설치 폴더를 사용할
수도 있지만, 이미 적용된 라이브 PORT 후보를 순정 입력으로 오인하지 않도록 기본값은
두지 않는다.

고정된 구조·보존 계약·후보 해시는 다음 명령으로 다시 확인한다.

```powershell
python workstreams/font_jp_seoulhangang_v1/build_jp_seoulhangang_v1.py verify `
  --port-stock-root "F:/SteamLibrary/steamapps/common/NOBU16/KR_PATCH_BACKUP/file_only_transaction/steam-jp-1.1.7-v0.7.0-12file/originals/RES_JP_PK_PORT" `
  --candidate-root F:\repo\tmp\jp_font_candidate
```

등록 전후 독립 A/B 빌드는 font archive, G1N, raster, plan, manifest가 모두 바이트 단위로 동일하다.

- base 후보: 154,216,023 bytes, `0E2AF3F3A163814FEB87A38085DC41E76BD3D98CDB6CD616B232F814CE0D95A0`
- PK 후보: 141,746,742 bytes, `EC758BC9B87F98B42E01CA6F841D963811BB944D113E2C65A1E9F5AE19F1DF08`
- PK PORT1 후보: 79,243,911 bytes, `00E9C1063ED164402AA70CB770100D8AE11A92B8024F20A4F1D89F2EA1A467F7`
- PK PORT2 후보: 67,086,423 bytes, `F18D99C4802AAB78C60C372FF0106ABD61ABDD8C026DC53CAE8FDE47C992C205`

## 보존 계약

일곱 G1N에서 수요에 필요한 map ordinal·record·atlas tail만 append한다. append 좌표를 제외한 기존 map, 기존 record, palette, stock atlas 전체 prefix는 동일하다. 바깥 LINK entry와 gap도 동일하므로 다른 G1T·이미지 payload는 변경하지 않는다.

공개 workstream에는 source-free recipe·해시·구조 증거·테스트만 둔다. TTF, raster pixel, stock/candidate G1N, 완성 `res_lang*.bin`은 포함하지 않는다.
