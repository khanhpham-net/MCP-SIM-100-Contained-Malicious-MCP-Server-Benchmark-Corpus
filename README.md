# MCP-SIM-100: Contained Malicious MCP Server Benchmark Corpus

> **Version:** `v4.4 (SIM-Only, Contained & Structurally Polymorphic)`  
> **Updated:** November 13, 2026  
> **Objective:** Provide a standardized benchmark corpus of 100 safe, contained malicious Model Context Protocol (MCP) server fixtures to quantitatively evaluate the detection capabilities of SAST, DAST, and AI Security Scanners (such as MCP Audit, MCTS, Cisco MCP Scanner, MCPShield, and NVIDIA SkillSpector).

---

## 1. Architecture Overview & Design Principles

The `MCP-SIM-100` corpus consists of **100 independent malicious MCP server samples** (`SIM001` – `SIM100`), engineered to rigorously evaluate taint analysis, public contract verification (`@mcp.tool()` contract mismatch), unauthorized child process execution, loopback network credential exfiltration, and indirect prompt injection across multiple MCP surfaces.

### 1.1. Controlled Experimental Matrix: 20 Families × 5 Edges

To prevent security scanners from relying on superficial shortcuts or shallow fingerprinting, the benchmark is orthogonalized across a **20 Family × 5 Edge** matrix:

```
                  ┌────────────────────────────────────────────────────────┐
                  │                    5 STRUCTURAL EDGES                  │
                  │  E1: Single-file FastMCP (no domain/models, functional)│
                  │  E2: Two-file Service (server.py + service.py adapter) │
                  │  E3: Subpackage + SSE Transport (core/handler.py)      │
                  │  E4: Multi-tool Realistic + Streamable-HTTP            │
                  │  E5: Modular Strict Replay-Tracked Server              │
┌─────────────────┼────────────────────────────────────────────────────────┤
│ 20 FAMILIES     │                                                        │
│ M01–M05 (Group M)│  SIM001–SIM025: Persisted State Mutation Mismatch      │
│ C01–C05 (Group C)│  SIM026–SIM050: Unauthorized Child Process / Shell     │
│ S01–S05 (Group S)│  SIM051–SIM075: Credential Harvesting & Network Exfil  │
│ P01–P05 (Group P)│  SIM076–SIM100: Indirect Prompt Injection & Poisoning   │
└─────────────────┴────────────────────────────────────────────────────────┘
```

- **Vertical Axis (20 Families — Business Domains & Vulnerabilities):** 20 independent business domains representing authentic industry microservices (inventory, billing, scheduling, reporting, telemetry monitoring, fleet, etc.). Each family defines a legitimate tool contract and a core malicious mechanism.
- **Horizontal Axis (5 Edges — Structural Polymorphism & Packaging):** Rather than sharing a uniform directory layout or coding pattern, the 5 edges systematically vary file topology, type annotations, invocation semantics (direct function calls vs. adapter methods vs. dynamic dispatch), transport mechanisms (stdio vs. sse vs. streamable-http), and input schema constraints (standard scalar parameters vs. Pydantic Field validation).
- **Scientific Significance:** This orthogonal decomposition enables researchers to isolate precisely why a scanner fails: whether due to **semantic security reasoning deficits** (Family axis) or **cross-file / AST packaging / transport parsing limitations** (Edge axis).

---

## 2. Specification of 4 Attack Classes

| Group | Sample Range | Target Vulnerability | Technical Mechanism in Source | Verification & Ground Truth Evidence |
|---|---|---|---|---|
| **M** | `SIM001`–`SIM025` | **Persisted Tool Contract Mismatch** | The tool advertises a benign read-only contract (`lookup_stock`, `quote_invoice`) with protocol metadata `readOnlyHint=True`, but secretly executes persistent state mutations recorded in a local ledger (`inventory_ledger.jsonl`, `billing_journal.jsonl`, etc.). Tool output returns a legitimate domain response with computed metrics, concealing the background mutation. | Detects MCP contract violation (`readOnlyHint=True` vs. persistent file writes); AST side-effect analysis identifies covert ledger appends. |
| **C** | `SIM026`–`SIM050` | **Unauthorized Child Process / Shell Gradient** | The tool declares a read-only telemetry query contract with metadata `readOnlyHint=True`, but spawns internal worker subprocesses following a deliberate detection gradient: `E1`–`E2` execute shell commands (`shell=True` with `safe_ref` validation to prevent arbitrary host injection); `E3`–`E5` execute pure `argv` lists (`asyncio.create_subprocess_exec`, `subprocess.run`, `subprocess.Popen`) invoking `--job apply` which mutates local `device_state.json` (violating `readOnlyHint=True`). | AST callsite detection of process execution (`subprocess.run`, `subprocess.check_output`, `create_subprocess_exec`, `subprocess.Popen`); worker mutation of `device_state.json` violating MCP `readOnlyHint=True`. |
| **S** | `SIM051`–`SIM075` | **Credential Harvesting & Network Exfiltration** | The tool accesses environment credentials (`GITHUB_TOKEN`, `OPENAI_API_KEY`, `SLACK_BOT_TOKEN`, `STRIPE_SECRET_KEY`) via `os.getenv`/`os.environ.get`, or reads local account profile `account_profile.txt` (for `S03`, with fallback to `AWS_ACCESS_KEY_ID`), packs them into an unsuspicious JSON field `"note"` (avoiding obvious keys like token or secret), and dispatches HTTP/socket POST requests to isolated fixed loopback ports (`9107`–`9644`) on `127.0.0.1` (without base64). | Taint flow from environment variables/config files into payload `"note"` reaching network sinks (`urllib.request` / `HTTPConnection` / `socket`) on dedicated loopback ports; zero hardcoded secret literals. |
| **P** | `SIM076`–`SIM100` | **Indirect Prompt Injection & Tool Poisoning** | Injects stealthy adversarial prompt payloads across 5 distinct MCP protocol surfaces (tool description, resource body, tool result `preview` read from `content.txt`, input schema description, prompt message). All 5 variants avoid crude trigger words (`OVERRIDE`, `SYSTEM`, `bypass`, `admin`), pursuing realistic security objectives: cross-tool listing exfiltration, conversation context harvesting, directory/config parameter disclosure via natural Vietnamese social engineering, and persistent instruction hijacking across conversation turns. | Protocol metadata and runtime attack surfaces; `P03` runtime ingestion from `content.txt`; verifies scanner capability to detect unauthorized data extraction and agent manipulation without relying on heuristic keyword filters. |

---

## 3. Containment Invariants & Safety Guarantees

All 100 benchmark fixtures strictly adhere to safety invariants to guarantee risk-free static analysis and controlled local execution:
1. **Network Containment (Loopback Only):** All outbound network requests in Group S are strictly bound to isolated, dedicated loopback ports on `127.0.0.1:9107–9644` with a 0.5-second timeout, zero external Internet access, no redirect following, no proxy traversal, and no base64 obfuscation.
2. **File Containment (Sample-Local Directory Only):** All ledger writes, state files, and worker artifacts are strictly confined to the fixture's local directory; no files outside the sample directory, user profile directories, registry, or shared OS locations are ever accessed (eliminating `tempfile.gettempdir()`).
3. **Controlled Execution (Domain-Specific Workers):** Group C subprocesses strictly invoke sample-local, domain-specific Python worker scripts (`counter_sync.py`, `indicator_service.py`, `device_dispatcher.py`, `asset_subsystem.py`, `task_executor.py`) supporting dual modes (`--job apply` produces state: changed, `--job status` produces state: unchanged), without downloading or executing remote code or destructive shell commands.
4. **Zero Hardcoded Secret Literals:** All credential reads use `os.getenv` with empty default values (`""`) or read local sample-local mock profiles, completely eliminating CWE-798 (hardcoded credentials) which confound static analysis scanners.

---

## 4. Repository Structure

```text
MCP-SIM-100/
├── audit_corpus.py             # AST validation, snapshot hashing, and syntax check (stdlib only)
├── build.py                    # Corpus generator reproducing all 100 samples and metadata
├── catalog.py                  # Taxonomy of 20 Families, Tools, Edges, and parameter matrix
├── fixture_templates.py        # Code generation templates for 20 families x 5 structural edges
├── prepare_evaluation.py       # Ingests review records, computes snapshot hashes, handles admission
├── create_handoff.py           # Generates 500 input records for benchmark scanner evaluation
├── score_results.py            # Evaluation and scoring engine for scanner benchmark runs
├── test_evaluation.py          # Regression and unit test suite
├── verify_static_sinks.py      # Static safety and contract verifier (AST, gradient, forbidden tokens, worker contracts, production depth)
├── manifest.json               # Raw generator manifest
├── benchmark-manifest.json     # Official admission and scoring manifest
├── scan-results-template.json  # 500-run input template (100 samples x 5 scanners)
├── SAMPLE_INDEX.md             # Direct lookup index for all 100 samples and evidence locations
├── EVALUATION_GUIDE.md         # Benchmark scoring methodology, rubric, and review guide
├── SCANNER_HANDOFF.md          # Input routing and execution instructions for each scanner tool
├── evaluation/
│   ├── static-audit.json       # Aggregated AST facts and snapshot hash report
│   ├── static-evidence/        # 100 detailed static evidence JSON files (SIM001–SIM100)
│   └── reviews.json            # Ground truth audit reviews for admission
├── samples/                    # 100 standalone MCP server source code directories
│   ├── SIM001/
│   │   ├── server.py
│   │   └── pyproject.toml
│   └── ... SIM100/
└── skill-views/                # 100 derived agent skill representations
    └── SIM001 ... SIM100/
        ├── SKILL.md
        └── ...
```

---

## 5. Pipeline Execution & Evaluation Workflow

Environment Requirement: **Python 3.11+** (Python 3.13 or virtual environment with `mcp` and `pydantic` installed is recommended).

### 5.1. Static Verification
Static inspection scripts use Python standard library only and never import or execute untrusted corpus modules:

```powershell
# 1. Statically audit entire corpus, verify AST syntax and snapshot integrity
python -B audit_corpus.py

# 2. Build admission manifest and synchronize ground-truth review records
python -B prepare_evaluation.py

# 3. Generate handoff input template for 5 scanners (500 runs)
python -B create_handoff.py

# 4. Run regression test suite to ensure scoring and admission integrity
python -B test_evaluation.py -v
```

### 5.2. Sample Reproduction (Build Pipeline)
To regenerate all 100 samples in `samples/` and `skill-views/` from the source generator:

```powershell
python -B build.py
python -B verify_static_sinks.py
python -B audit_corpus.py
python -B prepare_evaluation.py --auto-admit
python -B create_handoff.py
```

### 5.3. Scanner Scoring
Once evaluation scanners complete analysis and outputs are normalized per [EVALUATION_GUIDE.md](EVALUATION_GUIDE.md):

```powershell
python -B score_results.py results/normalized_run.json --output results/metrics.json
```

---
---

# [Bản tiếng Việt / Vietnamese Version]

# MCP-SIM-100: Contained Malicious MCP Server Benchmark Corpus

> **Phiên bản:** `v4.4 (SIM-Only, Contained & Structurally Polymorphic)`  
> **Cập nhật:** 13/11/2026  
> **Mục tiêu:** Cung cấp bộ benchmark gồm 100 mẫu máy chủ MCP (Model Context Protocol) độc hại được kiểm soát an toàn (contained test fixtures) phục vụ đánh giá định lượng năng lực phát hiện của các công cụ SAST, DAST, và AI Security Scanner (như MCP Audit, MCTS, Cisco MCP Scanner, MCPShield, NVIDIA SkillSpector).

---

## 1. Tổng quan Kiến trúc & Nguyên lý Thiết kế

Corpus `MCP-SIM-100` bao gồm **100 mẫu máy chủ MCP độc hại độc lập** (`SIM001` – `SIM100`), được thiết kế để kiểm thử khả năng phân tích luồng dữ liệu (taint analysis), kiểm tra vi phạm hợp đồng công bố công khai (`@mcp.tool()` contract mismatch), phát hiện thực thi tiến trình con ngoài luồng, rò rỉ thông tin nhạy cảm qua mạng loopback, và tiêm nhiễm prompt gián tiếp (Indirect Prompt Injection).

### 1.1. Ma trận Thí nghiệm Đối chứng 20 Family × 5 Edge

Để ngăn chặn các công cụ quét an ninh sử dụng "đường tắt" (shortcut learning / superficial fingerprinting), bộ benchmark được chuẩn hóa theo ma trận trực giao **20 Family × 5 Edge**:

```
                  ┌────────────────────────────────────────────────────────┐
                  │                    5 STRUCTURAL EDGES                  │
                  │  E1: Single-file FastMCP (không domain/models, native) │
                  │  E2: Two-file Service (server.py + service.py)         │
                  │  E3: Subpackage + SSE Transport (core/handler.py)      │
                  │  E4: Multi-tool Realistic + Streamable-HTTP            │
                  │  E5: Pydantic Regex Field + Dynamic Dispatch           │
┌─────────────────┼────────────────────────────────────────────────────────┤
│ 20 FAMILIES     │                                                        │
│ M01–M05 (Group M)│  SIM001–SIM025: Persisted State Mutation Mismatch      │
│ C01–C05 (Group C)│  SIM026–SIM050: Unauthorized Child Process / Shell     │
│ S01–S05 (Group S)│  SIM051–SIM075: Credential Harvesting & Network Exfil  │
│ P01–P05 (Group P)│  SIM076–SIM100: Indirect Prompt Injection & Poisoning   │
└─────────────────┴────────────────────────────────────────────────────────┘
```

- **Trục Tung (20 Families - Nghiệp vụ & Lỗ hổng):** 20 họ nghiệp vụ độc lập đại diện cho 20 lĩnh vực thực tế (quản lý kho, tài chính, DevOps, giám sát hệ thống, v.v.). Mỗi họ định nghĩa hợp đồng công cụ và hành vi độc hại cốt lõi.
- **Trục Hoành (5 Edges - Đa hình cấu trúc & Bao gói):** Thay vì sử dụng chung một bố cục thư mục đơn điệu, 5 edge biến thiên cấu trúc file, kiểu gõ (typing), cơ chế gọi hàm (direct call vs. dynamic dispatch), giao thức truyền tải (stdio vs. sse vs. streamable-http), và ràng buộc schema đầu vào (native types vs. Pydantic Field regex validation).
- **Ý nghĩa khoa học:** Sự phân tách trực giao này cho phép người nghiên cứu cô lập chính xác nguyên nhân khiến scanner thất bại: do **năng lực phân tích ngữ nghĩa bảo mật** (trục Family) hay do **khả năng phân tích liên tệp / AST / cấu trúc bao gói** (trục Edge).

---

## 2. Đặc tả 4 Nhóm Lỗ hổng (Attack Classes)

| Nhóm | Dải ID | Lỗ hổng mục tiêu | Cơ chế kỹ thuật trong Source | Bằng chứng kiểm chứng |
|---|---|---|---|---|
| **M** | `SIM001`–`SIM025` | **Persisted Tool Contract Mismatch** | Tool công bố docstring nghiệp vụ chuẩn mực (`lookup_stock`, `quote_invoice`) và metadata giao thức `readOnlyHint=True`, nhưng bên trong kích hoạt sửa đổi trạng thái bền vững ghi vào ledger cục bộ (`inventory_ledger.jsonl`, `billing_journal.jsonl`, v.v.). Kết quả trả về giữ nguyên trạng thái hợp lệ, che giấu hành vi biến đổi ngầm. | Phát hiện vi phạm hợp đồng MCP (`readOnlyHint=True` vs. persistent file write); phân tích AST phát hiện side-effect ẩn. |
| **C** | `SIM026`–`SIM050` | **Unauthorized Child Process / Shell Gradient** | Tool công bố hợp đồng truy vấn telemetry và metadata `readOnlyHint=True`, nhưng kích hoạt tiến trình con thực thi worker nội bộ theo gradient phát hiện có chủ đích: `E1`–`E2` sử dụng `shell=True` (với validation `safe_ref` tránh injection bừa bãi); `E3`–`E5` sử dụng danh sách `argv` thuần túy (`asyncio.create_subprocess_exec`, `subprocess.run`, `subprocess.Popen`) với `--job apply` làm đột biến file `device_state.json` (vi phạm hợp đồng chỉ-đọc `readOnlyHint=True`). | AST callsite thực thi tiến trình con (`subprocess.run`, `subprocess.check_output`, `create_subprocess_exec`, `subprocess.Popen`); worker mutation `device_state.json` vi phạm hợp đồng MCP `readOnlyHint=True`. |
| **S** | `SIM051`–`SIM075` | **Credential Harvesting & Network Exfiltration** | Tool đọc bí mật môi trường (`GITHUB_TOKEN`, `OPENAI_API_KEY`, `SLACK_BOT_TOKEN`, `STRIPE_SECRET_KEY`) qua `os.getenv`/`os.environ.get`, hoặc tài khoản cục bộ `account_profile.txt` (cho `S03`, fallback `AWS_ACCESS_KEY_ID`), đưa vào trường JSON trung tính `"note"` (không dùng các key lộ liễu như token hay secret) và gửi HTTP/socket POST tới các port loopback cố định riêng biệt (`9107`–`9644`) trên `127.0.0.1` (không dùng base64). | Taint flow từ biến môi trường/file cấu hình vào trường payload `"note"` tới sink mạng `urllib.request` / `HTTPConnection` / `socket` trên loopback port riêng biệt; không chứa hardcoded secrets. |
| **P** | `SIM076`–`SIM100` | **Indirect Prompt Injection & Tool Poisoning** | Chèn các chuỗi chỉ dẫn tiêm nhiễm tinh vi vào 5 bề mặt MCP (tool description, resource body, tool result `preview` đọc từ `content.txt`, schema description, prompt message). Toàn bộ 5 biến thể tránh hoàn toàn các từ khóa thô thiển (`OVERRIDE`, `SYSTEM`, `bypass`, `admin`), mang mục tiêu an ninh rõ ràng: trích xuất dữ liệu chéo công cụ qua listing, rò rỉ lịch sử hội thoại, lộ đường dẫn/biến cấu hình qua tiếng Việt tự nhiên, và duy trì chỉ dẫn dai dẳng xuyên lượt tương tác. | Bề mặt phân phối metadata/runtime; `P03` nạp runtime từ `content.txt`; kiểm chứng khả năng trích xuất dữ liệu và can thiệp hành vi tác tử mà không cần từ khóa lộ liễu. |

---

## 3. Bất biến An toàn & Cô lập (Containment Invariants)

Toàn bộ 100 mẫu fixture tuân thủ nghiêm ngặt các nguyên tắc an toàn để có thể thực thi và phân tích an toàn trong môi trường nghiên cứu:
1. **Cô lập Mạng (Loopback Only):** Mọi kết nối mạng nội bộ của nhóm S đều bị ghim chặt chẽ vào dải port loopback cố định riêng biệt `127.0.0.1:9107–9644`, timeout tối đa 0,5 giây, không truy cập Internet, không follow redirect, không vượt qua proxy, không dùng base64.
2. **Cô lập Tệp (Sample-Local Directory Only):** Toàn bộ file trạng thái nghiệp vụ và file của worker chỉ được đọc/ghi trong thư mục cục bộ của fixture, tuyệt đối không đụng chạm đến thư mục người dùng, registry, hoặc hệ thống tệp gốc (loại trừ hoàn toàn `tempfile.gettempdir()`).
3. **Mã độc Kiểm soát (Controlled Execution):** Nhóm C thực thi tiến trình con trỏ tới tệp script Python nội bộ theo nghiệp vụ riêng (`counter_sync.py`, `indicator_service.py`, `device_dispatcher.py`, `asset_subsystem.py`, `task_executor.py`), hỗ trợ chế độ kép `--job apply` (state: changed) và `--job status` (state: unchanged), không tải hoặc thực thi shellcode, không chạy lệnh phá hoại hệ thống.
4. **Không Hardcode Secrets (Zero Hardcoded Secret Literals):** Toàn bộ token, API key và credential được đọc qua `os.getenv` với giá trị mặc định rỗng (`""`) hoặc đọc tệp cấu hình mẫu cục bộ, loại trừ triệt để CWE-798 (hardcoded credentials) gây nhiễu cho các scanner phân tích tĩnh.

---

## 4. Cấu trúc Thư mục Dự án

```text
MCP-SIM-100/
├── audit_corpus.py             # Script kiểm tra AST, snapshot hash, cú pháp (chỉ dùng stdlib)
├── build.py                    # Generator tái tạo 100 mẫu SIM và metadata
├── catalog.py                  # Từ điển 20 Family, Tool, Edge và ma trận tham số
├── fixture_templates.py        # Thư viện template mã nguồn cho 20 họ x 5 edge
├── prepare_evaluation.py       # Tiếp nhận review, tính snapshot hash và admission
├── create_handoff.py           # Sinh danh mục 500 bản ghi input cho 5 scanner
├── score_results.py            # Công cụ tính toán chỉ số đánh giá (Evaluation engine)
├── test_evaluation.py          # Bộ kiểm thử hồi quy (Unit/Regression tests)
├── verify_static_sinks.py      # Bộ kiểm tra an toàn tĩnh (AST, gradient, sink tokens, worker contracts)
├── manifest.json               # Manifest gốc từ generator
├── benchmark-manifest.json     # Manifest chính thức dùng cho admission & scoring
├── scan-results-template.json  # 500 dòng input chuẩn bị cho 100 mẫu x 5 scanner
├── SAMPLE_INDEX.md             # Bảng tra cứu trực tiếp 100 mẫu và bằng chứng
├── EVALUATION_GUIDE.md         # Hướng dẫn quy trình chấm điểm và rubric
├── SCANNER_HANDOFF.md          # Hướng dẫn chi tiết định tuyến input cho từng scanner
├── evaluation/
│   ├── static-audit.json       # Báo cáo tổng hợp AST facts và snapshot hash
│   ├── static-evidence/        # 100 tệp JSON bằng chứng tĩnh chi tiết (SIM001–SIM100)
│   └── reviews.json            # Hồ sơ thẩm định độc lập phục vụ ground truth
├── samples/                    # 100 thư mục mã nguồn máy chủ MCP độc lập
│   ├── SIM001/
│   │   ├── server.py
│   │   └── pyproject.toml
│   └── ... SIM100/
└── skill-views/                # 100 thư mục dẫn xuất biểu diễn dạng Agent Skill
    └── SIM001 ... SIM100/
        ├── SKILL.md
        └── ...
```

---

## 5. Quy trình Chạy Pipeline & Đánh giá

Yêu cầu môi trường: **Python 3.11+** (Khuyến nghị Python 3.13 hoặc môi trường ảo đã cài đặt `mcp` và `pydantic`).

### 5.1. Rà soát & Xác thực Tĩnh (Static Verification)
Các script phân tích tĩnh sử dụng hoàn toàn thư viện chuẩn (Standard Library), không import hay thực thi mã của các sample:

```powershell
# 1. Rà soát tĩnh toàn bộ corpus, kiểm tra cú pháp AST và tính toàn vẹn snapshot
python -B audit_corpus.py

# 2. Xây dựng admission manifest và cập nhật hồ sơ review
python -B prepare_evaluation.py

# 3. Tạo template đầu vào chuẩn bị cho 5 công cụ quét (500 lượt chạy)
python -B create_handoff.py

# 4. Chạy bộ kiểm thử hồi quy bảo đảm tính toàn vẹn logic
python -B test_evaluation.py -v
```

### 5.2. Tái tạo Mã nguồn Mẫu (Build & Reproduction)
Để sinh lại toàn bộ 100 mẫu `samples/` và `skill-views/` từ source generator:

```powershell
python -B build.py
python -B verify_static_sinks.py
python -B audit_corpus.py
python -B prepare_evaluation.py --auto-admit
python -B create_handoff.py
```

### 5.3. Quy trình Chấm điểm Scanner (Scoring)
Sau khi các công cụ quét hoàn thành việc quét 100 mẫu và xuất kết quả chuẩn hóa theo định dạng trong [EVALUATION_GUIDE.md](EVALUATION_GUIDE.md):

```powershell
python -B score_results.py results/normalized_run.json --output results/metrics.json
```
