# 서울한강체 PC PK 폰트 파이프라인 v1

`NOBU16PK.exe`의 파일 전용 한국어 경로인 `RES_SC/res_lang.bin`에 맞춰 서울한강체를 로컬에서 G1N으로 래스터화하는 재현 가능 파이프라인이다. 메모리 패치, DLL 주입, 후킹, EXE/레지스트리 변경을 사용하지 않으며, 게임 설치본을 직접 수정하지 않는다.

## 결론

- Switch 한글 패치의 `RES_JP/res_lang.bin`은 PC PK `RES_SC/res_lang.bin`에 raw-copy할 수 없다.
  - Switch G1N entry 6/7은 각각 **3 table, palette 91**이고 PC 순정 SC entry 6/7은 각각 **2 table, palette 129**이다.
  - 대상 언어 경로도 Switch는 `RES_JP`, PC PK는 `RES_SC`이다.
  - 비교는 header·hash·count만 읽은 결과이며 Switch G1N/픽셀/완성 리소스를 내보내지 않았다. 상세는 [evidence/switch_pc_g1n_compatibility.v1.json](evidence/switch_pc_g1n_compatibility.v1.json)을 본다.
- 따라서 Switch 완성 폰트가 아니라 서울시 공식 `SeoulHangangM.ttf`를 로컬 입력으로 검증하고, 기존 PC SC G1N entry 6/7의 빈 glyph map만 append한다.

## 공식 폰트와 고지

- 공식 다운로드: [서울특별시 서울서체](https://www.seoul.go.kr/seoul/font.do)
- 검증한 공식 archive: `seoul_font3.zip`, SHA-256 `7AB485B98F5B1A1B05CFD04484DD49A62F856BE8506223CD99E5EA1A33E400A7`
- 사용 입력: `SeoulHangangM.ttf`, SHA-256 `D27E1B26B55E507BEC1045962C954CF426D79605009C720FAD1C9EF808E312CB`
- 라이선스/출처: 서울특별시 서울한강체, 공공누리 제1유형(출처표시). 서울시는 무료 사용을 안내하지만 판매·유상양도·무단배포는 허용하지 않는다고 명시한다.

Switch 배포 README는 서울한강체라는 계열만 밝히고 M/L/B/EB 중 어느 굵기를 썼는지는 명시하지 않는다. 따라서 v1은 비교 가능한 단일 공식 입력으로 **M**을 고정한 것이며, Switch와 glyph 픽셀까지 동일하다고 주장하지 않는다.

이 저장소는 이를 보수적으로 적용한다. 서울한강체 TTF/OTF, 해당 폰트의 래스터 픽셀, Switch 리소스, 게임 원본 G1N/LINK, 완성 `res_lang.bin`은 커밋하거나 공개 배포물에 포함하지 않는다. 빌드 결과는 사용자 로컬의 `private/`에만 생성된다. 배포/화면에는 다음 출처를 유지한다.

> 출처: 서울특별시, 서울서체 서울한강체 — https://www.seoul.go.kr/seoul/font.do

## 현재 수요 범위

기본 corpus는 source-free 공개 한국어 overlay 네 개를 SHA로 고정한다.

| 원천 | 항목 수 |
| --- | ---: |
| MSGUI v0.2 | 4,037 |
| Switch v1.1 → PK `msgev` 엄격 이식 | 7,025 |
| Switch v1.1 → PK `msgdata` 엄격 이식 | 16,176 |
| Switch v1.1 → PK `msggame` 엄격 이식 | 6,018 |

합계 33,256 항목에서 1,238개 codepoint(한글 음절 1,101개)를 수집한다. PC 순정 SC에 이미 있는 비한글 glyph는 보존하고, 실제 래스터 추가 수요는 1,171개다. entry 6/7 table 0에는 1,106개, table 1에는 1,171개를 append한다. 정확한 pin·hash·고지는 [manifest.v1.json](manifest.v1.json)에 있다.

## 로컬 빌드

먼저 계획만 검증한다. 이 단계는 서울한강체 TTF를 읽지 않고 순정 SC backup과 공개 overlay hash만 확인한다.

```powershell
$Stock = 'F:\Games\NOBU16\KR_PATCH_BACKUP\officer_names_v0_1\stock\font.stock.bak'
python -B .\workstreams\font_seoulhangang_v1\build_seoulhangang_v1.py plan `
  --stock-archive $Stock `
  --output-root .\tmp\font_seoulhangang_v1_plan
```

공식 페이지에서 받은 정확한 `SeoulHangangM.ttf`를 로컬 경로에 둔 뒤 후보를 만든다. 출력 경로는 비어 있어야 하며, 게임 트리 안에서는 이 작업공간의 `tmp` 하위만 허용한다. 입력 archive와 설치 게임 파일은 덮어쓰지 않는다.

```powershell
$Font = 'F:\local-fonts\SeoulHangangM.ttf'
python -B .\workstreams\font_seoulhangang_v1\build_seoulhangang_v1.py build `
  --stock-archive $Stock `
  --font $Font `
  --output-root .\tmp\font_seoulhangang_v1_build_a
```

후보는 `private/candidate/res_lang.SC.seoulhangang-v1.bin` 아래에만 생긴다. 이 파일은 검증 전용이며 이 작업은 설치본에 복사하거나 적용하지 않는다.

## 결정성 확인

서로 비어 있는 두 출력 경로에 같은 build를 수행한 뒤 `private/build_manifest.json`, entry 6/7 G1N, candidate archive SHA가 모두 같은지 `verify_seoulhangang_v1.py`로 확인한다. glyph codepoint가 바뀌거나 서울시 폰트/순정 SC hash가 다르면 fail-closed한다.

## 남은 검증

구조·SHA·A/B 결정성은 자동 검증 범위다. 실제 배포 가능 판정에는 별도의 사용자 승인 아래 순정 백업, 화면별 한글 렌더링, 저장/불러오기, 게임 종료 검증이 추가로 필요하다. 이 작업은 그 설치/실행 단계를 수행하지 않는다.
