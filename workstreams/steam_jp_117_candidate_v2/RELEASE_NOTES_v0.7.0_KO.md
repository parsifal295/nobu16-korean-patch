# v0.7.0 변경 사항

대상은 Steam판 PK `1.1.7`(Steam build `18823764`)이며 일본어(`JP`) 경로 전용이다.
SC 리소스, 메모리 패치, DLL 주입, 후킹, EXE·레지스트리 변조는 사용하지 않는다.

## 번역 갱신

- `MSG_PK/JP/msggame.bin`: 28,272개 전체 적용, 일본어 의미 문자열 잔여 0개
- wave07 추가분: 4,061개 좌표, 5개 병렬 번역 배치 통합
- `MSG_PK/JP/msgui.bin`: 4,036개 매핑, 3,955개 실제 변경, 미매핑 1개
- 공통 메시지 5종: 39,507개 적용, 미해결 96개
- `MSG/JP/strdata.bin`: 24,524개 적용

## 폰트 갱신과 issue #41

- 48px·96px급 글리프: 서울한강 EB
- 32px·64px급 글리프: 서울한강 B
- 수요 카탈로그: 124개 소스, 88,062개 항목
- 코드포인트: 1,472개(한글 음절 1,251개)
- `RES_JP/res_lang.bin`: 154,216,023바이트,
  SHA-256 `0E2AF3F3A163814FEB87A38085DC41E76BD3D98CDB6CD616B232F814CE0D95A0`
- `RES_JP_PK/res_lang_pk.bin`: 141,746,742바이트,
  SHA-256 `EC758BC9B87F98B42E01CA6F841D963811BB944D113E2C65A1E9F5AE19F1DF08`
- `RES_JP_PK_PORT/res_lang_pk_port1.bin`: 79,243,911바이트,
  SHA-256 `00E9C1063ED164402AA70CB770100D8AE11A92B8024F20A4F1D89F2EA1A467F7`
- `RES_JP_PK_PORT/res_lang_pk_port2.bin`: 67,086,423바이트,
  SHA-256 `F18D99C4802AAB78C60C372FF0106ABD61ABDD8C026DC53CAE8FDE47C992C205`
- issue #41 실기 회귀 검증: 창모드 QHD PASS, 보더리스 QHD PASS
- 게임 완전 종료 후 콜드 재시작: 보더리스 QHD 타이틀·메인 메뉴 PASS

## 배포본

- 파일: `NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.7.0.zip`
- 크기: 356,144,243바이트
- SHA-256: `F245F23882BD9C676B705DCA9DA5E1443BEE05EA88A12F7BA9E7692BEA100584`
- 검증 계약 SHA-256:
  `C98F6CDD5A7E1FDAD1F93DE4BCA2C95A47A9DF4D1371EC90A2523F8EFD4F52DD`
- 내용: 원래 폴더 구조와 파일명을 보존한 JP 경로 파일 정확히 12개
- 폴더: `MSG/JP`, `MSG_PK/JP`, `RES_JP`, `RES_JP_PK`, `RES_JP_PK_PORT`의
  정확히 5개
- 제외: `RES_JP_PK_PORT/res_lang_pk_port3.bin`은 ZIP에 포함하지 않으며
  설치 시 덮어쓰지 않음
- `MSG_PK/JP/msggame.bin` SHA-256:
  `6316E2B288F798B747D983DB08E6C2A477C6FC60DE319D3C7C302102C6384A84`

현재 수치는 추적된 exact-12 검증 핀과 일치한 배포 결과이며, ZIP의 12개 멤버는
후보 파일과 크기·SHA-256이 전부 일치한다. Steam PK 1.1.7 실기 적용, 게임 실행,
창모드·보더리스 QHD 화면 검증과 콜드 재시작 검증까지 완료했다.
