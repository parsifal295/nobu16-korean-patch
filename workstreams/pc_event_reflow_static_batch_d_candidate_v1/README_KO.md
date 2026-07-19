# PC PK 이벤트 정적 재배치 Batch D private 후보

## 결과

`pc_event_reflow_full_inventory_v1`에서 정적 폭·문맥 검토 대상으로 분리한 첫 25개
ID를 재검토했다. 그중 제목형 ID `4999`는 안전한 한국어 개행 위치가 분명하지 않아
보류했고, 나머지 **24개만** private 후보에 넣었다.

이 배치는 기존 LF를 지우는 작업이 아니다. 원본 24개는 모두 LF가 없는 한 줄이며,
각 행에 **수동 LF 하나를 새로 삽입**해 두 줄로 재배치한다. LF는 기존 어절 구분을
대체하거나 문장부호 뒤에만 들어가며, 보이는 단어·색상 태그·런타임 토큰·printf 토큰은
바꾸지 않는다.

Steam 파일, Git, GitHub, 네트워크, 릴리스에는 쓰기 기능이 없다. 출력은 오직
`tmp/pc_event_reflow_static_batch_d_candidate_v1/candidate` 아래에 생성된다.

## 입력과 출력 pin

| 구분 | 경로 / 프로필 |
|---|---|
| W45 한국어 입력 | `F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msgev.bin` — packed `01287E2ECC5328C85348657EFF06553353CB8664B0FB7E1669DB9FC591D53EBE` / 994,739 bytes, raw `F3716AB98D60931CEC0FE61976D8DAD386C05B30B7167BD1BDB2CDF02EC55ACC` / 990,828 bytes, 17,916 records |
| 직접 PC JP 근거 | `F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP\file_only_transaction\steam-jp-1.1.7-v0.6.0\originals\MSG_PK\JP\msgev.bin` — packed `A9D4434F589C231298D824617847574AEBE2E3302389517B322BE18E85050A84`, raw `07D7512BE0235753FC7BB0C7C548B61F471D9CDED01379E63B8AF8EAE013813E` |
| 폭 측정 글꼴 | 현재 Steam PC `RES_JP/res_lang.bin`, SHA-256 `3798CB758E6EA48A257F1FBBBBE56E800F668E6FA2DE0CFD4B277C785A322EE7` |
| private 출력 | packed `AB7B14FEFE360F6A5C48482A9B4866E8386CDF302FCAFD6C944AE7E9D6926C97` / 994,743 bytes, raw `70FAF792D88CA184A9E9A73C3CB825B7B1B872AFEADBA4CFFDD33587058303FB` / 990,832 bytes |

일본어는 같은 PC 레코드의 문장 단위·구문 확인에만 사용했다. Switch나 다른 언어
테이블은 열거나 검색하지 않았다.

## 승인된 24개 재배치

모든 target은 W45 원문의 LF 수 `0 → 1`만 바뀐다. 제어/태그 시그니처, 런타임과
printf 토큰, LF를 제외한 단어·markup 순서는 빌더가 각 target마다 검증한다.

| ID | 자연스러운 개행 경계 | target 줄 폭(px) |
|---:|---|---:|
| 3235 | 비유의 전반부 / 아사쿠라와 아자이 | 672 / 456 |
| 3238 | 누이를 시집보냄 / 동맹 개입 | 624 / 432 |
| 3269 | 미카와 사나이의 기개 / 보여 주마 | 792 / 240 |
| 3284 | 이 나라 사람들에게 / 구원을 전해야 한다 | 432 / 528 |
| 3847 | 오카자키의 / 마쓰다이라 가문은 | 408 / 528 |
| 3868 | 성주·나가오 마사카게 / 직접 오셨습니다 | 648 / 384 |
| 3886 | 그렇게 노골적으로 / 싫은 얼굴을 하지 마라 | 408 / 528 |
| 4016 | 그러던 중, 그는 / 유행병으로 쓰러졌다 | 360 / 552 |
| 4139 | 아사쿠라 가문 중신 / 아사쿠라 소테키 | 528 / 408 |
| 4142 | 그 소테키도 / 병으로 쓰러졌다 | 432 / 624 |
| 4329 | 경악 / 패하다니 | 720 / 216 |
| 4530 | 구니치카를 / 병마가 무정하게 덮쳤다 | 408 / 552 |
| 4752 | 가게토라는 / 간토의 구세주가 되었다 | 360 / 552 |
| 4758 | 이를 계기로 / 이름을 바꾸겠다 | 624 / 384 |
| 4911 | 사나다 유키타카의 셋째 아들 / 겐고로가 원복을 맞았다 | 648 / 552 |
| 4929 | 잘 들어라 / 가신들에게 이렇게 전하라 | 336 / 600 |
| 5031 | 도쿠가와 십육신장에도 꼽히는 / 와타나베 모리쓰나 | 792 / 408 |
| 5032 | 하치야 한노조라는 / 이름으로 알려진 하치야 사다쓰구 | 672 / 744 |
| 5092 | 맞지는 않았지만 / 크게 빗나가지도 않았다 | 384 / 552 |
| 5187 | 노지리호 인근 / 우사미 사다미츠의 저택 | 360 / 624 |
| 5209 | 무슨 말씀을 드려야 할지 / 모르겠습니다 | 696 / 312 |
| 5334 | 아케치 미쓰히데의 전반생은 / 수수께끼에 싸여 있다 | 624 / 504 |
| 5411 | 훗날 검성으로 칭송된 / 신카게류의 창시자다 | 480 / 480 |
| 5515 | 그러지 마시고 / 어떻게 좀 안 되겠습니까 | 336 / 648 |

## HOLD

| ID | 상태 | 이유 |
|---:|---|---|
| 4999 | HOLD | `미요시 가문·미요시 나가요시의 거성`은 제목형 구문이다. 점 구분자와 소유 조사 사이의 줄 위치가 문맥상 애매하므로, 보기 좋은 줄바꿈을 억지로 정하지 않았다. |

## 검증 범위

빌더는 다음을 실패 조건으로 둔다.

- W45 KO와 direct PC JP의 packed/raw SHA-256, 레코드 수, 각 target preimage hash 불일치
- 대상 24개 외의 레코드 변경, 또는 HOLD `4999` 변경
- target이 LF를 1개보다 많이/적게 삽입하는 경우
- 단어·markup의 레이아웃 정규화 순서, ESC 색상 태그 구조, 런타임·printf·제어 토큰의 변경
- 3줄 초과, 줄당 912 px 초과, 현재 이벤트 글꼴 폭과 선언 폭의 불일치
- 후보 LZ4/메시지 테이블 round-trip 또는 고정 출력 프로필의 불일치

실행 결과:

```text
build: PASS — 24 targets, hold 4999
verify-private: PASS
diff-check: PASS
unittest: 3 / 3 PASS
```

## 명령

```powershell
py -3 -B -X utf8 workstreams/pc_event_reflow_static_batch_d_candidate_v1/build_pc_event_reflow_static_batch_d_candidate_v1.py build
py -3 -B -X utf8 workstreams/pc_event_reflow_static_batch_d_candidate_v1/build_pc_event_reflow_static_batch_d_candidate_v1.py verify-private
py -3 -B -X utf8 workstreams/pc_event_reflow_static_batch_d_candidate_v1/build_pc_event_reflow_static_batch_d_candidate_v1.py diff-check
py -3 -B -X utf8 -m unittest workstreams/pc_event_reflow_static_batch_d_candidate_v1/test_pc_event_reflow_static_batch_d_candidate_v1.py -v
```

이 후보는 W58과 별개인 W45 기준 private component다. 최종 통합 단계에서는 W58과
record-level로 충돌을 검사한 뒤에만 합성할 수 있으며, 이 문서는 Steam 적용·릴리스
근거가 아니다.
