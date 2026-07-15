# PK `msgdata` 직접 번역 배치 01

현재 진행률에 등록된 `msgdata` 오버레이와 exact target catalog의 차집합을 오름차순으로 검토해, 실제 표시 의미와 PK/SC 런타임 계약을 확정할 수 있는 첫 100개를 직접 번역했다. 선택 ID는 15063~18157 사이에 있으며 100개 ID의 SHA-256은 `865614726A3D3F6466D084AE5496F0941EEA38F629A36C332BCCFEE4A33ED658`이다.

그보다 앞선 미번역 target을 무조건 세지 않았다. 인명 조각·발음과 관직 독음이 불확정한 55개, 평가 기호 3개, `dummy` 자리표시자 62개, 로마자 검색키 11개, 소유 화면을 확정할 수 없는 짧은 단편 8개 등 모두 139개를 명시적으로 제외했다. 제외 ID 집합의 SHA-256은 `D31AF7B3E2D358EDFC5AAA49E488C91DFFE2BA46B195E2C614A27568FAF613EC`이다. 빌더는 이 239개 untranslated target prefix가 바뀌면 실패한다.

번역 범위는 시나리오 개요, 사건명·특성명, 오다 노부나가 서술 일부, 세키가하라 전초와 제1차 우에다성 전투 서술이다. PK 공식 JP/SC/EN/TC를 같은 ID로 대조했으며, JP가 빈 추가 행은 SC·EN·TC의 합치 문맥만 사용했다. Switch v1.3도 다시 역색인했으나 이 100개에 재사용 가능한 한국어 대응문은 0개였다.

모든 행은 원본 SC의 printf, ESC, 일반 제어문자, 개행 수, PUA, 앞뒤 공백, 사용자 정의 대괄호 토큰을 그대로 보존한다. 선택 100개는 기존 오버레이 고유 ID 20,830개와 겹치지 않고 exact target 안에만 있다. 공개물에는 공식 원문이나 완성 게임 리소스가 없으며 화면 검수 상태는 아직 `runtime_reviewed=false`다.

```powershell
python -B workstreams/msgdata_pk_native_batch01/build_msgdata_pk_native_batch01.py --out-root workstreams/msgdata_pk_native_batch01
python -B -m unittest workstreams.msgdata_pk_native_batch01.tests.test_msgdata_pk_native_batch01 -v
```
