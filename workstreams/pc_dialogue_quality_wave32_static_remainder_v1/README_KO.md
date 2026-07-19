# PC 인물 대사 품질 Wave 32 — PK 잔여 정적 문장

현재 Steam PC `MSG_PK/JP/msggame.bin`에서 남아 있던 정적 대사 16개를
private 후보로 보정한다. 내용은 부정 의미 두 건, 성 함락 용어 열두 건,
생환 놀람 한 건, 요지 제압 한 건이다.

- 기준은 순정 PC Base/PK 일본어와 PC PK EN/SC/TC만 사용한다.
- Switch 파일·Switch 한국어·과거 한국어 산출물은 읽지 않는다.
- 각 PK 레코드는 현재 Steam 해시, PC 원문 대응 좌표, 원본 바이트코드 구조,
  활성 글꼴의 줄폭(최대 3줄·912px)을 고정해 검증한다.
- 필요한 정적 `0143` 활용 명령만 제거하고 그 밖의 비문자 바이트코드와 literal
  marker 구조는 보존한다.
- 빌더는 `tmp/pc_dialogue_quality_wave32_static_remainder_v1/`에만 후보를 쓰며,
  Steam 적용·Git·네트워크·릴리즈 기능이 없다.

이 후보는 인물 대사 전수 감사 완료를 주장하지 않는다. 런타임 토큰·UI 문맥이
필요한 보류군은 별도 실게임 검토 대상으로 남긴다.
