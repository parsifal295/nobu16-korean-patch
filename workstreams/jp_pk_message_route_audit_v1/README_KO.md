# 일본판 메시지 경로 감사 v1

이 작업은 일본판 실행 경로에서 한국어 메시지를 읽히게 하기 위한 **파일 전용** 후보를 검증한다. 게임 폴더, EXE, 레지스트리, 프로세스 메모리는 변경하지 않았다.

## 우선 후보: 한국어 SC 컨테이너를 JP 경로에 미러링

현재 누적 overlay 83,658개 작업을 병합하면 중복 override를 제외한 유효 좌표는 83,586개다. 이 좌표를 모두 포함한 SC 컨테이너를 원래 파일명 그대로 `MSG_PK/JP` 7종과 `MSG/JP/strdata.bin`에 배치하는 후보를 만들었다. 파일명을 바꾼 것이 아니라 언어 폴더만 `SC`에서 `JP`로 바꾼다.

| JP 대상 | 유효 좌표 | 후보 크기 | SHA-256 |
| --- | ---: | ---: | --- |
| `MSG_PK/JP/msgui.bin` | 4,037 | 116,027 | `C683AE9355A43F9A2104E49A6179363727CE0A550682F906C224A44F506826AC` |
| `MSG_PK/JP/msgev.bin` | 14,504 | 1,045,618 | `6B8228C0A0FDDF9C4C50C167C63282EF8AE28496F3CEEF4D56E2C71B9F29430A` |
| `MSG_PK/JP/msgdata.bin` | 26,318 | 492,035 | `5E641636C9D5BCD074CDD6B9D04DF5EF60487333835425157843389AC13DEA0C` |
| `MSG_PK/JP/msgbre.bin` | 2,217 | 478,591 | `69CF70A59F4F1D1EFB35A4123E4BA5B7092AA65DF629C5BE7D8317B97DB3CD29` |
| `MSG_PK/JP/msgire.bin` | 122 | 23,136 | `045B6ADDD7CF01401A3C10FA69A737B6C32259FA95007584E6A3E32CF2142D2A` |
| `MSG_PK/JP/msgstf.bin` | 8 | 16,289 | `C4A18BC5F7F7FCB8D9913D1AABC0C775059B09CE41261AFE38FB23F15146C195` |
| `MSG_PK/JP/msggame.bin` | 11,722 | 1,269,018 | `D5365A49945582D1F82BF5137CA898EC9EBE270B5F8B90513497E6ADC68E9AD9` |
| `MSG/JP/strdata.bin` | 24,658 | 953,064 | `A4B355256E4D3A30032362BBCD54199A3BC530C6D7FD1A09C9A79D53C94A703C` |

검증 결과는 다음과 같다.

- 8개 모두 LZ4 wrapper 해제, 내부 구조 strict parse, raw parse/rebuild를 통과했다.
- 공통 테이블 6종의 문자열 수는 JP 원본과 같다.
- `msggame`은 JP 원본과 block 18개, record 21,581개가 같다. 언어별 literal 수는 SC 25,598개, JP 29,149개로 다르며 미러 후보는 SC 컨테이너 구조를 보존한다.
- `strdata`는 JP 원본과 동일한 5개 block 및 `(25069, 4100, 3000, 122, 20)` slot 수를 보존한다.
- 누적 overlay 유효 좌표 83,586개를 후보에서 다시 읽어 모두 한국어 값과 일치함을 확인했다.
- 동일 입력 A/B 재구성 바이트가 일치한다.

단, **게임 내 JP 실행 화면 검증은 아직 하지 않았다.** 위 결과는 파일 형식과 번역 포함 완전성을 증명하며 런타임 호환 완료를 주장하지 않는다.

## 대조군: JP 원본 좌표 재빌드

JP 원본의 제어·형식 프로필과 정확히 맞는 좌표만 적용하는 보수적 대조군도 만들었다. 현재 분류는 78,197개 적용 가능, 5,389개 보류다. 보류 좌표는 미러 후보에서는 빠지지 않으며, 이 수치는 native-JP 재빌드 경로에만 해당한다.

모든 JP 원본은 [`route_lock.v1.json`](route_lock.v1.json)의 크기와 SHA-256이 맞아야만 읽힌다. 틀린 stock, 없는 좌표, 형식 프로필 불일치, 허용되지 않은 route는 즉시 실패한다.

## 산출물

- `public/jp_pk_message_native_route_map.v1.json`: source-free native route 전수 좌표표
- `evidence/jp_pk_message_route_evidence.v1.json`: overlay union, 8종 미러, 구조 및 해시 증거
- `review/jp_pk_message_native_blocked_review.v1.json`: native-JP 보류 좌표와 이유 키
- `translation_validation.v1.json`: 최종 통과 조건
- `jp_message_overlay_adapter.py`: JP stock SHA fail-closed in-memory adapter

완성 게임 바이너리는 추적하지 않는다. 로컬 후보는 `KR_PATCH_WORK/tmp/jp_pk_message_route_audit_v1_candidate_*` 아래에만 생성한다.

```powershell
python workstreams/jp_pk_message_route_audit_v1/build_jp_pk_message_route_audit_v1.py verify
python -m unittest workstreams.jp_pk_message_route_audit_v1.test_jp_pk_message_route_audit_v1
```
