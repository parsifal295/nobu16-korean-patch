# v1 오프라인 후보 검증 결과

이 문서는 Switch v2.3의 한글 조판 개선을 Steam JP PK 1.1.7 경로에
적용하기 전에 만든 **비공개 tmp 후보**의 검증 기록이다. 게임 파일 적용,
배포본 생성, 릴리스 업로드는 수행하지 않았다.

## 범위와 입력

- Switch v2.2 → v2.3에서 확인한 최적화 집합: 공백 1자, 호환 자모 51자,
  한글 음절 2,353자, 총 2,405자
- 집합 SHA-256:
  `FD1338F53F1AB1B634496C65CA5AED5F5D182C2731B6A32E4AE1366A6030848D`
- 대상 G1N 7개: base `/6,/7`, PK `/16,/17`, PORT1 `/1`, PORT2 `/0,/1`
- base는 이미지 후보가 이미 Steam live `RES_JP`에 적용되어 있으므로,
  검증된 v0.9 원본 백업을 읽었다. PK/PORT 입력은 여전히 검증된 Steam
  v0.9 preimage를 읽었다.

## 후보 산출물

생성 위치는 git 추적·배포 대상이 아닌
`tmp/steam_jp_font_advance_candidate_v1_run7/private/candidate/`다.

| 논리 경로 | 입력 SHA-256 | 후보 SHA-256 |
|---|---|---|
| `RES_JP/res_lang.bin` | `0E2AF3F3A163814FEB87A38085DC41E76BD3D98CDB6CD616B232F814CE0D95A0` | `64CCD9068D7EBCFA670091B8A8FB367F1E577C1BCAC05847F4F3C77D7219A64D` |
| `RES_JP_PK/res_lang_pk.bin` | `EC758BC9B87F98B42E01CA6F841D963811BB944D113E2C65A1E9F5AE19F1DF08` | `C0C8509FC91C244A813D4BC20C46E515F6396D03BEAC71B80F89A39245125189` |
| `RES_JP_PK_PORT/res_lang_pk_port1.bin` | `00E9C1063ED164402AA70CB770100D8AE11A92B8024F20A4F1D89F2EA1A467F7` | `B5BF46E90C444DE1931BCF455447168C01B77967D3143B72916636157F59DE00` |
| `RES_JP_PK_PORT/res_lang_pk_port2.bin` | `F18D99C4802AAB78C60C372FF0106ABD61ABDD8C026DC53CAE8FDE47C992C205` | `13504CB00D09D9A43B9EA5D9AD9FADEF8F58EC12CD290872EAC3FF31335DDA60` |

각 G1N의 세 table 모두 2,405자 전체를 매핑한다. 모든 non-target LINK
entry payload/gap, target wrapper prefix, LINK entry 수는 입력과 정확히
일치함을 확인했다.

## 조판 안전 규칙

- Switch의 width/advance/4bpp row-stride는 동일한 비율로 참고한다.
- Switch atlas 또는 crop x-offset은 복사하지 않는다.
- 기존 PC glyph는 PC atlas에서 실제 ink bbox를 기준으로 crop+row-pack한다.
- 비율 환산 폭이 PC ink를 자를 경우에만 `max(환산 폭, ink를 담는 최소
  짝수 폭)`을 적용한다. 물리 allocation을 넘으면 실패한다.
- 새 1,152 glyph는 SHA 고정 공식 SeoulHangang EB/B raster만 사용한다.
- U+0020만 blank glyph로 허용하고 나머지 blank/clipping은 fail-closed다.

## U+30FB 보류

전각 중점 `U+30FB`은 2,405자 폭 최적화 범위 밖이다. 21개 대상 table 중
15개에는 이미 있고 6개 table-2에는 없다. 공식 SeoulHangang EB/B TTF도
U+30FB cmap glyph가 없으므로, 텍스트 정규화가 이를 출력하기 전에 별도
same-cell stock donor 복사 후보를 만들어야 한다. 이번 후보는 기존
`U+00B7`의 map/record를 21/21 table에서 정확히 보존한다.

## 실행 검증

- unit test: 11개 통과, Windows symlink 권한 의존 테스트 1개 skip
- fresh Switch audit ↔ 추적 `audit.v1.json` compact projection: exact PASS
- `installed_game_files_modified=false`, `output_is_private_tmp_only=true`
