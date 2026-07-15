# PK `msgdata` 직접 번역 배치 06

배치 05까지의 모든 소유 ID를 제외하고 `MSG_PK/SC/msgdata.bin`에 남은 일반 의미 문자열 278개를 전부 직접 한국어로 번역했다. 대상은 ID `2086~29208`에 흩어진 이름·가문명·전법명·개발 조건·공적·지역 통일·업적 조건·효과 문구다.

당초 다음 300개를 목표로 했으나 실제 일반 의미 문자열 잔여는 278개뿐이었다. 이 배치를 적용하면 직접 번역 가능한 일반 의미 문자열은 0개가 된다. 남은 4,110개는 `dummy` 1,759개, 로마자·음가 조회 키 2,331개, 포맷·제어 전용 토큰 20개로 모두 구조 제외 근거를 고정했다.

공식 PK JP/SC/EN/TC를 같은 ID로 대조했으며 공개 파일에는 공식 원문이나 완성 리소스를 넣지 않는다. SC 원문 해시와 printf·ESC·PUA·제어문자·줄바꿈·앞뒤 공백을 검증한다. 반복 SC 원문 33개 그룹은 동일한 한국어 번역을 사용한다. 화면 검증 전이므로 278개 모두 `runtime_reviewed=false`다.

재생성과 검증:

```powershell
python -B workstreams/msgdata_pk_native_batch06/build_msgdata_pk_native_batch06.py --stock-pk-sc <원본_MSG_PK_SC_msgdata.bin> --out-root workstreams/msgdata_pk_native_batch06
python -B -m unittest workstreams.msgdata_pk_native_batch06.tests.test_msgdata_pk_native_batch06 -v
```

결정적 공개 산출물 SHA-256:

- 오버레이: `53A64CC10C28D48A829F984FEAB3D3F3A27318C2E5A3EE814DF39380EF8DF181`
- 정렬 증거: `472897363F1A2B2A86339F1DE67C892EEC45E010FAA0E058E9A3B0243C15F097`
- 검토 인덱스: `71B8AEEC7CBA3B3B28E78A5230728B54B973305651015EC9752514B5831828A8`
- 생성 검증: `0FEC13B11C1485BE8222C2ED32015F12E286210491FA4E2F1FC33C0386DD55DD`
