# PK `msgdata` 수동 계약 복구 2개

Switch v1.3 자동 복구에서 안전상 제외한 ID 22594와 25546을 PK 공식 JP/SC/EN/TC 문맥으로 다시 판정한 독립 배치다. 전체 게임 리소스나 공식 원문은 공개 산출물에 넣지 않는다.

- 22594: SC와 TC의 의미·형식 계약이 일치하고 JP/Switch 의미는 상충한다. SC 런타임을 기준으로 `성하 시설 <강조 %s>의 상업%+d`로 새로 번역했으며 ESC 강조 2개, `%s`, `%+d`를 그대로 보존했다.
- 25546: JP는 동적 수치가 있는 부대 능력 효과지만 SC/EN/TC는 모두 인자 없는 자리표시자다. 검증되지 않은 `%d`를 추가하지 않고 `부대 능력 증가`로 의미만 복구했다. 수치 생략은 안전 선택이며 화면 검수가 필요하다.

두 ID는 원본 SC의 nonblank 정확한 진행률 대상이고 기존 `msgdata` 오버레이 고유 ID 20,828개와 겹치지 않는다. 이 수는 기존 오버레이 합집합의 충돌 검사 기준일 뿐 stock-visible 진행률 수치가 아니다. 빌더는 네 공식 언어 리소스와 행 해시를 고정하고, printf/ESC/control/newline/PUA/가장자리 공백/사용자 정의 대괄호 계약을 검사한다. 진행률에 등록되기 전과 자기 오버레이가 정확히 한 번 등록된 뒤 모두 동일한 결과를 재생성한다.

```powershell
python -B workstreams/msgdata_pk_native_completion/build_msgdata_pk_native_completion.py --out-root workstreams/msgdata_pk_native_completion
python -B -m unittest workstreams.msgdata_pk_native_completion.tests.test_msgdata_pk_native_completion -v
```
