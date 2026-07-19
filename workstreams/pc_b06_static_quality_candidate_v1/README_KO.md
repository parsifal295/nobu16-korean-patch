# MSGGAME B06 고신뢰 정적 수정 후보 v1

## 범위

`pc_b06_clean_pc_audit_v1`의 고신뢰 PK 인물 대사 결함 두 슬롯만 후보화한다.

| 슬롯 | 현재 PK KO | 후보 KO | 근거 |
| --- | --- | --- | --- |
| `6:3144:0` | `전투는 잠시 끝났습니다\n잘 받아들여 주셨습니다` | `전투는 잠시 끝났습니다\n부디 승복해 주십시오` | 원문의 요청형을 완료형으로 잘못 옮긴 문제를 복구한다. 같은 JP 원문의 Base PC 번역도 요청형이다. |
| `6:3455:0` | `공훈 1위는 기쁘지만,\n이 자리는 아직 제게 과분합니다.\n더욱 노력하겠습니다.` | `공훈 1위는 기쁘지만,\n이 자리는 아직 제게는 모자랍니다.\n더욱 노력하겠습니다.` | `役不足`의 "현 지위가 화자 역량에 부족함"을 "화자에게 과분함"으로 뒤집은 문제를 바로잡는다. |

두 항목 모두 기존 수동 줄바꿈 수를 유지한다. 비텍스트 제어 바이트·리터럴 토폴로지·자리표시자는 변경하지 않는다.

## 고정 입력

직접 PC 파일 네 개만 읽는다. Switch·SC 소스는 읽지 않는다.

| 입력 | packed SHA-256 |
| --- | --- |
| Base 현재 KO | `F9342D73DE50FDFC97C1F8365A20FD5CEABD024CE63B82AF1F112D5EDEDCFCBB` |
| Base pristine JP | `EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4` |
| PK 현재 KO | `0A92516BC4B0A7AE98FD66418AD0BE289682B9DEE2CB25A8A1740A9609288092` |
| PK pristine JP | `31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210` |

## 산출물과 제한

- 산출물은 `tmp/pc_b06_static_quality_candidate_v1/candidate/MSG_PK/JP/msggame.bin`의 private 후보뿐이다.
- 후보는 B06의 PK 레코드 `6:3144`, `6:3455`만 논리적으로 변경한다.
- Steam 게임 파일 적용, Git 작업, 네트워크, 푸시, 릴리스는 구현하지 않았고 수행하지 않는다.
- 실제 게임 화면 검증이나 B06 전체의 문학적 번역 완결을 주장하지 않는다.

## 고정된 후보 출력

| 항목 | 값 |
| --- | --- |
| packed 크기 / SHA-256 | `1,806,538` / `A5316297C0E8EE51B8E0DBBCDF62B1B28F93446C729BCF24E922D507146E3F47` |
| raw 크기 / SHA-256 | `1,799,456` / `00AECBD9458BD9B575539B77949328A93569415B2AD630F77CE246DCDF06C5B5` |
| 논리 변경 레코드 | `6:3144`, `6:3455` (2개) |

빌더는 위 출력 핀이 다르면 생성과 검증을 중단한다.

## 검증 명령

```powershell
py -3 -B -X utf8 workstreams\pc_b06_static_quality_candidate_v1\build_pc_b06_static_quality_candidate_v1.py derive-pins
py -3 -B -X utf8 -m unittest workstreams\pc_b06_static_quality_candidate_v1\test_pc_b06_static_quality_candidate_v1.py
py -3 -B -X utf8 workstreams\pc_b06_static_quality_candidate_v1\build_pc_b06_static_quality_candidate_v1.py build
py -3 -B -X utf8 workstreams\pc_b06_static_quality_candidate_v1\build_pc_b06_static_quality_candidate_v1.py verify-private
py -3 -B -X utf8 workstreams\pc_b06_static_quality_candidate_v1\build_pc_b06_static_quality_candidate_v1.py diff-check
```

`derive-pins`는 읽기 전용이다. 그 결과의 출력 해시를 빌더 상수에 고정하기 전에는 후보 생성·검증을 거부한다.
