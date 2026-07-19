# Wave 39 — PC 정적 인물 대사 보정

PC 원문 대조와 독립 교차검토를 통과한 정적 인물 대사 41개를 private 후보로만
보정한다. Base 14개, PK 27개다.

- 인명·별칭과 조사 사이의 공백, 모음 뒤 조사, 붙어 있던 목적어, 일본식 쉼표,
  원문에서 빠진 정적 동작을 바로잡는다.
- 모든 대상은 `0143` 형태소 명령과 `02xx` 런타임 opcode가 없으며, literal 수,
  색/이름 marker, opaque span, 종료 코드, 수동 줄바꿈 수를 보존한다.
- PC JP 및 가능한 PC EN/SC/TC만 근거로 사용한다. Switch·과거 한국어는 읽지
  않는다.
- Base `6:4039`, `6:4045`는 정적 target 폭이 길고 Base renderer scale이 미해석이므로
  Steam 적용 전 실제 해당 UI 화면 QA가 필요하다. 다른 Base 레코드도 PK 폭 기준을
  끌어와 자동 통과 처리하지 않는다.
- PK `9:3880`은 보정 뒤 둘째 줄이 정적 상한인 912px에 정확히 닿으므로, Steam 적용 전
  실제 대사 화면에서 잘림·겹침 여부를 확인한다.
- `tmp/pc_dialogue_quality_wave39_static_dialogue_v1/candidate/` 아래 private 후보만
  생성한다. Steam 적용·Git·네트워크·릴리즈 기능은 없다.

원문 언어 간 의미가 갈리거나, 외부 이름 결합·레이아웃 위험이 남은 항목은 이 후보에
넣지 않고 보류한다.
