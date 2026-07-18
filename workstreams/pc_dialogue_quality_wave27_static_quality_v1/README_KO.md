# PC 대사 품질 Wave 27 — 정적 시설·복구 대사 보정

Wave 27은 완성된 Wave 26 private 후보의 정확한 11파일 profile만을 입력으로 사용한다. 본편 및 PK `msggame`에서 지정된 20개 Base→PK 쌍, 총 40개 레코드만 재구성한다.

기존 두 literal 경계와 수동 3줄 개행은 보존한다. 완결된 정적 `01 43` 제어 명령만 제거하며, 나머지 opaque bytes와 `05 05 05` 종단을 보존한다. 활성 PC JP 폰트에서 모든 줄은 912px 이하여야 한다.

근거는 PC JP Base/PK 및 PC EN/SC/TC 문맥만 사용한다. Switch 경로나 Switch 한국어는 읽거나 사용하지 않는다. Steam 적용, Git staging/commit/push, 릴리스 생성은 범위 밖이다.
