# PC-only `strdata` / `msgdata` 앵커 재감사 v1

이 작업은 현재 PC 한국어를 검사 대상만으로 사용한다. 번역 판단의 근거는 순정 PC 일본어와, 가능한 범위의 PC EN/SC/TC 동일 좌표뿐이다.

- Switch 한국어와 과거 한국어 리소스는 읽지 않는다.
- 일반 품질 overlay의 한국어 문자열은 읽거나 해석하지 않는다. 공개 overlay 바이트에서는 ASCII `name`/`coordinate` 필드만 추출해 이미 대기 중인 좌표를 제외한다.
- Steam 설치본, 일반 overlay, 릴리스, Git 상태는 쓰지 않는다.

검사 대상은 `MSG/JP/strdata.bin` 32,311좌표와 `MSG_PK/JP/msgdata.bin` 29,218좌표다. 후보는 아래 조건을 모두 만족할 때만 만든다.

1. 대상과 현재 PC 한국어 앵커가 순정 JP 및 가능한 모든 PC EN/SC/TC 문맥에서 완전히 같은 서명을 가진다.
2. 앵커의 한국어 본문을 대상의 외곽 공백만 보존하여 이식해도 런타임 토큰, printf, ESC, 줄바꿈, 제어문자 계약이 변하지 않는다.
3. 후보의 동아시아 셀 수가 현재 대상보다 길어지지 않고, 후보 글리프는 현재 PC 한국어 코퍼스에 이미 있다.
4. 대상과 앵커 모두 현재 generic quality overlay 좌표가 아니다.

이 조건은 이름·지명·집단명에서 PC 영어 로마자 표기까지 정확히 같은데 한국어 독음만 다른 경우를 대상으로 한다. 셀 수 검사는 정적 안전장치일 뿐 실제 UI 렌더링 완료 주장은 아니다.

실행:

```powershell
$py = 'C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe'
& $py -B workstreams\translation_quality_strdata_msgdata_pc_anchor_reaudit_v1\build_pc_anchor_reaudit_v1.py --write
& $py -B workstreams\translation_quality_strdata_msgdata_pc_anchor_reaudit_v1\build_pc_anchor_reaudit_v1.py --validate
```

생성물은 모두 `tmp/translation_quality_strdata_msgdata_pc_anchor_reaudit_v1/` 아래에 둔다. `validation.v1.json`은 한국어·일본어 원문을 포함하지 않는 source-free 검증 요약이다.
