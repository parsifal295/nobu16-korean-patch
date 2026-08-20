# 역사 타이틀 카드 레이어 재작업 시제품 v1

기본 역사 타이틀 카드 35종 가운데 첫 번째 `独眼竜 → 독안룡`을 대상으로 하는
PNG 전용 시제품 파이프라인이다. 생성형 이미지와 인페인팅을 사용하지 않는다.
원본의 투명 캔버스, 알파, 색상장, 강조 코어, 금색 후광 및 줌 버스트를 분리하고,
프로젝트에서 이미 승인해 사용 중인 음식디미방체로 한국어 글자 마스크만 다시 만든다.

## 대상 구조

- LOW: `RES_JP/res_lang.bin /4`, 1024x256 BC3, 35종 x 3상태
- HIGH: `RES_JP_PK_PORT/res_lang_pk_port3.bin /2`, 2048x512 BC3, 35종 x 3상태
- 시제품: 그룹 0, 슬롯 0~2, `独眼竜 → 독안룡`
- 상태: 기본 금색 / 흰 글자와 금색 후광 / 줌 버스트

카드에는 별도 판이나 배경 그림이 없고 텍스트·효과만 투명 캔버스에 있다. 따라서
일반 버튼처럼 배경을 인페인트할 필요가 없다. 원본 3상태 자체를 다음 레이어로
분해한다.

1. 원본 알파에서 상태별 안전 경계와 중심을 측정한다.
2. 기본 상태의 원본 색상을 정규화 보간해 금색 색상장으로 만든다.
3. 강조 상태를 저채도 고휘도 코어와 금색 후광으로 분리한다.
4. 음식디미방체 한국어 마스크를 원본 코어 경계에 맞춰 배치한다.
5. 원본에서 얻은 색상장을 새 마스크에 적용한다.
6. 강조 코어를 결정적으로 확대 누적해 3번째 줌 버스트 상태를 만든다.
7. LOW와 HIGH를 각각 원본 좌표계에서 렌더하고 경계·클리핑·결정성을 검증한다.

중간 레이어와 비교 시트, 재조립 후보는 모두 `tmp` 아래에만 쓴다. Steam 쓰기는
별도 적용 스크립트에서 후보·기준 해시, 게임 프로세스 종료 및 원본 백업을 검증한
경우에만 수행한다. v0.94 패처는 이 시제품 단계에서 변경하지 않는다.

## 현재 시제품 결과

- 승인 후보: `tmp/historical_title_card_layered_pilot_v1/pilot_006/`
- 비교 시트: `contact_sheet.png`
- 빌드 보고서: `build_report.json`
- 결과 매니페스트 SHA-256: `B71061FD7229410E1BC1C9785CDA484DD3DC1775A18066A9E1825B50A2D53994`
- 독립 재실행 `pilot_007`과 결과 매니페스트가 일치한다.
- LOW/HIGH 각 3상태의 캔버스 경계 접촉과 클리핑이 없다.
- 투명 픽셀의 RGB는 0으로 정규화했다.
- `binary_003`과 독립 재실행 `binary_004`의 후보 세트 SHA-256은
  `65C8CB88DB3DD082A3EF0784F1619CBEE5AE0F21BE1CE246401A47ED7A0AE645`로 일치한다.
- 변경 범위는 두 아카이브의 역사 타이틀 outer 엔트리와 내부 슬롯 0~2뿐이다.
  LOW의 다른 내부 슬롯 102개·outer 엔트리 41개, HIGH의 다른 내부 슬롯
  102개·outer 엔트리 9개는 원본과 바이트 단위로 같다.

## Steam 인게임 QA 후보 적용

사용자가 승인된 릴리스 후보를 만들기 위한 인게임 테스트라고 명시 승인하여
2026-08-20에 Steam 설치본에 시제품만 적용했다. 적용 당시 `NOBU16PK.exe`는
종료 상태였고, 복사 전 원본과 복사 후 후보 및 백업을 SHA-256으로 검증했다.

- `RES_JP/res_lang.bin`: `9DE71D530D71181643B1F48DBB08E06CC2AFDC59B4BBB196D85B1FEBCF1EB046`
- `RES_JP_PK_PORT/res_lang_pk_port3.bin`: `6E8981691FA07C392DF1AF5CA00D1C5CAB1DD8B014C28CBA7B340729B2AC3618`
- 백업: `tmp/historical_title_card_layered_pilot_v1/steam_backup_20260820_qa_001/`
- 적용 보고서: 백업 폴더의 `steam_apply_report.json`
- 영구 기록: `steam_qa_deployment.v1.json`

아직 게임을 실행하거나 화면을 판정하지 않았다. LOW는 1280x720, HIGH는
3840x2160에서 각각 확인하며, 해상도를 바꾼 뒤 매번 `NOBU16PK.exe`를 완전히
종료하고 다시 실행해야 한다. 각 결과에는 선택 해상도와 완전 재시작 여부를 기록한다.

## 실행

```powershell
$py = 'tmp\navigation_wheel_layered_rebuild_v1\.venv\Scripts\python.exe'
$target = 'I:\Workspaces\NOBU16-Korean\scratch\release-v0940-approve-all-layered-20260820-01\generator-output-03\target'
$font = 'I:\Workspaces\NOBU16-Korean\repository\KR_PATCH_WORK\tmp\third_party_fonts\yeongyang_eumsikdimibang\Yydimibang.ttf'
$out = 'tmp\historical_title_card_layered_pilot_v1\pilot_001'

& $py -B workstreams\historical_title_card_layered_pilot_v1\build_historical_title_card_layered_pilot_v1.py build `
  --jp-low "$target\RES_JP\res_lang.bin" `
  --jp-high "$target\RES_JP_PK_PORT\res_lang_pk_port3.bin" `
  --font $font `
  --output-root $out

& $py -B workstreams\historical_title_card_layered_pilot_v1\build_historical_title_card_layered_pilot_v1.py verify `
  --output-root $out

& $py -B -m unittest `
  workstreams\historical_title_card_layered_pilot_v1\test_historical_title_card_layered_pilot_v1.py -v

& $py -B workstreams\historical_title_card_layered_pilot_v1\build_historical_title_card_binary_pilot_v1.py build `
  --prototype-root tmp\historical_title_card_layered_pilot_v1\pilot_006 `
  --output-root tmp\historical_title_card_layered_pilot_v1\binary_003

& $py -B workstreams\historical_title_card_layered_pilot_v1\build_historical_title_card_binary_pilot_v1.py verify `
  --output-root tmp\historical_title_card_layered_pilot_v1\binary_003
```

## 인게임 QA 뒤 다음 단계

실게임에서 글꼴, 크기, 장평, 금색 및 버스트 강도를 승인받은 뒤에만 35종 전체
카탈로그를 확정한다. 동일 파이프라인을 기본 35종과 PK 11종으로 확장하고,
완성 후보를 v0.94 패처에 통합한다. 현재 Steam 반영은 `독안룡` 시제품의
릴리스 후보 QA 범위이며 최종 릴리스 승인을 뜻하지 않는다.
