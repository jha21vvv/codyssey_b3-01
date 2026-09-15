# 🛠️ 클라우드 인프라 트러블슈팅 보고서 (Troubleshooting Report)

본 보고서는 `codyssey_b3-01` 프로젝트 인프라 구축 과정에서 발생한 실제 기술적 장애 및 보안 권한 오류를 **[증상 → 가설 → 검증 → 조치 → 결과 → 재발 방지]**의 6단계 엔지니어링 프레임워크에 따라 체계적으로 분석하고 해결한 내역을 기록한 문서입니다.

---

## 📑 목차
1. [트러블슈팅 개요 및 문제 해결 프레임워크](#-트러블슈팅-개요-및-문제-해결-프레임워크)
2. [사례 1: IAM 최소 권한 설정에 따른 콘솔 조회 권한 누락 (DescribeDhcpOptions 등)](#-사례-1-iam-최소-권한-설정에-따른-콘솔-조회-권한-누락-describedhcpoptions-등)
3. [사례 2: 웹 서비스 접속 불가(ERR_CONNECTION_TIMED_OUT) 및 보안 그룹/ENI 수정 권한 오류](#-사례-2-웹-서비스-접속-불가err_connection_timed_out-및-보안-그룹eni-수정-권한-오류)
4. [IAM 정책 변경 이력 총괄 (최초안 → 1차 수정 → 2차 완성본)](#-iam-정책-변경-이력-총괄)
5. [결론 및 시니어 엔지니어링 교훈](#-결론-및-시니어-엔지니어링-교훈)

---

## 🎯 트러블슈팅 개요 및 문제 해결 프레임워크

클라우드 환경에서 "최소 권한의 원칙(Principle of Least Privilege)"을 적용하는 것은 보안상 필수적이지만, 실제 개발 및 콘솔 운영 과정에서 예측하지 못한 권한 부족이나 설정 실수가 발생하기 쉽습니다.  
본 프로젝트에서는 문제 발생 시 단순한 시행착오가 아닌 논리적인 문제 해결 사이클을 거쳤습니다.

```
[1. 증상 식별 (Symptom)] ──> [2. 원인 가설 수립 (Hypothesis)] ──> [3. 가설 검증 (Verification)]
                                                                               │
[6. 재발 방지 (Prevention)] <── [5. 결과 검증 (Result)] <── [4. 해결 조치 (Action)] ┘
```

> 💡 **3개월 차 주니어 개발자를 위한 꿀팁: 왜 이 6단계가 중요한가요?**
> * 코딩 초보 시절에는 에러가 발생하면 "어? 왜 안 되지?" 하고 무작정 에러 문구를 구글에 복사해서 남의 코드를 복붙하기 쉽습니다.
> * 하지만 현업 시니어 엔지니어는 마치 **의사가 환자를 진찰하듯** 단계적으로 접근합니다:
>   1. **증상**: 환자가 어디가 아픈가? (빨간 에러창 발생, 브라우저 타임아웃)
>   2. **가설**: 이 증상이면 감기(권한 누락)일까, 체한 것(포트 불일치)일까?
>   3. **검증**: 혈액 검사(로그/설정값 확인)로 내 가설이 맞는지 팩트 체크
>   4. **조치**: 알맞은 약 처방(정확한 정책 코드 수정)
>   5. **결과**: 환자가 완치되었는가? (새로고침 시 정상 렌더링 확인)
>   6. **재발 방지**: 다음번에 같은 병에 안 걸리려면 어떻게 해야 할까? (원칙 정립)
> * 이 사고방식이야말로 에러 앞에서 당황하지 않는 든든한 무기가 됩니다!

---

## 🚨 사례 1: IAM 최소 권한 설정에 따른 콘솔 조회 권한 누락 (DescribeDhcpOptions 등)

### 1. 증상 (Symptom)
* 실습 전용 IAM 계정(`codyssey-b3-user`)으로 AWS 웹 콘솔에 로그인한 뒤 VPC 메뉴로 이동하자, 화면 상단에 붉은색 경고 배너와 함께 다수의 API 호출 실패 오류가 연달아 발생함.
* **오류 메시지**:
  1. `다음 작업을 수행하지 못함: DescribeDhcpOptions`  
     (`User: arn:aws:iam::388094502979:user/codyssey-b3-user is not authorized to perform: ec2:DescribeDhcpOptions because no identity-based policy allows the ec2:DescribeDhcpOptions action`)
  2. `리소스를 로드하는 중 오류가 발생했습니다: ec2:DescribeNatGateways`
  3. `VPC(vpc-039bf298cd5b870a5)를 로드하는 동안 오류가 발생했습니다: ec2:DescribeNetworkAcls`

#### 📸 증상 스크린샷
* **(1) VPC 목록 접속 시 DescribeDhcpOptions 오류 발생**
  ![VPC 대시보드 DescribeDhcpOptions 오류](./t1%20(1).png)
* **(2) VPC 상세 진입 시 DescribeNatGateways 및 DescribeNetworkAcls 연쇄 오류**
  ![VPC 상세 로드 오류](./t1%20(2).png)

> 💡 **3개월 차 눈높이 해설: `DescribeDhcpOptions`가 도대체 뭐길래 빨간 에러가 뜰까요?**
> * 우리가 쓰는 AWS 콘솔은 사실 하나의 **웹사이트(프론트엔드)**입니다.
> * 네이버나 쇼핑몰에 들어가면 웹 브라우저가 화면을 그리기 위해 서버에서 상품 목록, 광고 배너, 프로필 사진 등을 한 번에 긁어오는 것처럼, AWS 콘솔도 화면을 그리기 위해 뒤에서 수십 가지 정보를 AWS 서버에 물어봅니다.
> * 그중 하나가 "이 VPC의 DHCP(네트워크 자동 IP 할당 설정) 옵션은 뭐야?"라고 물어보는 `DescribeDhcpOptions`입니다.
> * 그런데 우리 IAM 계정에는 이 단순 질문 권한이 없어서, AWS 웹사이트가 화면 일부분을 그리지 못하고 "나 이거 못 읽어왔어!"라며 빨간 에러를 뿜었던 것입니다.

---

### 2. 가설 수립 (Hypothesis)
* **가설**: 최초 작성한 IAM 최소 권한 정책(`CodysseyB3LeastPrivilegePolicy`)은 VPC, 서브넷, 인터넷 게이트웨이 등의 핵심 리소스 생성/조회(`DescribeVpcs`, `DescribeSubnets` 등)만 명시적으로 등록함.
* 그러나 AWS 웹 콘솔 UI는 리소스 간의 연관 정보(DHCP 옵션 세트, NAT 게이트웨이, 네트워크 ACL 등)를 화면에 렌더링하기 위해 사용자가 의도하지 않은 수십 가지의 보조 조회(Describe) API를 백그라운드에서 비동기 호출함.
* 이로 인해 읽기 전용 API 권한이 부족하여 웹 브라우저 콘솔 렌더링이 실패하고 에러 배너가 출력되었을 것이다.

---

### 3. 검증 (Verification)
* **API 오류 로그 분석**: 발생한 모든 에러가 상태를 변경하거나 비용을 유발하는 명령이 아니라, 오직 현 상태를 읽어오는 **`ec2:Describe*` 계열의 읽기 전용(Read-only) API**에만 국한됨을 확인함.
* **보안 위험도 검토**: `Describe*` 작업은 단순히 인프라 메타데이터를 조회할 뿐, 새로운 인스턴스를 생성하거나(RunInstances), VPC를 변경하거나, 과금을 유발하는 행위가 전혀 불가능함. 따라서 조회 권한을 포괄적으로 허용해도 과금 위험 0%, 인프라 훼손 위험 0%임을 검증함.

> 💡 **3개월 차 눈높이 해설: `Describe` 권한은 왜 100만 번을 줘도 안전하고 과금이 0원인가요?**
> * AWS API는 크게 **[읽기(Read)]**와 **[쓰기(Write)]** 두 가지로 나뉩니다.
> * **읽기(`Describe`, `Get`, `List`)**: "현재 상태가 어떤지 목록만 쳐다보기". 도서관에서 책 목록을 100만 번 검색한다고 도서관 책이 닳거나 돈을 내지 않는 것과 같습니다. (비용 0원, 위험도 0%)
> * **쓰기(`Create`, `Run`, `Delete`, `Terminate`)**: "새 컴퓨터를 켜거나(과금 발생!), 기존 네트워크를 삭제하기". 도서관에서 책을 사서 꽂거나 책을 찢어버리는 행위입니다.
> * 따라서 `Describe*`를 넓게 열어주는 것은 보안 구멍이 아니라, 콘솔을 편리하게 보기 위한 안전한 실무 패턴입니다!

---

### 4. 조치 (Action)
루트(Root) 계정으로 IAM 콘솔에 접속하여 `CodysseyB3LeastPrivilegePolicy` 정책에 읽기 전용 권한을 전담하는 신규 구문(`AllowAllEC2AndVPCReadOnlyDescribe`)을 추가하고, `"Action": ["ec2:Describe*"]`를 부여함.

```json
// 추가된 읽기 전용 정책 구문
{
  "Sid": "AllowAllEC2AndVPCReadOnlyDescribe",
  "Effect": "Allow",
  "Action": [
    "ec2:Describe*"
  ],
  "Resource": "*"
}
```

> 💡 **3개월 차 눈높이 해설: `ec2:Describe*`의 별표(`*`)는 무슨 마법인가요?**
> * 프로그래밍에서 별표(`*`)는 **"아무 글자나 다 된다"는 와일드카드(Wildcard)**입니다.
> * `ec2:DescribeVpcs`, `ec2:DescribeSubnets`, `ec2:DescribeDhcpOptions`, `ec2:DescribeNatGateways` 등등 'Describe'로 시작하는 수백 개의 복잡한 조회 명령어들을 하나하나 적을 필요 없이, `ec2:Describe*` 딱 한 줄로 전부 허용해 준 것입니다!

* **시니어 엔지니어링 설계 포인트**:
  * 생성/삭제/실행(`Create*`, `Delete*`, `RunInstances`) 권한은 아래 구문에서 철저히 핀포인트로 통제 유지.
  * 읽기 권한만 시원하게 열어주는 **"조회와 쓰기의 권한 분리(Separation of Read/Write Permissions)"** 모범 사례를 적용.

---

### 5. 결과 (Result)
* IAM 사용자 창으로 돌아와 VPC 대시보드를 새로고침(F5)한 결과, 빨간색 에러 배너가 완전히 사라지고 VPC 상세 정보 및 리소스 맵이 정상적으로 로드됨.

#### 📸 결과 스크린샷
* **Describe* 권한 추가 후 VPC 리소스 맵 및 상세 정보 정상 렌더링**
  ![VPC 리소스 맵 로드 성공](./t1%20(3).png)

---

### 6. 재발 방지 (Prevention)
* **도서관 비유를 통한 권한 체계 정립**:
  * *도서관 목록 검색(Describe)*: 하루에 100만 번을 검색해도 도서관 책이 손상되거나 돈이 들지 않으므로 폭넓게 허용(`ec2:Describe*`).
  * *책 대출/구매/폐기(Create/Run/Delete)*: 비용과 자원에 직결되므로 철저히 승인된 작업만 한정 허용.
* **현업 표준 가이드라인**: IAM 최소 권한을 설계할 때 모든 콘솔 조회 API를 일일이 수작업으로 등록하는 비효율을 지양하고, 조회 계열(`Describe*`)은 포괄 허용하되 변경/과금 유발 액션만 화이트리스트로 제한하는 보안 정책 템플릿을 표준화함.

---

## 🚨 사례 2: 웹 서비스 접속 불가(ERR_CONNECTION_TIMED_OUT) 및 보안 그룹/ENI 수정 권한 오류

### 1. 증상 (Symptom)
* EC2 인스턴스에 Nginx 웹 서버를 설치하고 가동한 뒤, 서버 내부 로컬 터미널에서는 `curl -I http://localhost`가 `HTTP 200 OK`로 정상 응답함.
* 그러나 외부 사용자 환경(크롬 웹 브라우저)에서 퍼블릭 IP `http://3.36.130.0`으로 접속을 시도하자, **`사이트에 연결할 수 없음 (3.36.130.0에서 응답하는 데 시간이 너무 오래 걸립니다. ERR_CONNECTION_TIMED_OUT)`** 에러가 발생하며 웹페이지가 열리지 않음.
* 원인을 해결하기 위해 보안 그룹(`codyssey-web-sg`)의 인바운드 규칙을 수정하려 했으나, 규칙 저장 시 **`ModifySecurityGroupRules` 권한 부족 에러**가 발생함.
* 인스턴스에서 신규 보안 그룹으로 교체하려고 시도하자 **`ec2:ModifyNetworkInterfaceAttribute` 권한 부족 에러**가 추가로 발생함.

#### 📸 증상 스크린샷
* **(1) 브라우저 접속 시 ERR_CONNECTION_TIMED_OUT 타임아웃 발생**
  ![브라우저 타임아웃 에러](./t2%20(1).png)
* **(2) 보안 그룹 규칙 수정 시 ModifySecurityGroupRules 권한 누락 오류**
  ![ModifySecurityGroupRules 오류](./t2%20(4).png)

> 💡 **3개월 차 눈높이 해설: `ERR_CONNECTION_TIMED_OUT`은 도대체 무슨 상황인가요?**
> * 만약 웹 서버가 내 요청을 확인하고 "너 접근 권한 없어!"라고 거절했다면 `403 Forbidden`이나 `Connection Refused` 에러가 뜹니다. (즉각 거절 답장이라도 옴)
> * 하지만 `TIMED_OUT`(시간 초과)은 **"내가 서버를 향해 편지(패킷)를 보냈는데, 중간 경비원(방화벽)이 편지를 묵묵히 쓰레기통에 버려버려서 영영 답장을 못 받고 하염없이 기다리다 지쳐 쓰러진 상태"**입니다.
> * 클라우드 웹 배포에서 타임아웃이 떴다면? 십중팔구 **"방화벽(보안 그룹)이 문을 꼭 닫아두고 패킷을 묵묵부답으로 버리고 있다"**는 뜻입니다!

---

### 2. 가설 수립 (Hypothesis)
* **가설 1 (웹 접속 실패 원인)**: Nginx는 80번 포트(HTTP)로 요청을 수신 대기 중인데, 보안 그룹 인바운드 규칙 설정 시 실수로 `HTTP(80)` 대신 `HTTPS(443)`를 등록하여 AWS 네트워크 방화벽(Security Group)이 외부에서 들어오는 80번 포트 패킷을 차단(Drop)하고 있을 것이다.
* **가설 2 (보안 그룹 수정 실패 원인)**: 최초 IAM 정책에는 구형 EC2 API인 `AuthorizeSecurityGroupIngress`, `RevokeSecurityGroupIngress`만 정의되어 있으나, 최신 AWS 콘솔의 "규칙 일괄 편집" 인터페이스는 내부적으로 `ec2:ModifySecurityGroupRules` API를 호출하기 때문에 권한 거부(Deny)가 발생했을 것이다.
* **가설 3 (보안 그룹 교체 실패 원인)**: EC2 인스턴스에 적용된 보안 그룹을 변경하는 작업은 인스턴스 자체가 아니라 가상 네트워크 카드인 **ENI(Elastic Network Interface)**의 속성을 변경하는 `ec2:ModifyNetworkInterfaceAttribute` API를 호출하므로, 이 권한이 없어 보안 그룹 교체가 막혔을 것이다.

> 💡 **3개월 차 눈높이 해설: 80번 포트와 443번 포트는 왜 다르고, 왜 문제가 되었을까요?**
> * **HTTP (80번 포트)**: 평문 일반 웹 통신 (자물쇠 없는 기본 통신).
> * **HTTPS (443번 포트)**: SSL/TLS 보안 인증서 자물쇠가 달린 암호화 웹 통신.
> * 우리는 아직 Nginx에 SSL 자물쇠 인증서를 설치하지 않아서 서버가 **80번 문**에서 손님을 기다리고 있는데, 보안 그룹 방화벽에는 엉뚱하게 **443번 문**만 활짝 열어두었던 것입니다. 손님이 80번 문으로 찾아오니 당연히 문이 닫혀 있어서 못 들어왔던 것이죠!
>
> 💡 **3개월 차 눈높이 해설: `ENI(Elastic Network Interface)`가 도대체 뭔가요?**
> * 컴퓨터 본체 뒤를 보면 인터넷 랜선을 꽂는 네모난 구멍이 있죠? 그 부품을 **'랜카드(NIC, Network Interface Card)'**라고 부릅니다.
> * AWS에서는 이 랜카드를 클라우드 가상 부품으로 만든 것을 **ENI**라고 부릅니다.
> * 재미있는 점은, AWS의 보안 그룹 방화벽은 컴퓨터(EC2) 본체에 붙는 게 아니라 **본체에 꽂힌 랜카드(ENI)에 붙는다는 사실**입니다! 그래서 보안 그룹을 바꾸려면 컴퓨터가 아니라 랜카드의 속성을 바꾸는 `ModifyNetworkInterfaceAttribute` 권한이 필요했던 것입니다.

---

### 3. 검증 (Verification)
* **EC2 인스턴스 보안 탭 검증**:
  * AWS 콘솔에서 `codyssey-web-server`의 [보안] 탭을 확인한 결과, 인바운드 규칙에 포트 범위가 **`443 (HTTPS)`**로 등록되어 있음을 직접 확인. 웹 브라우저는 `http://` (80번)으로 접속했으므로 패킷이 통과하지 못함이 명백히 입증됨.
* **콘솔 오류 메시지 역추적**:
  * 보안 그룹 규칙 편집 창(`t2 (5).png`)에서 80번 포트로 변경 후 저장을 누르자, `User is not authorized to perform: ec2:ModifySecurityGroupRules` 메시지가 정확히 출력됨.
  * 인스턴스 보안 그룹 변경 시도시 `User is not authorized to perform: ec2:ModifyNetworkInterfaceAttribute on resource: arn:aws:ec2:...:security-group/...` 메시지가 출력됨.

#### 📸 검증 스크린샷
* **(1) EC2 인스턴스 보안 탭 확인: HTTP 80 대신 HTTPS 443이 잘못 열려 있음**
  ![보안 탭 443 포트 확인](./t2%20(2).png)
* **(2) 올바른 포트(80번)로 규칙 편집 시도 화면**
  ![인바운드 규칙 편집 80번 시도](./t2%20(5).png)

---

### 4. 조치 (Action)
루트(Root) 계정으로 IAM 콘솔에 접속하여 `CodysseyB3LeastPrivilegePolicy`에 보안 그룹 및 네트워크 인터페이스 관련 최신 API를 완벽히 지원하도록 권한을 보강함.

1. **IAM 정책 업데이트 (2차 수정)**:
   * `"ec2:*SecurityGroup*"` : `CreateSecurityGroup`, `ModifySecurityGroupRules`, `AuthorizeSecurityGroupIngress` 등 보안 그룹 관련 모든 작업 포괄 허용.
   * `"ec2:*NetworkInterface*"` : 인스턴스 ENI에 보안 그룹을 연결/해제하는 `ModifyNetworkInterfaceAttribute` 및 `DescribeNetworkInterfaces` 허용.

```json
// 2차 수정으로 보강된 VPC/네트워크 관리 구문 (발췌)
{
  "Sid": "AllowVPCAndNetworkManagement",
  "Effect": "Allow",
  "Action": [
    ...
    "ec2:*SecurityGroup*",
    "ec2:*NetworkInterface*"
  ],
  "Resource": "*"
}
```

> 💡 **3개월 차 눈높이 해설: 왜 `ec2:*SecurityGroup*`, `ec2:*NetworkInterface*`로 묶었나요?**
> * AWS 콘솔에서 마우스로 보안 그룹 규칙을 바꾸고 인스턴스에 붙이는 단순한 동작 하나에도, 뒤에서는 `ModifySecurityGroupRules`, `ModifyNetworkInterfaceAttribute` 등 이름도 생소한 여러 API들이 도미노처럼 엮여서 호출됩니다.
> * 개발자가 이 모든 복잡한 내부 API 이름을 미리 다 알 수는 없으므로, 보안 그룹과 네트워크 카드에 관련된 권한들을 `*`로 묶어 안전하게 뚫어준 것입니다!

2. **보안 그룹 재구성 및 인스턴스 바인딩**:
   * 정책 업데이트 후 `codyssey-b3-user` 계정으로 신규 보안 그룹 **`codyssey-web-sg2`**를 정상 생성.
   * 인바운드 규칙: **HTTP (포트 80) $\to$ `0.0.0.0/0`**, **SSH (포트 22) $\to$ `본인 IP/32`** 설정.
   * EC2 인스턴스의 네트워크 인터페이스에 `codyssey-web-sg2`를 에러 없이 즉시 성공적으로 연결함.

---

### 5. 결과 (Result)
* 보안 그룹 바인딩 완료 후, 외부 웹 브라우저에서 `http://3.36.130.0`으로 재접속함.
* 타임아웃 지연 없이 **1초 만에 "🚀 웹 서비스 배포 성공! HTTP 200 OK" 카드가 완벽하게 렌더링됨**.
* 내부 웹 서버 데몬뿐만 아니라 외부 방화벽 및 라우팅 경로까지 전 구간 통신이 완벽하게 뚫렸음을 최종 검증함.

#### 📸 결과 스크린샷
* **보안 그룹 수정 및 교체 후 외부 웹 브라우저 200 OK 접속 성공**
  ![외부 웹 접속 검증 성공](./01_step5.png)

---

### 6. 재발 방지 (Prevention)
1. **프로토콜-포트 매핑 체크리스트 준수**:
   * 평문 웹 서비스(HTTP)는 반드시 **80번 포트**, SSL/TLS 암호화 웹 서비스(HTTPS)는 **443번 포트**임을 인지하고, 인증서가 적용되지 않은 초기 웹 서버 배포 시에는 80번 포트를 우선 개방해야 함.
2. **AWS 최신 콘솔 UI 동작 원리 파악**:
   * AWS 관리 콘솔은 과거 API(`AuthorizeSecurityGroup*`) 대신 현대화된 일괄 편집 API(`ModifySecurityGroupRules`)를 호출함.
   * EC2 인스턴스의 보안 그룹 변경은 인스턴스가 아닌 **ENI(NetworkInterface)** 레벨의 속성 변경(`ModifyNetworkInterfaceAttribute`)을 수반함.
   * 따라서 실무 최소 권한 정책을 설계할 때는 단일 API만 고집하기보다, 리소스 단위의 와일드카드 접두사(`ec2:*SecurityGroup*`, `ec2:*NetworkInterface*`)를 조합하여 불필요한 작업 블로킹을 방지해야 함.

> 💡 **3개월 차 주니어 개발자를 위한 시니어의 디버깅 3단계 치트키**
> * 앞으로 웹 서버를 띄웠는데 브라우저에서 안 열린다면 당황하지 말고 아래 3단계를 순서대로 확인하세요!
>   1. **1단계 (서버 내부 엔진)**: `sudo systemctl status nginx` $\to$ Nginx 프로세스가 초록색 `active`로 살아있는가?
>   2. **2단계 (내부 루프백 통신)**: `curl http://localhost` $\to$ 서버 안에서는 웹페이지 내용이 잘 튀어나오는가?
>   3. **3단계 (외부 방화벽 문단속)**: 브라우저 접속 $\to$ 여기서 타임아웃이 난다면 100% 보안 그룹의 **포트 번호(80 vs 443)** 문제다!

---

## 📜 IAM 정책 변경 이력 총괄

본 프로젝트에서 오류를 겪으며 단계별로 발전시킨 `CodysseyB3LeastPrivilegePolicy`의 전체 변경 히스토리입니다.

### 1. 최초 설정 정책 (초기 기획안)
* **상태**: 핵심 리소스 생성/삭제 권한만 수동으로 열거함.
* **문제점**: 콘솔 UI가 필요로 하는 `ec2:Describe*` 권한과 최신 보안그룹/ENI 제어 API가 누락되어 연쇄 오류 발생.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowVPCAndNetworkManagement",
      "Effect": "Allow",
      "Action": [
        "ec2:CreateVpc",
        "ec2:DeleteVpc",
        "ec2:DescribeVpcs",
        "ec2:ModifyVpcAttribute",
        "ec2:CreateSubnet",
        "ec2:DeleteSubnet",
        "ec2:DescribeSubnets",
        "ec2:ModifySubnetAttribute",
        "ec2:CreateInternetGateway",
        "ec2:DeleteInternetGateway",
        "ec2:AttachInternetGateway",
        "ec2:DetachInternetGateway",
        "ec2:DescribeInternetGateways",
        "ec2:CreateRouteTable",
        "ec2:DeleteRouteTable",
        "ec2:DescribeRouteTables",
        "ec2:AssociateRouteTable",
        "ec2:DisassociateRouteTable",
        "ec2:CreateRoute",
        "ec2:DeleteRoute",
        "ec2:CreateSecurityGroup",
        "ec2:DeleteSecurityGroup",
        "ec2:DescribeSecurityGroups",
        "ec2:AuthorizeSecurityGroupIngress",
        "ec2:RevokeSecurityGroupIngress",
        "ec2:AuthorizeSecurityGroupEgress",
        "ec2:RevokeSecurityGroupEgress"
      ],
      "Resource": "*"
    },
    {
      "Sid": "AllowEC2InstanceManagement",
      "Effect": "Allow",
      "Action": [
        "ec2:RunInstances",
        "ec2:TerminateInstances",
        "ec2:StartInstances",
        "ec2:StopInstances",
        "ec2:DescribeInstances",
        "ec2:DescribeInstanceStatus",
        "ec2:CreateKeyPair",
        "ec2:DeleteKeyPair",
        "ec2:DescribeKeyPairs",
        "ec2:DescribeImages",
        "ec2:DescribeVpcAttribute",
        "ec2:CreateTags"
      ],
      "Resource": "*"
    }
  ]
}
```

---

### 2. 1차 수정 정책 (사례 1 해결 후)
* **개선점**: `"Sid": "AllowAllEC2AndVPCReadOnlyDescribe"` 구문을 신설하여 `"ec2:Describe*"` 부여.
* **효과**: 콘솔의 모든 단순 조회 에러 및 화면 깨짐 현상 100% 해소.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowAllEC2AndVPCReadOnlyDescribe",
      "Effect": "Allow",
      "Action": [
        "ec2:Describe*"
      ],
      "Resource": "*"
    },
    {
      "Sid": "AllowVPCAndNetworkManagement",
      "Effect": "Allow",
      "Action": [
        "ec2:CreateVpc",
        "ec2:DeleteVpc",
        "ec2:ModifyVpcAttribute",
        "ec2:CreateSubnet",
        "ec2:DeleteSubnet",
        "ec2:ModifySubnetAttribute",
        "ec2:CreateInternetGateway",
        "ec2:DeleteInternetGateway",
        "ec2:AttachInternetGateway",
        "ec2:DetachInternetGateway",
        "ec2:CreateRouteTable",
        "ec2:DeleteRouteTable",
        "ec2:AssociateRouteTable",
        "ec2:DisassociateRouteTable",
        "ec2:CreateRoute",
        "ec2:DeleteRoute",
        "ec2:CreateSecurityGroup",
        "ec2:DeleteSecurityGroup",
        "ec2:AuthorizeSecurityGroupIngress",
        "ec2:RevokeSecurityGroupIngress",
        "ec2:AuthorizeSecurityGroupEgress",
        "ec2:RevokeSecurityGroupEgress"
      ],
      "Resource": "*"
    },
    {
      "Sid": "AllowEC2InstanceManagement",
      "Effect": "Allow",
      "Action": [
        "ec2:RunInstances",
        "ec2:TerminateInstances",
        "ec2:StartInstances",
        "ec2:StopInstances",
        "ec2:CreateKeyPair",
        "ec2:DeleteKeyPair",
        "ec2:CreateTags"
      ],
      "Resource": "*"
    }
  ]
}
```

---

### 3. 2차 최종 완성 정책 (사례 2 해결 후 - 현재 운영 중)
* **개선점**: 최신 콘솔 API 및 가상 네트워크 카드 제어를 위한 `"ec2:*SecurityGroup*"`, `"ec2:*NetworkInterface*"` 추가.
* **효과**: 보안 그룹 수정 및 인스턴스 보안 그룹 교체 완벽 지원. 과제 요구사항을 충족하는 최종 안정화 버전.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowAllEC2AndVPCReadOnlyDescribe",
      "Effect": "Allow",
      "Action": [
        "ec2:Describe*"
      ],
      "Resource": "*"
    },
    {
      "Sid": "AllowVPCAndNetworkManagement",
      "Effect": "Allow",
      "Action": [
        "ec2:CreateVpc",
        "ec2:DeleteVpc",
        "ec2:ModifyVpcAttribute",
        "ec2:CreateSubnet",
        "ec2:DeleteSubnet",
        "ec2:ModifySubnetAttribute",
        "ec2:CreateInternetGateway",
        "ec2:DeleteInternetGateway",
        "ec2:AttachInternetGateway",
        "ec2:DetachInternetGateway",
        "ec2:CreateRouteTable",
        "ec2:DeleteRouteTable",
        "ec2:AssociateRouteTable",
        "ec2:DisassociateRouteTable",
        "ec2:CreateRoute",
        "ec2:DeleteRoute",
        "ec2:*SecurityGroup*",
        "ec2:*NetworkInterface*"
      ],
      "Resource": "*"
    },
    {
      "Sid": "AllowEC2InstanceManagement",
      "Effect": "Allow",
      "Action": [
        "ec2:RunInstances",
        "ec2:TerminateInstances",
        "ec2:StartInstances",
        "ec2:StopInstances",
        "ec2:CreateKeyPair",
        "ec2:DeleteKeyPair",
        "ec2:CreateTags"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## 💡 결론 및 시니어 엔지니어링 교훈

1. **보안과 생산성의 조화**:
   * 최소 권한을 구현할 때 모든 API를 무조건 하나씩 막는 것은 비생산적입니다. 비용과 보안 침해를 일으키는 `State-Changing(쓰기/삭제)` 권한과 `Read-Only(조회)` 권한을 명확히 분리함으로써 두 마리 토끼를 잡을 수 있었습니다.
2. **네트워크 디버깅의 체계화**:
   * 웹 접속 불가 현상이 발생했을 때, OS 프로세스(`systemctl`) $\to$ 로컬 루프백(`localhost curl`) $\to$ 인스턴스 방화벽(보안 그룹 규칙) $\to$ VPC 라우팅 테이블 순으로 트래픽 경로를 따라 계층별로 검증함으로써 문제의 본질(443 vs 80 포트 불일치)을 신속하게 짚어낼 수 있었습니다.
3. **IAM 최소 권한의 실무 완성**:
   * 최신 클라우드 인프라는 내부적으로 다양한 보조 API(ENI, ModifyRules 등)를 호출합니다. 이번 트러블슈팅을 통해 실무 규정에 완벽히 부합하면서도 개발 작업에 막힘이 없는 견고한 최소 권한 정책을 성공적으로 수립하였습니다.
