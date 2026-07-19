# PC MSGGAME B07–B10 독립 대사 감사

이 보고서는 Steam PC의 현재 Korean `msggame.bin`과 정확히 대응하는 pristine PC Japanese `msggame.bin`만 직접 대조한 독립 감사 기록이다. 후보 파일, 게임 파일, Steam, Git, 네트워크, 커밋, 릴리즈는 건드리지 않았다.

## 범위와 입력 고정

| 리소스 | Korean 입력 | PC Japanese 원문 | packed SHA-256 | raw SHA-256 |
| --- | --- | --- | --- | --- |
| Base KO | `F:\SteamLibrary\steamapps\common\NOBU16\MSG\JP\msggame.bin` | — | `F9342D73DE50FDFC97C1F8365A20FD5CEABD024CE63B82AF1F112D5EDEDCFCBB` | `27F2021CED9D7E36B89025EACCF3449D5E424EE5C38C758E5E0995C8234EEB6D` |
| Base JP | — | `F:\Games\NOBU16\MSG\JP\msggame.bin` | `EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4` | `353010B59A3E04BFE5541162229C1CFCAD181EF0E75FCC9B6DE2043BFC515F38` |
| PK KO | `F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin` | — | `0A92516BC4B0A7AE98FD66418AD0BE289682B9DEE2CB25A8A1740A9609288092` | `737DAEAB7CC9257BC0F9E15523D01A0C3E807912B8D44393F75512BFB4C2A11E` |
| PK JP | — | `F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP\file_only_transaction\steam-jp-1.1.7-v0.6.0\originals\MSG_PK\JP\msggame.bin` | `31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210` | `F052DA62C584C024C1EAF67A706253525421E6068976657DF6A6C07EFCA5D4E8` |

`B07`–`B10`은 `msggame_format.py`의 0-base block ID `7`–`10`이다. literal은 검증된 `07 07 01 ... 07 07 02` UTF-16LE slot만 대상으로 삼았다.

## 전수 구조 대조 결과

| 대상 | B07 records / literals | B08 | B09 | B10 | 합계 records / literals |
| --- | ---: | ---: | ---: | ---: | ---: |
| Base | 2,807 / 3,587 | 1,207 / 1,676 | 3,802 / 3,864 | 9 / 10 | 7,825 / 9,137 |
| PK | 2,887 / 3,779 | 1,248 / 1,815 | 4,149 / 4,325 | 9 / 10 | 8,293 / 9,929 |

- 총 **16,118 record 쌍**, **19,066 literal 쌍**을 좌표 순서대로 대조했다.
- Base 7,825개와 PK 8,293개 모든 record에서 KO/JP literal slot 수가 일치했다.
- 네 입력 모두 multi-block parser → 원본 raw rebuild가 byte-exact였다.
- 각 literal의 manual LF 수는 KO/JP가 모두 일치했다. Base 6,878개, PK 7,394개의 LF를 확인했고 CR은 0개였다.
- literal 내부 ESC/runtime/기타 C0 control skeleton의 KO/JP 불일치는 0개였다.
- 비literal opcode까지 포함한 record skeleton은 Base 31개, PK 31개가 JP와 다르다. 이들은 번역 중 과거에 추가·제거된 opaque opcode가 섞인 좌표라서 이 보고서에서는 **전부 Hold**로 두며, text-only 수정 대상으로 취급하지 않는다.

## 문자 잔재·수치·키워드 검사

- Korean literal에서 히라가나·가타카나·한자·U+FFFD는 발견되지 않았다. Base의 `B07:2778:0`, `B07:2785:0`에만 U+30FB `・`가 남아 있다.
- U+3001 `、`는 Base 50개, PK 55개 literal에 남아 있다. 다수는 runtime 삽입부 앞뒤의 구분자여서 쉼표/공백으로 일괄 치환하면 조립 결과와 줄폭이 바뀔 수 있다. 개별 렌더링 확인 전까지 Hold다.
- literal의 수동 LF, CR, ESC/runtime token topology는 KO/JP가 모두 일치했다. 수치 토큰 비교에서 Base `B08:889:1`와 PK `B08:901:1`의 `제2`만 원문의 한자 표기 `第二`와 형식이 달랐으며, 서수 의미는 유지되어 수정하지 않는다.
- 이 범위에서 `덴령` 0건, `전령`은 Base/PK 각 3건, `소성` 0건, `상사람` 0건, `선교` 0건이다.

## 고신뢰 수정 방향

아래 `<LF>`는 실제 U+000A를 뜻한다. 모든 권고는 literal text만 바꾸며 LF 수와 control skeleton을 보존한다. 아직 candidate로 만들지 않았다.

### 1. `使者`를 자연스러운 한국어 명사로 교정

| 좌표 | JP | 현 KO | 권고 KO | 판정 |
| --- | --- | --- | --- | --- |
| Base `B09:3776:0` | `講和の使者が効きましたな<LF>方針を巡って仲違いしたのでしょう` | `강화 사자가 통했군요<LF>방침을 두고 반목한 것이겠지요` | `강화 사절이 통했군요<LF>방침을 두고 반목한 것이겠지요` | `使者`의 문맥상 뜻은 강화 사절이다. `사자`보다 자연스럽고, `통했다`의 결과 의미를 유지한다. |
| PK `B09:4094:0` | 동일 | 동일 | 동일 | Base와 같은 literal이다. |

- current UTF-16LE SHA-256: `502CEA9756290AC6004B9FF9A9FCD0CAD0DA42BEF6DE7DF3F02ECE6B7F0981EB`
- target UTF-16LE SHA-256: `49C6930141FD96950CD1F229F171A5C8FEE3E3FA3D945F2D975C376ABC92C837`

### 2. 문장부호 뒤 공백 누락

| 좌표 | JP | 현 KO | 권고 KO | 판정 |
| --- | --- | --- | --- | --- |
| PK `B09:4113:0` | `伏兵がおったぞ！混乱している内に蹴散らすぞ！` | `복병이 있었다!혼란한 틈에 쳐부수자!` | `복병이 있었다! 혼란한 틈에 쳐부수자!` | 두 독립 문장이 공백 없이 붙어 있다. 뜻과 LF/control은 바꾸지 않는다. |

- current UTF-16LE SHA-256: `81C83E910F854320CA5DE5698575DFD560F29FA913F57F31D4D5D5C192947098`
- target UTF-16LE SHA-256: `6EED72FA56D5AA310FD6EC11F7AB3397192EF6A487E27ED5786ACF20995657D7`

### 3. 한국어 ellipsis 표기 통일

| 좌표 | JP | 현 KO | 권고 KO | 판정 |
| --- | --- | --- | --- | --- |
| Base `B09:3640:0` | `これでしばらく戦は出来ぬであろう...` | `이것으로 당분간 싸움은 하지 못하리라...` | `이것으로 당분간 싸움은 하지 못하리라…` | ASCII 점 세 개를 사용 중이다. 범위 내 한국어 대사의 `…` 표기와 통일한다. |
| Base `B09:3796:0` | `まさか見破られるとは・・・` | `설마 간파당하다니···` | `설마 간파당하다니…` | U+00B7 세 개를 ellipsis 하나로 통일한다. |
| PK `B09:4114:0` | 동일 | 동일 | 동일 | Base와 같은 literal이다. |

| 좌표 | current UTF-16LE SHA-256 | target UTF-16LE SHA-256 |
| --- | --- | --- |
| Base `B09:3640:0` | `08DCD2DDAA191111089EA952157082D025EBEC0438F87D6469DE71865C114D92` | `80A10359A740BC09B5D0A4E3033C4B57D56B66AB41DB5E5B5DF850B04AD3EB74` |
| Base `B09:3796:0`, PK `B09:4114:0` | `DA2923D02C5C31BAB02BFBB698D5124A7286DE3FB3E4B4D7AAAF6F12FDFF6909` | `12BDA0582865642E1D4E5962D5DF80CFEB2AC0F9444F5B731E6226B9D6AA3CAB` |

## Hold

| 좌표 | JP | 현 KO | Hold 사유 |
| --- | --- | --- | --- |
| Base `B09:3774:0`, `B09:3789:1`; PK `B09:4092:0`, `B09:4107:1` | `田北` | `기타키타` | 현재 읽기는 부자연스럽고 오독 가능성이 높다. 그러나 이 범위의 원문만으로 정확한 한국어 독음을 확정할 근거가 부족하다. 이름 권위 자료 또는 실제 게임 명부 대조 전에는 수정하지 않는다. |
| Base `B08:560:0`; PK `B08:572:0` | `さらなる加増を期待していましたが…` | `더 많은 가증을 기대하고 있었습니다만…` | `加増`은 봉록·영지 증가의 역사 용어다. `가증`은 현대어로는 낯설지만 문자상 오역으로 단정하기 어렵다. 용어집 결정 전 Hold다. |
| Base `B07:2778:0`, `B07:2785:0` | `・…` | `・…` | U+30FB bullet은 Korean UI에서는 어색할 수 있으나, UI bullet/style 및 폭 확인 없이 `·`나 `•`로 교체하지 않는다. |
| Base 50개 / PK 55개의 U+3001 `、` literal | 원문도 `、` | Korean에도 `、`가 남아 있음 | runtime 삽입부와 조립되는 구분자가 섞여 있다. 문맥별 쉼표·공백·줄폭 QA가 필요하므로 일괄 교체 금지. |
| Base 31개 / PK 31개의 opaque record skeleton 차이 | — | — | literal 범위 바깥 opcode 차이이므로 이 보고서의 텍스트 수정 권한 밖이다. |

## 한계와 다음 단계

이 작업은 B07–B10의 모든 literal 좌표를 구조적으로 직접 대조하고, 문자 잔재·수치·개행·control skeleton 및 고신뢰 언어 이상을 선별한 감사다. **19,066개 literal에 대한 인간 문학 감수 완료를 주장하지 않는다.**

후속 후보를 만들 때에는 위 여섯 고신뢰 literal만 W45 입력에서 다시 preimage hash로 확인하고, Base/PK 동기 좌표를 함께 다뤄야 한다. Hold 항목은 이름 권위, runtime 조립, 실제 게임 렌더링 검증 없이는 포함하면 안 된다.
