# PK `msgdata` 직접 번역 배치 02

배치 01의 마지막 ID 18157 다음부터 기존 오버레이와 겹치지 않는 정확한 번역 대상 키를 다시 훑었다. ID 18158~22643 구간에서 실제 표시 의미가 있는 150개를 모두 골라 번역했다. 앞쪽 75개(18158~18232)는 아자이 나가마사의 최후, 고마키·나가쿠테 전투, 오사카 여름 전투를 다룬 연속 이벤트 서사다. 나머지 75개는 PK의 건의·평정중·정책·효과 명칭과 설명이다.

같은 구간에서 번역 대상으로 잡혀 있으나 실제 표시 문장이 아닌 1,728개도 명시적으로 분류했다. `dummy` 자리표시자 1,642개와 발음·검색용 로마자 키 86개이며, 선택한 150개와 이 구조 항목을 합치면 해당 미번역 구간 전체를 빠짐없이 설명한다. 이 구조 키들은 번역 오버레이에 넣지 않았고, 진행률 분모에서 제외할지는 별도의 카탈로그 정책 검토가 필요하다.

공식 PK JP/SC/EN/TC를 같은 ID로 대조했다. ID 21672~21681은 JP만 서로 다른 건의 해금 의미를 담고 있지만 SC와 EN에는 관계없는 동일 문구가 반복되고 TC는 `dummy`다. 이 10개는 JP 의미를 기준으로 번역하되 실제 SC 행의 형식 계약은 그대로 보존했다. ID 22625와 22626도 JP·EN·TC와 달리 SC에 동적 수치 인자가 없으므로 검증되지 않은 printf 인자를 추가하지 않았다.

Switch v1.3 역색인에서도 150개에 재사용 가능한 한국어 후보는 0개였다. 공개 오버레이·증거·검토 파일에는 공식 원문이나 완성 게임 리소스를 넣지 않는다. 모든 항목은 SC의 printf, ESC, 제어문자, 줄바꿈, PUA, 가장자리 공백 계약을 보존하며 화면 검수 전 상태인 `runtime_reviewed=false`다.

```powershell
python -B workstreams/msgdata_pk_native_batch02/build_msgdata_pk_native_batch02.py --out-root workstreams/msgdata_pk_native_batch02
python -B -m unittest workstreams.msgdata_pk_native_batch02.tests.test_msgdata_pk_native_batch02 -v
```
