# PC MSGGAME B16 정적 대조 감사 v1

이 보고서는 PC `msggame.bin`의 0-base Block 16만 대상으로, 현재 Korean 리소스와 고정된 pristine PC Japanese 리소스를 직접 대조한 읽기 전용 기록이다. 아래 네 파일 외의 번역본·참조 자료는 사용하지 않았고, 후보 파일·Steam 적용·Git·네트워크·커밋·태그·릴리스 작업은 수행하지 않았다.

좌표는 `B16:<record>:<literal>`이며, literal은 검증된 `07 07 01 ... 07 07 02` UTF-16LE 구간만 뜻한다.

## 고정 입력

| 구분 | 직접 대조 파일 | packed SHA-256 | raw SHA-256 |
| --- | --- | --- | --- |
| Base KO | `F:\SteamLibrary\steamapps\common\NOBU16\MSG\JP\msggame.bin` | `F9342D73DE50FDFC97C1F8365A20FD5CEABD024CE63B82AF1F112D5EDEDCFCBB` | `27F2021CED9D7E36B89025EACCF3449D5E424EE5C38C758E5E0995C8234EEB6D` |
| Base pristine JP | `F:\Games\NOBU16\MSG\JP\msggame.bin` | `EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4` | `353010B59A3E04BFE5541162229C1CFCAD181EF0E75FCC9B6DE2043BFC515F38` |
| PK KO | `F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin` | `0A92516BC4B0A7AE98FD66418AD0BE289682B9DEE2CB25A8A1740A9609288092` | `737DAEAB7CC9257BC0F9E15523D01A0C3E807912B8D44393F75512BFB4C2A11E` |
| PK pristine JP | `F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP\file_only_transaction\steam-jp-1.1.7-v0.6.0\originals\MSG_PK\JP\msggame.bin` | `31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210` | `F052DA62C584C024C1EAF67A706253525421E6068976657DF6A6C07EFCA5D4E8` |

`msggame_format.py`로 네 입력 모두 압축 해제, parser 통과, raw parse → rebuild byte-exact를 확인했다.

## Parser topology와 대조 쌍

| 리소스 쌍 | 전체 block / record 수 | B16 record 수 (KO / JP) | B16 block 크기 (KO / JP) | B16 literal slot 수 (KO / JP) | 직접 구조 대조 literal 쌍 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Base | 18 / 19,152 | 88 / 88 | 4,970 / 4,104 bytes | 94 / 98 | 94 |
| PK | 18 / 21,751 | 88 / 88 | 4,968 / 4,140 bytes | 93 / 98 | 93 |

- Base와 PK 모두 KO/JP의 18개 block record-directory topology 및 B16의 record 좌표 `0..87`은 일치한다.
- `직접 구조 대조 literal 쌍`은 같은 record 안에서 양쪽에 존재하는 literal의 수다. 문학적 동등성을 뜻하지 않는다.
- Base는 84개 record에서 literal 수가 같고, `B16:4`, `15`, `32`, `38`에서 KO 1개 / JP 2개다. PK는 83개 record에서 같고, 같은 네 record와 `B16:45`에서 KO 1개 / JP 2개다.
- 이 차이는 Korean 문장이 JP의 두 literal을 하나로 합친 구조다. 예: Base `B16:4:0`의 현재 KO는 `싸움 없는 세상은\n과연 찾아올 것인가…`, JP는 `戦なき世は\n訪れるの` + `か…`이다. 누락 텍스트로 단정하거나 literal 분할을 되돌리지 않는다.

## 줄바꿈·제어·opaque skeleton

| 항목 | Base KO / JP | PK KO / JP |
| --- | ---: | ---: |
| literal 안 수동 LF 합계 | 85 / 85 | 85 / 85 |
| CR | 0 / 0 | 0 / 0 |
| ESC | 0 / 0 | 0 / 0 |
| LF·CR·ESC 이외 C0 control | 0 / 0 | 0 / 0 |
| `[]`, `<>` 형태 literal token | 0 / 0 | 0 / 0 |

- literal을 이어 붙인 record 단위 LF 순서는 Base/PK 각각 88개 record 모두 KO/JP가 같다. 따라서 위의 4개/5개 literal 분할 차이를 수동 개행 오류로 취급하지 않는다.
- literal slot 단위 C0 배열은 분할 차이 record에서만 다르게 보인다. LF 자체는 같은 record 안에 보존되어 있다.
- literal 텍스트를 제외한 opaque record skeleton은 Base 9개(`2, 4, 15, 29, 32, 36, 38, 43, 46`), PK 10개(`2, 4, 15, 32, 36, 38, 42, 43, 45, 46`)에서 JP와 다르다. 이 바이트에는 화면·런타임 의미가 미확정인 metadata가 포함될 수 있으므로, 이 감사 범위에서는 text-only 수정 대상으로 취급하지 않고 Hold한다.

## 문자 잔재 검사

Korean B16 literal에서 아래 일본어 잔재·손상 문자는 모두 0건이었다.

- U+FFFD replacement character
- Hiragana, Katakana, half-width Katakana, CJK unified ideograph
- U+30FB, U+3001, U+3002, U+00B7
- ASCII `...` 연속 말줄임표

표기 현황은 Base `U+2026` 32개 / U+002E 6개, PK `U+2026` 31개 / U+002E 6개다. U+002E는 `쉽지 않다.`, `군비를 갖추자.`처럼 문장 종결에 쓰인 단일 마침표이며, 이 감사만으로 통일 변경하지 않는다.

## 고신뢰 정적 수정 대상

없음.

B16의 94개 Base 및 93개 PK 구조 대조 literal을 JP와 함께 읽어 확인했으나, 이 네 PC 파일만으로 현재 텍스트를 바꾸어도 안전하다고 판정할 수 있는 명백한 오역·누락·문법 오류는 찾지 못했다. 따라서 후보 파일도 만들지 않았다.

## Hold

| 좌표 | JP | 현재 KO | Hold 이유 |
| --- | --- | --- | --- |
| Base/PK `B16:4:0`, `15:0`, `32:0`, `38:0`; PK `B16:45:0` | JP가 두 literal로 분할됨 | KO는 한 literal에 같은 문장 흐름을 합침 | record 단위 LF는 보존됐지만 literal 경계 및 opaque skeleton이 다르다. 런타임 화면과 폭을 확인하기 전에는 분할을 변경하지 않는다. |
| Base `B16:21:0` | `赤備の精鋭よ` | `아카조나에의 정예여` | `赤備`의 프로젝트 표준 용어(음역/번역)를 이 파일만으로 결정할 수 없다. |
| Base `B16:45:0` | `郡代では、やはり…\n部下の配属さえあれば` | `군다이로서는 역시…\n부하가 배속되기만 한다면` | 관직명 표기 정책과 UI 용어 확인이 필요하다. |
| Base/PK `B16:53:0` | `備え整わば勝利も同然\n黄備え、いざ勝たん` | Base `황색 부대여, 이제 승리하자` / PK `황비, 이제 승리하자` | `黄備え`의 고유 부대·색채 용어 여부와 Base/PK 표기 정책이 불명확하다. 현 파일만으로 한쪽을 정답으로 고정하지 않는다. |
| Base/PK `B16:58:0` | `チェスト、急げ！\n戦は近いぞ！` | `어서, 서둘러라!\n싸움이 가깝다!` | 사쓰마식 구호의 음역을 살릴지 자연어로 옮길지는 문체 결정 사항이다. |
| Base/PK `B16:66:0`, `76:0`, `78:0` | `禄寿応穏`, `米五郎左`, `一服` | `녹수응온`, `고메고로자`, `한 대` | 주문·인명·흡연/휴식 맥락은 단독 literal만으로 표준 표기나 장면 의미를 확정하기 어렵다. |
| 동적 조각 record들 (예: `B16:5:0`, `6:0`, `7:0-1`, `10:0-13:0`, `16:0-18:0`) | 조사·명사 조각 | `로는`, `의 상업을`, `을(를)` 등 | 삽입 이름·UI token과 결합되어 출력된다. 정적 문자열만 보고 조사를 고치면 실게임 문법이나 폭을 깨뜨릴 수 있다. |

## 결론

이 shard는 B16의 구조, 문자 잔재, LF/control, JP 대조에 대한 제한된 감사다. 전체 인물 대사나 전체 문학적 품질 전수조사가 완료되었다는 선언이 아니며, Hold 항목은 실제 런타임 출력·문맥·용어 정책 검증 없이 수정하지 않는다.
