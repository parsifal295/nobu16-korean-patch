# 후리가나 한국 한자음 전환

JP 화면의 표시 무장명은 기존 한국어 표기를 그대로 유지한다. 대신 무장 편집기 등의 `성 독음`·`이름 독음` 필드는 일본식 가나 독음이 아니라 원문 한자의 한국 한자음으로 바꾼다. 예를 들어 `織田`와 `信長`의 독음은 각각 `직전`, `신장`이며, 화면에서는 공백 없이 `직전신장`으로 이어진다.

대상은 PK `MSG_PK/JP/msgdata.bin`의 완전한 이름 사전 독음 4,569칸(주 이름 3,332개, 여성명 100개, 보조 장수명 1,137개)과, 같은 사전이 정렬된 Base `MSG/JP/strdata.bin` block 0의 4,556칸(주 이름 3,319개와 나머지 두 사전 전부)이다. 뒤따르는 성·도시·가문·칭호 독음은 별도 표이므로 건드리지 않는다. `msgev.bin`은 표시 전체 이름만 있고 독음 칸이 없으므로 대상이 아니다.

Unicode 17.0 `Unihan_Readings.txt`의 `kHangul`을 직접 대응 글자의 기준으로 검증한다. 다독자 중 이 사전의 일본 신자체·용례가 확정된 4자는 별도 검수값을 쓰며(`姫→희`, `芸→예`, `茶→차`, `証→증`), 여기에 없는 일본 신자체·이체·희귀자 79개도 대상 사전에 맞춰 코드포인트별로 검수한 고정 한국 한자음만 쓴다. 따라서 일반 사전의 임의 fallback이 섞이지 않으며, 예를 들어 `渓→계`, `楽→락`(첫머리에서는 `낙`)으로 처리된다. 고정한 `hanja==0.15.1` 표는 입력 문자 범위와 Unicode 대응값을 교차 검증하는 데만 사용한다. 단어 시작의 두음법칙을 적용하고, 원문이 가나뿐인 예외는 기존 가나 독음을 한글로 옮긴다. 모든 결과는 공백 없는 한글만 허용한다.

```powershell
python -B workstreams/hanja_furigana_v0140/build_hanja_furigana_v0140.py
python -B -m unittest workstreams.hanja_furigana_v0140.tests.test_hanja_furigana_v0140 -v
python -B workstreams/hanja_furigana_v0140/apply_hanja_furigana_v0140.py
```

빌더는 Steam 설치본을 읽기만 한다. 추출한 후보와 원문 대조표는 `private/` 아래에만 만들며, 공개 operation ledger에는 ID·해시·한글 대체값만 넣는다. 적용 스크립트도 ledger에 기록된 Steam 원본 해시와 각 칸 해시가 전부 일치할 때에만 별도 후보 폴더를 만들고, Steam 경로를 직접 덮어쓰는 옵션은 제공하지 않는다.
