# 전략 지도 성 이름 세로쓰기: 파일 전용 경로 조사

## 판정

사용자가 확인한 **SC 기반 전략 지도 성 이름의 세로 표시를 재현 사실로
채택**한다. 현재까지 확인된 증거로는 이 문제가 `msgui.bin`/`msgdata.bin`의
문자열 속성이나 `res_lang.bin` 안의 누락된 가로 레이아웃 파일 때문이라고 볼 수
없다. 범용 실행파일이 지도 오버레이를 만들 때 영어 언어 비트(bit 8)를 검사하고,
그 결과에 따라 서로 다른 텍스트 형식값과 좌표 상수 묶음을 코드에서 직접 선택한다.

따라서 stock 범용 실행파일 + SC 리소스 조합에서 **정상적인 영어식 가로 지도
이름표를 켜는 파일 전용 스위치는 발견되지 않았다**. 현재 릴리스 게이트의
`castle_name_horizontal`은 계속 `false`이며 공개 배포본은 막힌 상태가 맞다.

이 조사는 설치본, 실행파일, 레지스트리, 실행 중 프로세스, canonical/release
산출물을 변경하지 않았다. Ghidra 분석 프로젝트와 `KR_PATCH_WORK/tmp`의 분석
산출물만 사용했다.

## 1. 범용 실행파일의 실제 언어 비트 초기화

분석 대상 범용 unpacked 실행파일:

- 크기: 29,609,536 bytes
- SHA-256:
  `7D64114D6C99FF3C40A2BA07B0D10A8E3024FFDE4833698CA0ACF900F4A28793`

언어 관리자는 `+0x22c` 필드를 비트 마스크로 사용한다.

```c
// 0x1408e8970
return (*(uint *)(manager + 0x22c) & requested_bit) != 0;
```

`Configs/LANGUAGE`를 읽는 범용 초기화 함수 `0x1408e8040`은 다음과 같이
동작한다.

```c
value = read_config("Configs", "LANGUAGE", 0);
if (value < 4) {
    bit = 1 << value;
    if (bit == 8) bit = 1;
    manager->language_bits = bit;
}
```

즉 설정값 `0, 1, 2`는 각각 bit `1, 2, 4`가 되지만, 설정값 `3`으로 bit 8을
요청해도 다시 bit 1로 강제 환원된다. 범용 실행파일의 설정 파일만 바꿔서는
영어 전용 분기를 활성화할 수 없다.

근거 산출물:

- `KR_PATCH_WORK/tmp/castle_layout_probe/generic_language_init.c`
- `KR_PATCH_WORK/tmp/castle_layout_probe/generic_field_22c.txt`

## 2. 지도 오버레이 텍스트 형식은 실행파일이 직접 선택

범용 실행파일의 `0x140e002e0`은 지도 오버레이 풀 type 1과 type 3에서 공통으로
생성되는 객체의 생성자다. 각 풀의 동시 객체 수는 40이며, 생성자는 동적 텍스트
객체 두 개를 포함한 여러 지도 표시 요소를 만든다.

생성자는 먼저 영어 언어 비트 검사를 저장한다.

```c
is_english = language_test(manager, 8); // 0x1408e8970
```

그 뒤 동일한 동적 텍스트 객체를 만들 때 다음 값을 코드 리터럴로 조립한다.

```c
if (!is_english) {
    format = make_size(0x1a) | 0x0100212c;
} else {
    format = make_size(language_specific_size) | 0x01002101;
}
```

이 선택은 생성자 안에서 두 번 반복된다. 텍스트 박스의 X/Y/폭/높이 및 관련
그래픽 값도 같은 영어 비트 검사로 서로 다른 실행파일 내부 `.rdata` 상수 묶음에서
가져온다. 외부 메시지나 PARAM 레코드에서 형식값을 읽는 경로가 아니다.

하위 텍스트 배치 함수 `0x1408f8030`은 형식값의 저위 비트 `0x02`, `0x08`,
`0x20` 등을 실제 정렬 계산에 사용하고, 영어 비트에 따라 글자 폭 및 세로 위치
계산도 달리한다. 따라서 `...212c`와 `...2101`의 차이를 단순 색상이나 폰트 번호
차이로 볼 수 없다. 다만 각 비트 하나의 명칭을 아직 완전히 역명명하지 않았으므로,
보고서에서는 이 값을 개별적으로 “세로쓰기 비트”라고 단정하지 않고
**영어/비영어 지도 텍스트 형식 및 배치 묶음**이라고 부른다.

근거 산출물:

- `KR_PATCH_WORK/tmp/castle_layout_probe/generic_map_overlay_ctor.c`
- `KR_PATCH_WORK/tmp/castle_layout_probe/en_text_layout_flags.c`
- `KR_PATCH_WORK/tmp/castle_layout_probe/en_draw_text_ctor.c`

같은 리터럴의 원본 파일 오프셋도 양쪽 실행파일에서 확인했다.

| 실행파일 | `...2101` | `...212c` |
|---|---|---|
| generic | `0xDFFC7C`, `0xDFFF44` | `0xDFFC90`, `0xDFFF63` |
| EN | `0xDFAEBC`, `0xDFB184` | `0xDFAED0`, `0xDFB1A3` |

이는 EN 분석본에서만 생긴 오인식이 아니라 범용 실행파일에도 동일한 언어 분기
구조가 있음을 확인하는 교차 증거다.

## 3. 외부 파일 후보 전수 확인

### 메시지 파일

`MSG_PK/*/msgui.bin`과 `msgdata.bin`의 성명 엔트리는 일반 UTF-16 문자열 및 ID
테이블이다. 성명 문자열 옆에 가로/세로 방향을 지정하는 메타데이터가 붙는 구조는
발견되지 않았다.

### 언어 리소스

`RES_*/res_lang.bin`의 핵심 글꼴은 entry 6/7이고, 나머지는 언어별 이미지/텍스처
성격이 중심이다. 동적 전략 지도 성명을 담은 별도 가로 이름표 레이아웃은 찾지
못했다.

### 공용 리소스

다음 LINK 아카이브를 최상위 엔트리별로 풀어 문자열/노드 이름을 재귀 검색했다.

- `RES/res_else.bin` — 250 entries
- `RES/res_grp.bin` — 172 entries
- `RES_PK/res_pk.bin` — 428 entries

`general_name`, `name_txt` 계열은 이벤트 대화, 인물명 창, 자막 레이아웃에서만
나왔다. `3Dmap/kyoten` 관련 엔트리들은 주로 상태 아이콘/애니메이션/모델
리소스였으며, 전략 지도 성 이름용 가로/세로 텍스트 박스 쌍은 발견되지 않았다.

검색 도구와 추출물은 다음 위치에 있다.

- `KR_PATCH_WORK/tmp/castle_layout_probe/scan_resource_strings.py`
- `KR_PATCH_WORK/tmp/castle_layout_probe/extract/`

### PARAM

`PARAM_PK/CastleInfo.bin`과 `PARAM_PK/EN/CastleInfo.bin`도 비교했다.

| 파일 | 크기 | SHA-256 |
|---|---:|---|
| `PARAM_PK/CastleInfo.bin` | 3,720 | `244DA50BA640C15208FC3B02D7E23D89B5ECB4D122ADECD94042697DAB7B75F3` |
| `PARAM_PK/EN/CastleInfo.bin` | 3,684 | `AE15B6BAFDE2A3F909834B44D2265211CF28BF1AA5106451F2D69F223740B4F3` |

두 파일은 12-byte header 뒤에 고정 길이 ASCII 숫자 행이 이어지고, EN 변형은
주로 목록 열 폭 같은 값을 다르게 가진다. 전략 지도 동적 이름표의 쓰기 방향을
지정하는 레코드로 볼 근거가 없다.

## 4. 파일 전용으로 남는 경로

### 정상 가로 레이아웃 전환

현재 증거상 막혔다. 범용 실행파일에서 영어 비트를 설정 파일로 만들 수 없고,
지도 텍스트 형식과 좌표는 실행파일 리터럴/내부 상수다. 이를 직접 바꾸는 것은
실행파일 수정이며 프로젝트의 파일 전용 배포 정책에서도 금지된 경로다. 메모리
패치, DLL 주입, 훅은 더 명확하게 금지된다.

EN 전용 실행파일은 bit 8을 하드코딩하지만, 기존 조사에서 한글 글리프 폭 처리에
별도의 실행 중 코드 변경 다섯 곳이 필요했다. 그러므로 EN 실행파일 + SC 파일 복사도
현재의 파일 전용 배포 해법이 아니다.

### 단일 wide-glyph 프록시 우회

프로젝트에는 별도의 **파일 전용 fallback**이 준비되어 있다. 각 성 이름을 사용하지
않는 한글 codepoint 한 글자로 치환하고, 그 글리프 비트맵 자체에 성명 전체를 가로로
그려 넣는 방식이다. 세로 배치기가 “한 글자”만 배치하게 하여 방향 분기를 우회한다.

관련 보고서:

- `KR_PATCH_WORK/reports/single_glyph_castle_probe_2026-07-14.md`
- `KR_PATCH_WORK/reports/single_glyph_castle_wrapped_candidate_2026-07-14.md`

이 방식은 실행파일/메모리를 건드리지 않지만 아직 런타임 성공이 확인되지 않았다.
또한 다음 제약이 있다.

1. G1N 폭/advance/stride가 255px 이하라 긴 성명은 개별 축소가 필요하다.
2. canonical 성명 ID를 쓰는 목록, 툴팁, 대사 삽입 화면에도 wide bitmap이 나타날
   수 있다.
3. `城/馆/御所/御坊` 접미사가 공용 ID라, 392개 성별 종류를 연결해 bitmap에
   포함해야 한다.
4. 392개 전체에 대해 지도 밖 화면의 클리핑과 가독성 QA가 필요하다.

따라서 이것은 “정상 가로쓰기 경로”가 아니라 **마지막 파일 전용 우회 실험**이다.

## 5. 다음 안전 시험과 완료 조건

다음 단계는 기존 `name-only` wide-glyph 시험 후보 하나를 해시/저널/원복 보장
harness로 적용한 뒤, 사용자가 실제 전략 지도에서 확인하는 것이다. 판정 기준은
명확하다.

- wide bitmap이 한 개의 가로 quad로 온전히 보이는가
- 별도 접미사가 아래에 남더라도 본체가 잘리지 않는가
- 원복 뒤 두 대상 파일이 stock SHA-256으로 복귀하는가

이 시험이 실패하면 현재 정책 안에서 입증된 파일 전용 해결책은 없다. 성공하더라도
392개 자동 생성, 성 종류 매핑, 긴 이름 축소, 전체 화면 QA를 마치기 전에는
`castle_name_horizontal=true` 또는 `release_eligible=true`로 바꾸면 안 된다.
