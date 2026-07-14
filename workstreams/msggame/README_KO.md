# msggame.bin 구조 분석 v0.1

`msggame.bin`은 일반 메시지 테이블이 아니라 18개 블록에 가변 길이
바이트코드 레코드를 담은 다중 블록 리소스다. 이번 분석으로 레코드 경계와
표시 문자열 프레임을 확정했고, SC 파일을 기준으로 길이가 달라지는 한글
문자열도 오프셋을 다시 계산하여 파일 전용으로 재패킹할 수 있게 되었다.

## 확인된 번역 분모

| 대상 | 구조 레코드 | UTF-16LE 리터럴 슬롯 | 표시 가능한 SC 번역 후보 |
|---|---:|---:|---:|
| `MSG_PK/SC/msggame.bin` | 21,581 | 25,598 | 16,482 |
| `MSG/SC/msggame.bin` | 19,152 | 21,225 | 12,268 |

표시 후보는 SC 리터럴 중 공백·빈 문자열·제어문자만 있는 슬롯을 제외하고,
눈에 보이는 문자가 하나 이상 있는 슬롯이다. 전체 슬롯도 좌표와 해시를
보존하므로 이후 사람이 코드용 문자열을 발견하면 번역 대상에서 더 제외할
수 있다.

## 파일 구조

1. 24바이트 NOBU16 raw-LZ4 래퍼를 해제한다.
2. 원시 데이터 첫 `u32`는 블록 수이며 현재 모든 대상은 18이다.
3. 이어지는 18개 `(u32 offset, u32 size)`가 블록 디렉터리다.
4. 각 블록의 첫 `u32`는 레코드 수이고, 그 뒤의 `u32[]`는 블록 기준
   상대 레코드 오프셋이다. 마지막 레코드는 블록 끝에서 종료한다.
5. 바이트코드의 `07 07 01`과 `07 07 02` 사이가 UTF-16LE 리터럴이다.
6. 공개 오버레이 좌표는 `(block_id, record_id, literal_id)`를 사용한다.

PK의 SC·JP·TC·EN은 21,581개 레코드 좌표가 일치하고, 본편의 SC·JP·TC는
19,152개 레코드 좌표가 일치한다. 다만 언어에 따라 한 레코드 안의 리터럴
개수와 분할 방식이 다르므로 `literal_id`를 언어 사이에서 맹목적으로 같은
문장으로 취급하면 안 된다. 번역은 SC 좌표를 기준으로 하고 다른 언어는
같은 레코드의 문맥 참고 자료로 사용해야 한다.

## 구현 및 검증

- `msggame_format.py`: 엄격 구조 파서, 리터럴 파서, 무변경 byte-exact
  원시 재구축, 가변 길이 레코드/리터럴 재구축, raw-LZ4 재래핑
- `build_structure_inventory.py`: 설치된 7개 언어 파일을 읽기 전용으로
  검증하고 공식 문장 없이 구조 통계와 해시만 생성
- `build_literal_overlay.py`: SC 원문 해시와 `(block_id, record_id,
  literal_id)`를 검증하고, 한글 길이에 맞춰 모든 상위 오프셋을 다시 계산해
  별도 출력 폴더에 `msggame.bin`을 생성
- `public/structure_inventory.v0.1.json`: 공개 가능한 구조·분모 인벤토리
- `validation.v0.1.json`: 원본 핀, 결정성, 안전성 검증 결과
- `tests/`: 합성 픽스처와 실제 PK/SC 파일의 메모리 내 가변 길이 오버레이
  검증

7개 파일 모두 압축 해제 후 `parse → rebuild`가 바이트 단위로 동일했고,
모든 리터럴 마커가 균형을 이루며 UTF-16LE로 엄격 디코딩됐다. 실제
`MSG_PK/SC/msggame.bin`에 더 긴 한글 문자열을 넣은 결과도 메모리 안에서
재패킹·재파싱에 성공했고 설치 파일 해시는 바뀌지 않았다.

아직 게임 실행 화면에서 만든 파일을 검증하지 않았고, 번역 배치와 공통
배포 빌더 연결도 남아 있다. 구조상 파일 전용 오버레이를 만들 수 있다는
단계까지 확인된 상태다.

## 재검증

```powershell
python workstreams/msggame/build_structure_inventory.py
python -m unittest discover -s workstreams/msggame/tests -p 'test_*.py' -v
python workstreams/msggame/msggame_format.py verify ..\MSG_PK\SC\msggame.bin
python workstreams/msggame/msggame_format.py verify ..\MSG\SC\msggame.bin
python workstreams/msggame/build_literal_overlay.py --overlay <overlay.json> --output-root <output-dir>
```

생성기는 게임 설치 파일, 폰트, 설치기, 루트 진행률 문서를 수정하지 않는다.
