# Steam JP 이미지형 텍스트 다음 우선군 감사 v1

이 workstream은 Steam 1.1.7 **일본어 경로**의 다음 래스터 텍스트 대상을
읽기 전용으로 조사한 결과다. 후보 파일이나 이미지 번역본은 만들지 않으며,
게임 폴더에 쓰지 않는다.

| ID | PC JP 경로 | nested slot | 형식/크기 | 예상 화면 |
| --- | --- | ---: | --- | --- |
| `base_boot_warning` | `RES_JP/res_lang.bin /1` | 6 | G1T `0x01`; 2048×2048 3장, 4096×4096 3장 | 기동 직후 부트 경고·고지 |
| `base_historical_title_cards` | `RES_JP/res_lang.bin /4` | 105 | BC3 `0x5B`; 각 1024×256 | 본편 역사 전투/이벤트 제목 카드 |
| `pk_mixed_menu_labels` | `RES_JP_PK/res_lang_pk.bin /18` | 43 | BC3 `0x5B`; 각 512×128 | PK 혼합 메뉴·콘텐츠 라벨 |
| `pk_historical_episode_title` | `RES_JP_PK/res_lang_pk.bin /21` | 33 | BC3 `0x5B`; JP 1024×256, SC에는 2048×256 3장 포함 | PK 역사 에피소드/이벤트 제목 카드 |

`audit.v1.json`은 slot별 wrapper/raw/G1T/payload **SHA-256과 구조 메타데이터**만
담는다. 원본 `bin`, G1T/BC 바이트, 디코드 PNG, Switch 번역 픽셀은 저장소에 넣지
않는다. 각 PC 입력은 읽기 전/후 SHA-256을 비교해 동일함을 기록하므로, 감사 실행이
게임 파일을 변경하지 않았다는 입력 무결성 증거도 남긴다.

## 핵심 판정

- JP와 SC는 네 대상 모두 원본 G1T raw hash가 슬롯 단위로 전부 다르다.
  따라서 중국어 리소스를 덮어쓰거나 파일 전체를 언어 간 복사하는 방식은 사용할 수 없다.
- Switch v1.3와 v2.0에 들어 있는 `RES_JP/res_lang.bin`은 member SHA가
  `79B572CE…651159`로 byte-identical이다. `/1`과 `/4`의 **번역 참고**에는 쓸 수
  있지만, PC G1T/LINK/wrapper와 구조·해상도가 다를 수 있으므로 Switch 바이트를
  PC에 복사하면 안 된다. 특히 `/1`은 PC physical slot 6개와 달리 Switch가
  physical 4개·virtual 2개이며, `/4`는 105개 슬롯 수는 같아도 raw/payload hash가
  105개 모두 다르다.
- 두 Switch 배포본에는 `RES_JP_PK/res_lang_pk.bin`이 없다. 따라서 `/18`, `/21`은
  Switch 직접 이식원이 없으며, 한국어 문구 확정과 PC 전용 렌더가 선행돼야 한다.
- `/1`은 현재 PC BC1/BC3 재인코더가 다루지 않는 `0x01` format이다. pixel codec 및
  extra-header 계약을 검증하기 전에는 구현 대상으로 올리지 않는다.

## 구현 시작 전 필수 게이트

1. 실제 런타임 파일 open trace와 화면 캡처로 slot→화면을 확정한다.
2. PC JP 1.1.7의 대상 outer/inner LINK, raw-LZ4, G1T를 기준으로만 재조립한다.
3. `/4`는 105개 이벤트 카드의 의미·용어·ink origin을 개별 검토한다.
4. `/18`, `/21`은 자체 한국어 렌더 설계와 PK 화면 검증 뒤에만 후보를 만든다.
5. 후보는 private `tmp`에서 재추출/구조 검증/화면 QA를 통과한 뒤, 게임 종료 상태에서
   복원 가능한 트랜잭션으로만 적용한다.

이 감사는 메모리 패치, DLL 주입, 후킹, EXE/레지스트리 변경을 사용하지 않는다.

## 재현

```powershell
$py = 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'

& $py -B workstreams\steam_jp_image_text_audit_v1\build_steam_jp_image_text_audit.py audit `
  --game-root F:\SteamLibrary\steamapps\common\NOBU16 `
  --switch-v13-zip tmp\third_party_switch_v13\NobunagaShinsei_KoreanPatch_v1.3.zip `
  --switch-v20-zip tmp\third_party_switch_v20\NobunagaShinsei_KoreanPatch_v2.0.zip

& $py -B workstreams\steam_jp_image_text_audit_v1\build_steam_jp_image_text_audit.py verify
& $py -B -m unittest workstreams\steam_jp_image_text_audit_v1\test_steam_jp_image_text_audit_v1.py -q
```

`audit` 명령은 audit JSON만 갱신한다. 지정한 게임 경로의 파일은 읽기만 한다.
