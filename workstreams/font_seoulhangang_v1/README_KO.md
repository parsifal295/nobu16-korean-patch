# 서울한강체 PC PK 폰트 파이프라인 v1

`NOBU16PK.exe`의 파일 전용 한국어 경로인 `RES_SC/res_lang.bin`에 맞춰 서울한강체를 로컬에서 G1N으로 래스터화하는 재현 가능 파이프라인이다. 메모리 패치, DLL 주입, 후킹, EXE/레지스트리 변경을 사용하지 않으며, 게임 설치본을 직접 수정하지 않는다.

## 결론

- Switch 한글 패치의 `RES_JP/res_lang.bin`은 PC PK `RES_SC/res_lang.bin`에 raw-copy할 수 없다.
  - Switch G1N entry 6/7은 각각 **3 table, palette 91**이고 PC 순정 SC entry 6/7은 각각 **2 table, palette 129**이다.
  - 대상 언어 경로도 Switch는 `RES_JP`, PC PK는 `RES_SC`이다.
  - 비교는 header·hash·count만 읽은 결과이며 Switch G1N/픽셀/완성 리소스를 내보내지 않았다. 상세는 [evidence/switch_pc_g1n_compatibility.v1.json](evidence/switch_pc_g1n_compatibility.v1.json)을 본다.
- 따라서 Switch 완성 폰트가 아니라 서울시 공식 `SeoulHangangEB.ttf`와 `SeoulHangangB.ttf`를 로컬 입력으로 검증하고, 기존 PC SC G1N entry 6/7의 빈 glyph map만 append한다.
- PC 표시 위계는 entry 6의 48px table 0/1에 **서울한강 EB**, entry 7의 32px table 0/1에 **서울한강 B**를 배정한다. PC의 2-table 구조 자체는 바꾸지 않는다.

## 공식 폰트와 고지

- 공식 다운로드: [서울특별시 서울서체](https://www.seoul.go.kr/seoul/font.do)
- 검증한 공식 archive: `seoul_font3.zip`, SHA-256 `7AB485B98F5B1A1B05CFD04484DD49A62F856BE8506223CD99E5EA1A33E400A7`
- 48px 입력: `SeoulHangangEB.ttf`, SHA-256 `60D6A471E9A14F4BA563612D2577B9B6CCB2D1C599A69191B3F9F82EF80A19D1`
- 32px 입력: `SeoulHangangB.ttf`, SHA-256 `C33BAB9596C0B60ADA7EA9B3456E00E1CFD8EE63C599DB2F0EF71A84BA54769B`
- 라이선스/출처: 서울특별시 서울한강체, 공공누리 제1유형(출처표시). 서울시는 무료 사용을 안내하지만 판매·유상양도·무단배포는 허용하지 않는다고 명시한다.

Switch 배포 README는 서울한강체라는 계열만 밝히고 M/L/B/EB 중 어느 굵기를 썼는지는 명시하지 않는다. PC 패치는 화면 크기 위계를 명시적으로 살리기 위해 **48px=EB, 32px=B**를 고정하며, Switch와 glyph 픽셀까지 동일하다고 주장하지 않는다.

이 저장소는 이를 보수적으로 적용한다. 서울한강체 TTF/OTF, 해당 폰트의 래스터 픽셀, Switch 리소스, 게임 원본 G1N/LINK, 완성 `res_lang.bin`은 커밋하거나 공개 배포물에 포함하지 않는다. 빌드 결과는 사용자 로컬의 `private/`에만 생성된다. 배포/화면에는 다음 출처를 유지한다.

> 출처: 서울특별시, 서울서체 서울한강체 — https://www.seoul.go.kr/seoul/font.do

## 현재 수요 범위

기본 corpus는 `translation_progress.v0.1.json`에 등록된 **PK 전용 7개 메시지
리소스와 PK 실행 시 함께 읽는 정확한 공유 `MSG/SC/strdata.bin` 1개의 모든
source-free 공개 overlay**를 SHA로 고정한다. 다른 `MSG/SC` 메시지 경로는
거부한다. 진행률 파일 자체와 93개 입력 파일의 path·SHA·schema·항목 수를 합친
catalog hash가 모두 맞아야 한다.

| PK 로드 리소스 | overlay 파일 / 항목 수 |
| --- | ---: |
| `msgui` | 1 / 4,037 |
| `msgev` | 35 / 13,178 |
| `msgdata` | 10 / 21,152 |
| `msgbre` | 14 / 2,217 |
| `msgire` | 1 / 122 |
| `msgstf` | 1 / 8 |
| `msggame` | 29 / 10,352 |
| 공유 `MSG/SC/strdata.bin` | 2 / 24,425 |

합계 93개 overlay의 75,491행(좌표 중복을 포함한 글꼴 수요 입력)에서 1,389개
codepoint(한글 음절 1,232개)를 수집한다. PC 순정 SC에 이미 있는 비한글 glyph는
보존하고, 실제 래스터 추가 수요는 1,306개다. entry 6/7 table 0에는 1,237개,
table 1에는 1,306개를 append한다. 독립 A/B verifier는 네 G1N table 모두가 이
전체 수요를 누락 없이 매핑하는지도 확인한다. 정확한 pin·hash·고지는
[manifest.v1.json](manifest.v1.json)에 있다.

## 로컬 적용 상태

2026-07-15에 최신 1,306개 래스터 수요를 `48px=EB / 32px=B`로 독립 A/B
빌드했고, 두 폰트 후보가 SHA-256
`C9A522AE77A93186F8376E9D07E044436B6CF7415B77021217AADA337EDAE173`로
일치함을 확인했다. 현재 설치 archive의 비폰트 LINK entry 40개를 그대로 보존하고
entry 6/7만 합성한 최종 후보는
`DB94884F058EA5DEE72F8BC3584E157B98F7B59DB70D7265CCE9125452F0A431`이다.
제목 이미지가 든 outer LINK entry 3은 적용 전후 SHA와 바이트가 동일하다.

로컬 적용은 `pk-font-eb48-b32-preserve-images-20260715-v1` 파일 전용
트랜잭션으로 수행했으며, predecessor
`057E3B7E1BA426EAAAC1ABE3A7907DB7E750BDAD9419E87743C5A5612D1A6E62`를
검증된 backup으로 보존한다. restore dry-run은 통과했지만 실제 화면에서 굵기,
클리핑, 프로필 역할을 확인하는 런타임 QA는 아직 남아 있다.

## 로컬 빌드

먼저 계획만 검증한다. 이 단계는 서울한강체 TTF를 읽지 않고 순정 SC backup과 공개 overlay hash만 확인한다.

```powershell
$Stock = 'F:\Games\NOBU16\KR_PATCH_BACKUP\officer_names_v0_1\stock\font.stock.bak'
python -B .\workstreams\font_seoulhangang_v1\build_seoulhangang_v1.py plan `
  --stock-archive $Stock `
  --output-root .\tmp\font_seoulhangang_v1_plan
```

공식 페이지에서 받은 정확한 `SeoulHangangEB.ttf`와 `SeoulHangangB.ttf`를 로컬 경로에 둔 뒤 후보를 만든다. 출력 경로는 비어 있어야 하며, 게임 트리 안에서는 이 작업공간의 `tmp` 하위만 허용한다. 입력 archive와 설치 게임 파일은 덮어쓰지 않는다.

```powershell
$FontEB = 'F:\local-fonts\SeoulHangangEB.ttf'
$FontB = 'F:\local-fonts\SeoulHangangB.ttf'
python -B .\workstreams\font_seoulhangang_v1\build_seoulhangang_v1.py build `
  --stock-archive $Stock `
  --font-eb $FontEB `
  --font-b $FontB `
  --output-root .\tmp\font_seoulhangang_v1_build_a
```

후보는 `private/candidate/res_lang.SC.seoulhangang-v1.bin` 아래에만 생긴다. 이 파일은 검증 전용이며 이 작업은 설치본에 복사하거나 적용하지 않는다.

## 결정성 확인

서로 비어 있는 두 출력 경로에 같은 build를 수행한 뒤 `private/build_manifest.json`, entry 6/7 G1N, candidate archive SHA가 모두 같은지 `verify_seoulhangang_v1.py`로 확인한다. glyph codepoint가 바뀌거나 서울시 폰트/순정 SC hash가 다르면 fail-closed한다.

## 남은 검증

구조·SHA·A/B 결정성은 자동 검증 범위다. 실제 배포 가능 판정에는 별도의 사용자 승인 아래 순정 백업, 화면별 한글 렌더링, 저장/불러오기, 게임 종료 검증이 추가로 필요하다. 이 작업은 그 설치/실행 단계를 수행하지 않는다.
