# MSGGAME B11~B13 고신뢰 정적 수정 후보 v1

## 범위

`pc_dialogue_b11_b13_clean_audit_v1`에서 확정한 B13 리터럴 8개만 수정한다.

| 범위 | 슬롯 | 수정 |
| --- | --- | --- |
| Base | `13:258:0`, `13:260:0` | `献言` 메뉴 표기를 `건언`/`건의`에서 `헌언`으로 통일 |
| PK | `13:260:0`, `13:262:0`, `13:452:0` | `献言` 메뉴 표기를 `건언`/`건의`에서 `헌언`으로 통일 |
| PK | `13:353:0`, `13:575:0` | `要所` 계열을 UI의 기존 표기인 `요충지`/`특수 요충지`로 통일 |
| PK | `13:615:0` | `外様家宰`의 불일치 표기 `외양 가재`를 같은 기능의 기존 표기 `도자마 가재`로 통일 |

대상 외 모든 archive 레코드는 `record.data` 전체가 byte-identical이어야 한다. 각 수정은 기존 수동 LF 수와 non-text control skeleton을 보존한다.

## 고정 입력과 검증

네 정확한 PC 파일만 읽고 Switch/SC 소스는 읽지 않는다.

| 입력 | packed SHA-256 |
| --- | --- |
| Base 현재 KO | `F9342D73DE50FDFC97C1F8365A20FD5CEABD024CE63B82AF1F112D5EDEDCFCBB` |
| Base pristine JP | `EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4` |
| PK 현재 KO | `0A92516BC4B0A7AE98FD66418AD0BE289682B9DEE2CB25A8A1740A9609288092` |
| PK pristine JP | `31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210` |

빌더는 B11~B13의 Base/PK KO↔JP 레코드 수, 리터럴 토폴로지, 수동 LF 차이, opaque control skeleton 차이의 감사 프로필까지 고정한다. 후보 생성 뒤에도 이 프로필이 변하면 실패한다.

## 고정 후보 출력

| 리소스 | packed 크기 / SHA-256 | raw 크기 / SHA-256 |
| --- | --- | --- |
| `MSG/JP/msggame.bin` | `1,504,410` / `FFD9B5A53EE6B7F3B491B98441A68A0F26319AF947F4202829734722D99E6D97` | `1,498,508` / `CDB4D8D9E1D0EC401CB4C9ABE493F9D9ABF17FCC943F1D1458E3F3AB4059FD17` |
| `MSG_PK/JP/msggame.bin` | `1,806,550` / `8D1D7F08D92ACB0BF128E46953749A096339C7C33BF26F7DEFB584A459618697` | `1,799,468` / `1C7BCF821EC9D3991CCA1AE3733B6B86EB12649385976B5DDA5F0FD06D8FBC1B` |

산출물은 `tmp/pc_b11_b13_static_quality_candidate_v1/candidate/` 아래 private 후보 두 파일뿐이다. 출력 핀이 다르면 빌드·검증을 거부한다.

## 제한

- Steam 게임 리소스 적용·쓰기: 구현하지 않았고 수행하지 않는다.
- Git, 네트워크, 커밋, 푸시, 릴리스: 구현하지 않았고 수행하지 않는다.
- B11~B13 전체의 문학적 번역 완결이나 실제 게임 화면 합격을 주장하지 않는다.

## 검증 명령

```powershell
py -3 -B -X utf8 workstreams\pc_b11_b13_static_quality_candidate_v1\build_pc_b11_b13_static_quality_candidate_v1.py derive-pins
py -3 -B -X utf8 workstreams\pc_b11_b13_static_quality_candidate_v1\test_pc_b11_b13_static_quality_candidate_v1.py
py -3 -B -X utf8 workstreams\pc_b11_b13_static_quality_candidate_v1\build_pc_b11_b13_static_quality_candidate_v1.py build
py -3 -B -X utf8 workstreams\pc_b11_b13_static_quality_candidate_v1\build_pc_b11_b13_static_quality_candidate_v1.py verify-private
py -3 -B -X utf8 workstreams\pc_b11_b13_static_quality_candidate_v1\build_pc_b11_b13_static_quality_candidate_v1.py diff-check
```
