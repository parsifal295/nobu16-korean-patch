# Switch v1.3 화면 제목 → PC PK 오프라인 후보

Switch v1.3의 화면 제목 번역 픽셀을 PC `RES_SC/res_lang.bin`의 `/3/0..107`에
그대로 복사하지 않고, PC 전용 `GT1G0600`·BC3·raw-LZ4·LINK 구조로 다시
조립한다. 완성 후보와 PNG는 상용·제3자 픽셀을 포함하므로 `tmp/**/private/`에만
두며 Git에는 넣지 않는다.

## 현재 상태

108개 화면 제목의 의미 대응과 PC 전용 재조립을 완료한 오프라인 후보 A가 생성됐다.

- 같은 인덱스의 Switch 번역 재사용: 103개
- 다른 인덱스의 Switch 번역 재매핑: 3개 (`0 ← 3`, `24 ← 25`, `25 ← 24`)
- 서울한강체 M으로 새로 렌더한 보정 라벨: 2개 (`38`, `74`)
- 후보 SHA-256:
  `057E3B7E1BA426EAAAC1ABE3A7907DB7E750BDAD9419E87743C5A5612D1A6E62`
- 후보에서 108개 타이틀을 전부 다시 추출했으며, 외부 LINK의 비대상 엔트리와
  PC 전용 꼬리 엔트리 `108`, `109`가 그대로 보존됨을 확인했다.

후보와 재추출 PNG는 완전한 게임 리소스 및 제3자 번역 픽셀을 포함하는 비공개
검증 산출물이다. 공개 저장소나 배포본에 넣을 수 없다. 실제 게임 화면에서 위치,
크기, 가독성을 확인하는 런타임 QA는 아직 남아 있으므로 현재 결과는 배포 판정이
아니다.

전수 감사에서 확인한 예외는 다음과 같이 처리한다.

- 0: placeholder 대신 같은 의미인 Switch 3 `거래 내용 파악` 재사용
- 24/25: `요리코 선택`과 `요리키 일람`의 의미 순서에 맞게 서로 교환
- 15: PC 의미와 일치하는 기존 `연조`를 그대로 사용
- 37/38: 서로 같던 `부대 편제` 중 37은 유지하고 38만 `부대 편성`으로 구분
- 74: `휘 정보` 대신 `공주 정보`로 새 렌더

새 두 라벨은 공식 서울한강체 M을 사용해 결정적으로 렌더한다. 나머지 106개는
감사한 Switch v1.3 PNG를 사용하며, 그중 103개는 같은 인덱스에 두고 3개는 위의
의미 매핑에 따라 옮긴다. 모든 이미지는 해당 PC 원본 alpha bbox의
높이에 맞춰 premultiplied-alpha Lanczos3로 등비 확대·축소한 뒤, 왼쪽·위 잉크
원점에 맞춘 512×128 투명 캔버스에 합성한다. 이 배치는
오프라인 구조 검증용이며 실제 게임 화면 위치·크기 QA가 끝나기 전에는 배포 판정이
아니다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File `
  workstreams\pc_title_images_v13\rasterize_corrected_labels.ps1 `
  -FontPathInput tmp\third_party_fonts\SeoulHangangM.ttf `
  -OutputDirectory tmp\pc_title_images_v13\private\corrected

python -B tools\build_pc_title_images_candidate.py `
  --archive tmp\font_seoulhangang_v1_fullpk_switch_refresh_d\private\candidate\res_lang.SC.seoulhangang-v1.bin `
  --switch-png-root tmp\switch_title_pixel_audit\private\switch_v13 `
  --corrected-png-root tmp\pc_title_images_v13\private\corrected `
  --audit tmp\switch_title_pixel_audit\private\audit.json `
  --output-root tmp\pc_title_images_v13
```

빌더는 설치본을 읽기 전용으로도 요구하지 않는다. 로컬 후보나 검증된 백업을 입력으로
받으며 입력 해시를 전후 비교한다. 출력은 저장소 `tmp` 밖으로 쓸 수 없다.
