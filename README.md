# 基于DID的跨境数据认证和传输系统

## 项目概述

本项目是由**光联世纪**和**澳门科技大学**在澳门科学技术发展基金（FDCT）的支持下共同开发的一套基于分布式身份（DID）和可验证凭证（VC）技术的跨境数据认证与传输系统。

该系统利用区块链和密码学技术，为跨境数据传输提供安全的身份认证、授权管理和审计追踪机制，确保跨境数据流动的合规性和安全性。

## 核心功能

### 1. **分布式身份管理（DID）**
- 基于Ed25519密钥对的DID生成和管理
- 用户、发行人、验证人等角色的身份唯一标识
- 密钥存储和管理机制

**相关文件：** `user.py`, `issuer.py`, `verifier.py`

### 2. **可验证凭证（VC）颁发与签署**
- 发行机构为用户生成用户身份凭证（User VC）
- 数据提供者生成跨境数据传输凭证（Transfer VC）
- 基于DID-Kit的异步签署机制
- 支持批量用户创建和凭证生成

**相关文件：** `issuer.py`, `provider.py`, `VCHashUpload.py`

### 3. **可验证演示（VP）生成**
- 用户生成验证演示，组合展示多个VC
- VP签署和验证
- 演示的生命周期管理

**相关文件：** `user.py`, `VPHashUpload.py`

### 4. **跨境数据传输管理**
- 创建跨境数据传输请求
- 包含数据源地、目的地、数据类型、体积、传输原因等信息
- 传输时间和过期时间管理
- 数据哈希验证

**相关文件：** `transettings.py`, `provider.py`, `transferor.py`

### 5. **规则引擎与合规性检查**
- 基于不同司法管辖区的数据传输规则
- 支持多个地区判定：EEA、中国、印度、俄罗斯、新加坡、越南、日本、韩国、香港、英国、美国、加拿大等
- CBPR（跨境隐私规则）合规性检查
- 审批人规则验证

**相关文件：** `ruleset.py`, `cbpr.py`, `propset.py`

### 6. **审批与审计机制**
- 审批人（Reviewer）对传输请求的合规性审查
- VP签署确认
- 传输日志记录和性能分析
- 支持多步骤审批流程

**相关文件：** `reviewer.py`, `merge_performance_logs.py`, `file_checker.py`

### 7. **数据哈希与上传**
- 用户凭证哈希计算（SHA256）
- VP哈希计算
- VC上传验证
- 支持批量处理和性能监测

**相关文件：** `HashMethod.py`, `UserKeyUpload.py`, `VCHashUpload.py`, `VPHashUpload.py`

### 8. **VDR（可验证数据仓库）**
- 简单VDR实现，存储所有用户DID映射
- 用户查询和验证
- JSON格式的用户数据库

**相关文件：** `simplevdr.py`, `allusers.json`

## 系统架构

### 主要角色

1. **发行人（Issuer）** - 负责颁发用户身份凭证
2. **用户（User）** - 拥有DID身份，可以生成和提交传输请求
3. **数据提供者（Provider）** - 创建跨境数据传输凭证
4. **数据接收者（Transferor）** - 接收和处理传输请求
5. **审批人（Reviewer）** - 审查传输请求的合规性
6. **验证人（Verifier）** - 验证凭证和演示的有效性

### 工作流程

```
1. 颁发阶段
   Issuer → 为User创建身份VC

2. 传输请求阶段
   Provider → 创建Transfer VC
   User → 生成VP（包含User VC + Transfer VC）

3. 审批阶段
   Reviewer → 检查规则和合规性
   Reviewer → 签署VP确认

4. 执行阶段
   Transferor → 处理审批通过的传输
   Verifier → 验证所有凭证的有效性

5. 审计阶段
   系统记录所有操作的性能指标和日志
```

## 快速开始

### 环境要求

- Python 3.8+
- didkit-python（DID工具库）
- 标准库：json, csv, asyncio, datetime

### 安装依赖

```bash
pip install didkit
```

### 基本使用示例

#### 1. 创建用户

```python
from issuer import Issuer

# 初始化发行人
issuer = Issuer("key.jwk")

# 批量创建用户
issuer.create_users_batch(5)  # 创建5个用户
```

#### 2. 生成跨境传输请求

```python
from provider import Provider

# 初始化数据提供者
provider = Provider("key.jwk")

# 创建传输请求
provider.create_trans_request(
    receiver="user0",
    approver1="user1",
    outfile="transfer_request.json"
)
```

#### 3. 审批传输请求

```python
from reviewer import Reviewer
from ruleset import Decision

# 初始化审批人
reviewer = Reviewer("key.jwk")

# 检查规则合规性
decision = reviewer.check_rules("transfer_request.json")

if decision == Decision.APPROVE:
    # 签署并批准
    reviewer.sign_file("transfer_request.json", "transfer_approved.json")
```

#### 4. 验证凭证

```python
from verifier import Verifier

# 初始化验证人
verifier = Verifier("key.jwk")

# 验证用户VC
verifier.verify_vc_file("user.json")

# 验证VP
verifier.verify_vp_file("user_vp.json")
```

#### 5. 处理传输

```python
from transferor import Transferor

# 初始化数据接收者
transferor = Transferor("key.jwk")

# 处理传输请求
transferor.process_transfer("transfer_approved.json")
```

## 关键文件说明

| 文件 | 功能说明 |
|------|--------|
| `user.py` | 用户类，生成VP，签署凭证 |
| `issuer.py` | 发行人类，颁发用户身份VC |
| `provider.py` | 数据提供者类，创建传输VC |
| `reviewer.py` | 审批人类，审查合规性和签署 |
| `verifier.py` | 验证人类，验证VC和VP的有效性 |
| `transferor.py` | 数据接收者类，处理传输 |
| `transettings.py` | 传输请求配置类 |
| `ruleset.py` | 规则引擎，实现合规性检查 |
| `cbpr.py` | 跨境隐私规则检查 |
| `propset.py` | 传输属性和组织类型定义 |
| `HashMethod.py` | 数据哈希计算方法 |
| `simplevdr.py` | 简单VDR实现 |
| `fileoper.py` | 文件操作工具类 |
| `UserKeyUpload.py` | 用户密钥上传处理 |
| `VCHashUpload.py` | VC哈希上传处理 |
| `VPHashUpload.py` | VP哈希上传处理 |

## 数据格式

### 用户凭证（User VC）

```json
{
  "@context": ["https://www.w3.org/2018/credentials/v1"],
  "id": "user-credential-id",
  "type": ["VerifiableCredential"],
  "issuer": "did:key:...",
  "issuanceDate": "2024-01-01T00:00:00Z",
  "credentialSubject": {
    "id": "did:key:...",
    "userName": "user0"
  },
  "proof": {...}
}
```

### 传输凭证（Transfer VC）

```json
{
  "@context": ["https://www.w3.org/2018/credentials/v1"],
  "id": "transfer-credential-id",
  "type": ["VerifiableCredential"],
  "issuer": "did:key:...",
  "credentialSubject": {
    "transferId": "trans-001",
    "userName": "user0",
    "receiver": "user1",
    "receiverKey": "did:key:...",
    "transferTime": "2024-01-02T00:00:00Z",
    "origArea": "China",
    "destArea": "EU",
    "dataType": "PersonalData",
    "dataVolume": "100",
    "dataUnit": "MB",
    "dataHash": "sha256-hash-value",
    "reason": "Business Transfer",
    "approver": "did:key:..."
  },
  "expirationDate": "2024-01-30T00:00:00Z"
}
```

### 可验证演示（VP）

```json
{
  "@context": ["https://www.w3.org/2018/credentials/v1"],
  "type": ["VerifiablePresentation"],
  "verifiableCredential": [
    {...user-vc...},
    {...transfer-vc...}
  ],
  "proof": {...}
}
```

## 性能监测

系统支持对各阶段的性能进行监测和日志记录：

- `provider_upload_times.csv` - 数据提供者操作时间日志
- `reviewer_upload_times.csv` - 审批人操作时间日志
- `performance_results.csv` - 综合性能结果
- `final_performance_summary.csv` - 最终性能总结

### 性能分析

```python
from merge_performance_logs import merge_performance_logs

# 合并和分析性能日志
merge_performance_logs()
```

## 规则与合规性

系统支持多个司法管辖区的数据传输规则：

- **EEA（欧洲经济区）** - GDPR合规
- **中国** - 数据出境合规检查
- **印度、俄罗斯、新加坡** - 各地区特定规则
- **CBPR（跨境隐私规则）** - 亚太地区隐私保护

规则检查由`RuleChecker`类在`ruleset.py`中实现，返回批准（APPROVE）或拒绝（REJECT）的决策。

## 安全特性

- **DID身份** - 基于公钥密码学的去中心化身份
- **数字签署** - 所有凭证和演示使用Ed25519签署
- **哈希验证** - 数据完整性通过SHA256哈希验证
- **时间锁定** - 传输请求包含生效时间和过期时间
- **审计跟踪** - 所有操作的日志记录

## 测试文件

项目包含测试数据和演示文件：

- `test-user.py` - 用户功能测试
- `transetting_test.py` - 传输设置测试
- `trans0928.json` - 示例传输请求
- `user*.json` - 示例用户凭证

## 许可证

本项目由光联世纪和澳门科技大学联合开发。

## 致谢

本项目得到了**澳门科学技术发展基金（FDCT）**的大力支持。感谢FDCT对本项目的资助和支持，使得我们能够开发这一创新的跨境数据认证和传输系统，为促进数据的安全流动和跨境合作做出贡献。

---

**开发机构：**
- 光联世纪
- 澳门科技大学

**支持机构：**
- 澳门科学技术发展基金（FDCT）
