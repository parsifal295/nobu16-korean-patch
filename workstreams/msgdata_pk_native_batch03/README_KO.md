# PK `msgdata` 직접 번역 배치 03

배치 02의 마지막 ID 22643 다음부터 기존 소유 오버레이와 겹치지 않는 미번역 키를 오름차순으로 다시 분류했다. ID 22644~25004의 고정 접두부에서 실제 표시 의미가 있는 다음 250개를 번역했다. 내용은 PK 정책·특성 효과와 건의 해금 설명, 전략·공성전·이벤트 표제, 가신 심경, 고유 특성명과 합전 행동 설명이다.

같은 접두부의 나머지 203개는 번역문이 아닌 구조 항목으로 명시했다. `dummy` 자리표시자 23개, 발음·검색용 로마자 키 164개, printf·ESC·PUA·기호만으로 구성된 형식/제어 토큰 16개다. 선택 250개와 구조 제외 203개가 고정 접두부 453개를 빠짐없이 설명한다.

공식 PK JP/SC/EN/TC를 같은 ID로 대조했다. ID 23652는 EN만 순번 2를 생략하고, ID 23888은 EN만 `dummy`이므로 각각 JP/SC/TC의 일치 문맥을 우선했다. 공개 오버레이·증거·검토·검증 파일에는 공식 원문이나 완성 리소스를 넣지 않으며, SC의 printf, ESC, 제어문자, 줄바꿈, PUA, 가장자리 공백 계약을 모두 보존한다. 화면 검수 전이므로 250개 모두 `runtime_reviewed=false`다.

공유 `strdata` 행 추가로 대상 카탈로그 전체 파일 해시는 바뀌었다. 이 배치는 전체 파일 해시를 고정하지 않고 `MSG_PK/SC/msgdata.bin` 리소스 행의 정렬 키 독립 의미 해시 `458F6D95E8A2ECE17A6C49FFA1E3ED04DF8492347DEBD3EC157C23CCD5567510`과 대상 ID 해시 `B541D484A26F0B6F4306D46A344A29846331CEBC7C6381F18122F0A161C59D3E`만 검증한다. 따라서 관계없는 카탈로그 행 추가·변경은 결과물을 흔들지 않지만, `msgdata` 행 변경은 즉시 실패한다.

진행률 등록 검증은 미등록, 정확한 자기 등록, 서로 겹치지 않는 후속 배치 등록, 자기·후속 동시 등록을 모두 허용한다. 네 상태에서 생성물 바이트가 동일한지 테스트하며, 후속 오버레이가 기존 소유권·이 배치·다른 후속 배치와 겹치거나 대상 밖 ID를 쓰면 실패한다.

```powershell
python -B workstreams/msgdata_pk_native_batch03/build_msgdata_pk_native_batch03.py --out-root workstreams/msgdata_pk_native_batch03
python -B -m unittest workstreams.msgdata_pk_native_batch03.tests.test_msgdata_pk_native_batch03 -v
```

결정적 공개 산출물 SHA-256:

- 오버레이: `FAD7242A909EE205F1AF5D1D555208534E8A345095C94F386583CF2E59A22460`
- 정렬 증거: `66D3BDF8875077D66C936782F8F93A66B3E6B99B00B3AF5E322F8A52CF470829`
- 검토 인덱스: `679D34739BC04771FB33527E6CB39EE81A3481120755552C7D3797D991550C73`
- 생성 검증: `9DD844512ACA6261F5E53F5BBC7FF0C74FAE788B743E191A4726793C2C0BBFC6`
