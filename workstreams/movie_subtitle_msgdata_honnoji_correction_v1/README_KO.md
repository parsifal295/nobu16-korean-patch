# 혼노지 영상 자막 역사 표현 교정 v1

PK `MSG_PK/JP/msgdata.bin`의 혼노지의 변 영상 자막 두 곳만 교정한다.

| ID | 교정 결과 |
|---:|---|
| 18025 | `「도키의 때는 지금―천하를 다스릴 오월이로다」` |
| 18032 | `군기의 문양은… 도라지꽃.` |

입력은 선행 `movie_subtitle_msgdata_fix_v1`의 승인 후보로 고정한다.
빌더는 입력의 packed/raw 해시와 두 문자열의 UTF-16LE preimage를 모두
검사하며, 다른 문자열이 바뀌면 실패한다.

결정적 후보 SHA-256은
`36AA074DCEBD5E26D3679E5468F0529A996E54DAF65188C71C96EAC11862B982`다.

검증 범위는 영상 10편의 실제 자막 `17989–18237`, 총 249슬롯이다.
후보는 모든 슬롯이 채워지고 일본어 가나가 없으며 최대 2줄인지를 다시
검사한다. Steam 설치 경로에는 쓰지 않는다.

```powershell
python workstreams/movie_subtitle_msgdata_honnoji_correction_v1/build_movie_subtitle_msgdata_honnoji_correction_v1.py `
  --input <accepted-msgdata.bin> `
  --output-root tmp/movie_subtitle_msgdata_honnoji_correction_v1
```
