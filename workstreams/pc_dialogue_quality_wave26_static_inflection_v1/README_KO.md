# PC 대사 품질 Wave 26 — 정적 어미·문맥 보정

Wave 26은 완성된 Wave 25 private 후보의 정확한 11파일 profile을 유일한 입력으로 고정한다. 본편 `MSG/JP/msggame.bin`과 PK `MSG_PK/JP/msggame.bin`에서 지정된 20개 Base→PK 대화쌍, 총 40개 레코드만 재구성한다.

각 레코드는 기존 literal marker 수와 수동 줄 수를 유지하고, 완결된 정적 `01 43` 제어 명령만 제거한다. 그 밖의 opaque bytes와 `05 05 05` 종단은 보존한다. 활성 PC JP 폰트 기준 모든 줄은 912px 이하여야 한다.

근거는 PC 원본 Base/PK JP 및 PC EN/SC/TC 문맥 파일만 사용한다. Switch 경로·Switch 한국어는 읽거나 사용하지 않는다.

후보 생성 위치는 `tmp/pc_dialogue_quality_wave26_static_inflection_v1` 아래로 제한된다. Steam 적용, Git staging/commit/push, 릴리스 생성은 이 작업의 범위가 아니다.
