# NOBU16 common message table extractor/rebuilder (2026-07-13)

## 결과

`KR_PATCH_WORK/tools/nobu16_msg_table.py`를 구현했다. 이 도구는 LZ4가 해제된
`msgbre`, `msgdata`, `msgev`, `msgire`, `msgstf`, `msgui`의 단일 블록 문자열
테이블을 구조적으로 추출하고, 번역 길이가 달라져도 전체 문자열 오프셋과 논리
블록 크기를 다시 계산한다. 원본 게임 파일은 수정하지 않았다.

`msggame`은 같은 형식이 아니다. 실제 파일은 `block_count=18`인 멀티블록
바이트코드 컨테이너이므로 이 도구의 범위에서 명시적으로 제외하며, 입력하면
설명 있는 오류와 종료 코드 2를 반환한다.

## 확인된 raw 구조

| 위치 | 값/의미 |
|---:|---|
| `0x00` | `u32le block_count = 1` |
| `0x04` | `u32le block_offset = 0x0C` |
| `0x08` | `u32le logical_block_size` (파일 끝 정렬 패딩 제외) |
| `block+0x0C` | `u32le table_rel = 0x14` |
| `block+table_rel` | 오프셋 테이블, 현재 6종은 절대 `0x20` |
| `table+id*4` | `u32le`, 테이블 기준 UTF-16LEZ 문자열 상대 오프셋 |

테이블 첫 u32는 별도 크기 헤더가 아니라 **id 0의 상대 오프셋 자체**다.
오프셋 배열 바로 뒤에서 id 0 문자열이 시작하므로 `first_offset / 4 ==
string_count`가 성립한다. 문자열 절대 위치는 `table_offset + offset[id]`다.

재빌드는 첫 문자열 이전의 불투명 헤더/블록 메타데이터를 그대로 보존하고,
오프셋 배열의 모든 u32를 갱신한다. `0x08`의 논리 크기도 다시 기록한 뒤 파일을
4바이트 경계까지 `00`으로 패딩한다.

## 번역 파일

- CSV 열은 정확히 `id,text,translation`이며 출력 인코딩은 BOM 없는 UTF-8이다.
- Python 표준 CSV quoting과 `newline=""`을 사용하므로 원문 안의 줄바꿈도
  안전하게 왕복한다.
- `.jsonl`/`.ndjson`도 지원한다. 내장 줄바꿈이 JSON escape되므로 각 레코드는
  물리적으로 한 줄이다.
- `translation`이 비어 있으면 원문을 유지하고, 비어 있지 않으면 번역문을 쓴다.
- 행 수, id 연속성/중복, 원문 불일치, NUL, UTF-16 인코딩 가능 여부를 검증한다.
- 출력 경로가 raw 입력이나 번역 입력과 같으면 덮어쓰기를 거부한다.

## 6종 무변경 CSV 왕복 검증

각 raw에 대해 `extract`로 CSV를 만들고, 그 CSV를 수정하지 않은 채 `rebuild`한
결과를 원본과 SHA-256 비교했다. 6종 모두 바이트 단위로 동일했다.

| 파일 | 문자열 수 | raw 크기 | SHA-256 | 결과 |
|---|---:|---:|---|---|
| msgbre | 3,000 | 836,320 | `8445078e7691461d791364208a4286a00d73f0fe4df73569d376fe9e05986f64` | 동일 |
| msgdata | 29,210 | 744,236 | `da913d870da3c13f108e8e6727c9a8881b9e13a83f8eb7f02dd3c55d1d444b32` | 동일 |
| msgev | 17,910 | 1,868,232 | `806a34770aba15550033e0b2d51cfa849e3c9367b61bc0ba05c37b87f13475ef` | 동일 |
| msgire | 122 | 46,920 | `271325456e72b511b7991819a97f8725c5ea35790e263ffc7ce35ba1ab0f636c` | 동일 |
| msgstf | 20 | 20,052 | `5aa69f346d44c77c3230b1cb3fcb21f6977dc6f286fcc3f3ceeb713cd8544488` | 동일 |
| msgui | 5,100 | 219,108 | `ecfdaf31f393ea5a442c3d416910a80cad3eb9de9ed5ad1ba6559d0619bedbad` | 동일 |

CSV 첫 3바이트도 `69 64 2C` (`id,`)로 확인해 UTF-8 BOM이 없음을 검증했다.
검증 산출물은 `KR_PATCH_WORK/tmp/msg_table_roundtrip/`에 있다.

## 길이 변경과 후속 오프셋 검증

`msgstf` JSONL에서 원래 빈 문자열인 id 8을 `한글 길이 변경 검증 문자열`로
바꿨다. UTF-16LEZ 길이가 2바이트에서 32바이트로 늘어 다음 id 9의 상대
오프셋이 `19998`에서 `20028`로 정확히 30 증가했다. 논리 데이터도 30바이트
늘었고, 새 4바이트 정렬 패딩 2바이트 때문에 물리 파일 크기는 20,052에서
20,084로 증가했다.

새 raw를 다시 파싱하고, 무변경 재빌드하고, JSONL로 재추출했다. 세 단계가 모두
통과했으며 재추출 id 8도 정확히 같은 한글 문자열이었다.

별도 통합 검증에서는 `msgui` id 1을 `새로운 시작`으로 바꾼 raw를
`nobu16_lz4.py`로 wrapper 재압축 후 다시 해제했다. 재해제 raw의 SHA-256은
재빌드 raw와 같은
`bf79e31f5690428f52d2bda3ef47f27d73d2c6f6cd03afcf78cc09b973c99bad`였고,
재추출 문자열도 일치했다. 산출물은 `KR_PATCH_WORK/tmp/msg_table_probe/`에 있다.

## 사용 예

```powershell
# 원본 wrapper를 raw로 해제
python KR_PATCH_WORK/tools/nobu16_lz4.py decompress `
  MSG_PK/EN/msgui.bin KR_PATCH_WORK/tmp/msgui.raw

# CSV 또는 JSONL 추출
python KR_PATCH_WORK/tools/nobu16_msg_table.py extract `
  KR_PATCH_WORK/tmp/msgui.raw KR_PATCH_WORK/tmp/msgui.csv

# translation 열을 편집한 뒤 새 raw 생성
python KR_PATCH_WORK/tools/nobu16_msg_table.py rebuild `
  KR_PATCH_WORK/tmp/msgui.raw KR_PATCH_WORK/tmp/msgui.csv `
  KR_PATCH_WORK/tmp/msgui.ko.raw

# 구조/무변경 바이트 왕복 검사
python KR_PATCH_WORK/tools/nobu16_msg_table.py verify `
  KR_PATCH_WORK/tmp/msgui.ko.raw

# 원본 wrapper의 8바이트 prefix를 보존해 재압축
python KR_PATCH_WORK/tools/nobu16_lz4.py recompress `
  KR_PATCH_WORK/tmp/msgui.ko.raw KR_PATCH_WORK/tmp/msgui.ko.bin `
  --template MSG_PK/EN/msgui.bin
```

항상 새 출력 경로를 사용하고, 실제 게임 파일 적용 전에는 wrapper를 다시
해제해 raw SHA-256과 재추출 문자열을 확인하는 것이 안전하다.
