# Switch v1.3 기반 PK `msgev` 직접 재구성 13건

자동 구조 복구가 의도적으로 제외한 정확한 13개 ID를 공식 PK SC·JP·EN·TC와
Switch v1.3의 동일 일본어 매핑을 읽기 전용으로 대조한 뒤 한국어로 직접
재구성한다. Switch 한국어 문구를 그대로 복사하지 않고, SC 가로쓰기 런타임이
요구하는 ESC 개수·순서와 사용자 정의 괄호 토큰 순서를 기준으로 문장 전체를 다시
썼다.

## 결과

- 대상: `6829, 6833, 7027, 7633, 7823, 7953, 8094, 8642, 8959, 9331, 9336, 9340, 10888`
- 직접 번역·재구성: 13건
- 의미 확정 불가: 0건
- 기존 모든 `msgev` 오버레이와 겹침: 0건
- 정확한 PK SC 번역 대상 밖 항목: 0건
- 선택 ID SHA-256: `FBEB52131D74798885BD0BC311399EB1F054EFB0CB716BE8DFE0AD1133897C72`
- 공개 오버레이 SHA-256: `92767CB6E1C0BB890F185F611B3055A2E75370D544370A0AEDF08B8AAC6FDE07`

12건은 이름·지명 색상 토큰의 추가/삭제, 엔티티 순서 변경, 동적 괄호 토큰의 PC
SC 순서 복원으로 해결했다. ID `10888`은 JP·EN·Switch 문맥과 SC·TC 문맥이 서로
달랐다. 실제 SC 경로의 제어 계약을 훼손하지 않도록 SC와 TC가 공통으로 채택한
야마자키·덴노잔 전투 도입 문맥을 한국어로 새로 번역했다.

## 산출물

- `public/msgev_ko_switch_v13_native_contract_recovery_13.v1.json`
- `evidence/switch_v13_msgev_native_contract_recovery_alignment.v1.json`
- `review/switch_v13_msgev_native_contract_recovery_review.v1.json`
- `validation.v1.json`

공개 증거에는 공식 원문 대신 UTF-16LE SHA-256만 들어 있다. 완성 게임 리소스는
출력하지 않으며, SC 원본에 13개 값을 적용한 결과는 메모리에서만 재구성·재파싱한다.

## 고정 검증

빌더와 테스트는 다음 조건을 실패 시 즉시 중단한다.

1. 공식 PK SC·JP·EN·TC 및 Switch v1.3 입력의 packed/raw 핀
2. 선행 구조 복구가 제외한 정확한 13개 ID 집합
3. source-free 번역 대상 카탈로그 안의 ID이며 기존 오버레이와 불겹침
4. printf, ESC, 제어문자, 줄바꿈, PUA, 앞뒤 공백, 사용자 정의 괄호 순서 보존
5. 모든 한국어 값의 한자·가나 0개와 의미 있는 한글 포함
6. 자기 오버레이 등록 전·후 바이트 동일 산출물
7. 격리 2회와 최종 1회의 바이트 동일 생성 및 메모리 재구성 A/B 일치

## 실행

```powershell
python -B workstreams/switch_msgev_v13_native_contract_recovery/build_switch_msgev_v13_native_contract_recovery.py
python -B -m unittest discover -s workstreams/switch_msgev_v13_native_contract_recovery/tests -p "test_*.py" -v
```

이 워크스트림은 루트 진행률·README·폰트·설치된 게임 파일을 수정하거나 배포·커밋·
푸시하지 않는다.
