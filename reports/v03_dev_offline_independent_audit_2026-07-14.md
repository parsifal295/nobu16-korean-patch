# P4 / Font-v4 v0.3-dev 독립 오프라인 감사

감사 일자: 2026-07-14 KST

## 판정

- 개발 마일스톤 오프라인 검증: **PASS**
- 공개 배포 승격: **금지**
- `release_eligible`: `false`
- `runtime_validation`: `pending`
- 알려진 런타임 차단 사유: 실제 SC 경로에서 성 이름이 세로로 표시됨
- 공개판 승격을 위해 새로 고정한 필수 증거: `castle_name_horizontal=true`
- canonical 공개 ZIP: 생성하지 않음

## 최종 canonical dev 상태

- 폴더: `KR_PATCH_WORK/releases/msgui_p4_file_only_v0.3-dev_2026-07-13`
- 파일 수: 17
- 정규화 트리 SHA-256: `05B306D045CC78058534A38C26B7B5D0BFCD4543DF67E4D720CE5B7FD5F72B14`
- manifest SHA-256: `11A9227D6F4EC7326B1AD108365028CE7433D02C33A332B4C76687ABD132EBFB`
- 패키지 내 검증 증거 SHA-256: `57213391521B922A7435ECB333ADD4EA8FA3CE5FF0E2487823A6C7AF997ECFC2`
- 설치기 SHA-256: `7FA3DD0EADF7A6498D91F5F2C19C8D773C9C783D0F547756628E9DFC46174E32`
- 최종 독립 오프라인 결과: `release_p4_vnext_offline_validation_final2_2026-07-14.json`
- 최종 독립 오프라인 결과 SHA-256: `2DE6F131BF4BBB8685E6CE60C65911695717A4096CDB544E9085D5FC8C36743D`

대상 산출물은 P4 메시지 SHA-256 `5E4B26FC465F4F0F4C046462714E7B677D7B479FDA6023086EF7F9A8817E6984`, Font-v4 SC 아카이브 SHA-256 `3BC57379D9AF95E83A77C96C1EE2D104AAF4A8BEA1733EA33FC3D1BCF056D1A9`로 고정되어 있다.

## 실행한 검사

- Windows PowerShell 5.1 구문 분석 5개: PASS
- template/package C# 두 쌍 독립 컴파일: PASS
- 패키지 `Verify`: PASS
- 실행 전 독립 allowlist/pin/static audit: PASS
- stock-only 격리 게임 루트 Apply: PASS
- 대상 메시지·폰트 해시 및 크기 검증: PASS
- journal과 stock backup 검증: PASS
- 격리 Restore: PASS
- bad-stock 선제 거부 및 입력 보존: PASS
- message-stock/font-target 혼합 상태 journal 복구: PASS
- `NOBU16PK.exe` 이름의 격리 helper 실행 중 Apply 거부: PASS
- runtime 미검증 dev의 기본 Apply 거부: PASS
- `castle_name_horizontal` 누락 또는 `false` runtime 증거의 release build 거부: PASS
- 실제 설치본 두 파일 불변: PASS

## hostile fixture

다음 10개 회귀 fixture가 모두 거부되었다.

1. allowlist recipe 경로에 완전한 상용 P4 `msgui` 대입
2. 완전한 상용 P4 `msgui`를 무시되는 Base64 JSON 필드에 은닉
3. 완전한 상용 P4 `msgui`가 든 미등록 중첩 ZIP
4. ZIP `..` traversal member
5. manifest 직접 중복 키
6. evidence 중첩 중복 키
7. JSON escape로 동일해지는 중복 키
8. 대소문자만 다른 manifest 키 충돌
9. marker 코드를 삽입한 설치기 변조; marker 실행 전에 외부 pin audit가 거부
10. 중복 키가 있는 builder evidence

검사 결과는 상용 완전 리소스, ZIP traversal/중첩 아카이브, 중복·escape·case-collision JSON 키, 실행 코드 변조를 모두 실행 전에 차단한다.

## 독립 재현성

동일 basename을 가진 독립 C/D dev build를 같은 검증 입력에서 각각 생성했다.

- 17파일 트리: byte-exact
- manifest SHA-256: `11A9227D6F4EC7326B1AD108365028CE7433D02C33A332B4C76687ABD132EBFB`
- 감사 전용 ZIP SHA-256: `84E21DA0661A78D64BC739763422857DC9DAE2CB9DDC7E6F3C2DFF18F39C9B37`
- 감사 전용 sidecar SHA-256: `089BA8E55311BE6BF4CBFC164202F3C38B1D2291C3886916309E80BC54D4D844`
- canonical dev 폴더와 독립 build 폴더: byte-exact
- 독립 ZIP audit: PASS

위 ZIP은 재현성 검사만을 위한 임시 dev 산출물이며 canonical 공개 ZIP으로 승격하지 않았다.

## 불변 확인

- 설치된 `MSG_PK/SC/msgui.bin`: `C2C69FDF09D9BE06E14F03C4F40562ADD0CA247EE0D50FC3E06EF501524B5E82`
- 설치된 `RES_SC/res_lang.bin`: `916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99`
- v0.2 폴더 트리: `7592BDB378BEB0A37CE9412C39B69CB5ED7826419140507BD46E2EAD5D6934A0`
- v0.2 ZIP: `58A66AF9311D120EA77E0E1F31D6D29E0D0E1CF8E15A28A51223B065214805F8`
- P4 canonical build 트리: `ABADC3D498479D51C5ECC6D37AB147097EEA3119CE8E8BC8D6B690180A6B4FC8`
- Font-v4 canonical 트리: `1C52B0EACA675269DF5A94AAFA345F10D4351F22E095F2C600E03A3651FEEE2F`
- 감사 종료 시 게임/런처 프로세스: 0

## 남은 차단 조건

오프라인 패키징은 통과했지만 성 이름의 세로 표시가 해결·검증되지 않았다. 따라서 `release_eligible=true`, 버전 `0.3`, 최종 공개 ZIP/sidecar 생성은 허용되지 않는다. SC 런타임에서 성 이름이 가로로 표시되는 화면 증거와 `castle_name_horizontal=true`를 포함한 일치하는 runtime evidence가 있어야만 builder가 공개판 승격을 허용한다.
