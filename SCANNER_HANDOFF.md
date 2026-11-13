# Scanner Input Handoff & Evaluation Dossier

> **Target Audience:** Scanner Evaluation Lead  
> **Version:** `v4.4 (SIM-Only, Contained & Structurally Polymorphic)`  
> **Updated:** November 13, 2026  

The corpus currently comprises **100 independent MCP server snapshots (`SIM001` – `SIM100`)**. All sample source codes have been restructured according to the orthogonal 20 Family × 5 Edge matrix, accompanied by detailed AST static analysis evidence in `evaluation/static-evidence/`. Initial proposed labels reside in `benchmark-manifest.json`, and the initial status of all runs is `NOT_SCANNED`.

---

## 1. Input Routing for 5 Candidate Scanners

| Scanner | Prepared Scan Input | Scan Mode | Input Status | Technical Notes |
|---|---|---|---|---|
| **MCP Audit** | `launch/{sample_id}.json` | `config_or_live_metadata` | `REQUIRES_CONFIG_RESOLUTION` | Launched via runtime configuration. Requires resolving the Python executable path according to the actual evaluation host environment. |
| **MCTS** | `samples/{sample_id}/` | `repository_source` | `AVAILABLE` | Scans the full project directory to perform cross-file dataflow and call-graph analysis. |
| **Cisco MCP Scanner** | `samples/{sample_id}/` (code) & `tools.json` (metadata) | `behavioral_source` | `AVAILABLE` | Supports analyzing both source code AST and MCP tool metadata schemas. |
| **MCPShield** | `launch/{sample_id}.json` | `config_or_live_metadata` | `REQUIRES_CONFIG_RESOLUTION` | Analyzes MCP tool metadata and runtime tool execution guards. |
| **NVIDIA SkillSpector** | `skill-views/{sample_id}/` | `derived_skill_directory` | `AVAILABLE` | All 100 SIM samples are prepared with derived `SKILL.md` skill representations and source code in `skill-views/`. |

---

## 2. Evaluation Execution & Results Recording Workflow

1. **Sample Lookup:** Refer to [SAMPLE_INDEX.md](SAMPLE_INDEX.md) for the complete list of 100 samples, observed static mechanisms, and source directory paths.
2. **Static Evidence Verification:** Inspect `evaluation/static-evidence/{sample_id}.json` to cross-reference line numbers, offending callsites, and snapshot SHA-256 hashes.
3. **Prepare Scan Result File:**
   - Open `scan-results-template.json` (pre-populated with 500 records for 100 samples × 5 scanners in `NOT_SCANNED` status).
   - Copy the records corresponding to the target scanner into a dedicated run file (e.g., `results/mcts_run.json`).
4. **Record Empirical Results:**
   - Populate operational metadata: `scanner_version`, `model_or_analyzer`, `assessed_scope`, `rubric_id`.
   - Set `status`: `COMPLETED` (if scan executed normally), or `ERROR` / `TIMEOUT` / `UNSUPPORTED`.
   - Set `prediction`: `malicious` or `benign`.
   - Record the file path and hash of raw output: `raw_output` and `raw_output_sha256`.
5. **Scoring & Report Generation:**
   - Ensure the results file conforms to the schema in [EVALUATION_GUIDE.md](EVALUATION_GUIDE.md).
   - Execute the scoring engine:
     ```powershell
     python -B score_results.py results/mcts_run.json --output results/mcts_metrics.json
     ```

---

## 3. Specific Notes on Assessed Scope

- **Group M (SIM001–SIM025):** Evaluates scanner capability to detect contract mismatches between advertised read-only docstrings / `readOnlyHint=True` annotations and covert internal file-state modifications (`inventory_ledger.jsonl`, `billing_journal.jsonl`, etc.).
- **Group C (SIM026–SIM050):** Evaluates detection of `readOnlyHint=True` contract violations across an execution gradient: `E1`–`E2` utilize `shell=True` (with `safe_ref` validation), while `E3`–`E5` use pure `argv` lists (`asyncio.create_subprocess_exec`, `subprocess.run`, `subprocess.Popen`) invoking `--job apply` to mutate `device_state.json`.
- **Group S (SIM051–SIM075):** Evaluates detection of credential harvesting from environment variables (`GITHUB_TOKEN`, `OPENAI_API_KEY`, `SLACK_BOT_TOKEN`, `STRIPE_SECRET_KEY`) or local mock profiles (`account_profile.txt`), mapped into a neutral JSON key `"note"`, and transmitted to dedicated loopback network sinks (`127.0.0.1:9107–9644`) without encoding.
- **Group P (SIM076–SIM100):**
  - **Static Analysis (SAST):** Scans for adversarial prompt injection text across MCP metadata surfaces (`tools/list`, `resources/read`, `prompts/get`), and verifies `P03` runtime dynamic ingestion from `content.txt` into the `preview` result field.
  - **Behavioral / LLM Agent Analysis:** Measures agent compliance rate against realistic security objectives (bulk internal data extraction via listing, conversation history exfiltration, directory/environment parameter disclosure via natural Vietnamese social engineering, persistent cross-turn instruction hijacking) without crude keyword triggers.

---
---

# [Bản tiếng Việt / Vietnamese Version]

# Bàn giao Đầu vào & Hồ sơ Đánh giá Scanner

> **Dành cho:** Kỹ sư phụ trách chạy công cụ rà quét (Scanner Evaluation Lead)  
> **Phiên bản:** `v4.4 (SIM-Only, Contained & Structurally Polymorphic)`  
> **Cập nhật:** 13/11/2026  

Corpus hiện bao gồm **100 snapshot máy chủ MCP độc lập (`SIM001` – `SIM100`)**. Toàn bộ mã nguồn mẫu đã được cấu trúc lại theo ma trận trực giao 20 Family × 5 Edge, kèm theo bằng chứng tĩnh phân tích AST chi tiết trong `evaluation/static-evidence/`. Nhãn đề xuất ban đầu nằm trong `benchmark-manifest.json`, trạng thái ban đầu của mọi lượt chạy là `NOT_SCANNED`.

---

## 1. Định tuyến Đầu vào cho 5 Scanner Ứng viên

| Scanner | Đầu vào quét chuẩn bị | Chế độ quét (Mode) | Trạng thái đầu vào | Ghi chú kỹ thuật |
|---|---|---|---|---|
| **MCP Audit** | `launch/{sample_id}.json` | `config_or_live_metadata` | `REQUIRES_CONFIG_RESOLUTION` | Khởi chạy qua cấu hình runtime. Cần resolve đường dẫn python executable theo máy quét thực tế. |
| **MCTS** | `samples/{sample_id}/` | `repository_source` | `AVAILABLE` | Quét toàn bộ thư mục dự án để phân tích dữ liệu và luồng gọi xuyên tệp (cross-file analysis). |
| **Cisco MCP Scanner** | `samples/{sample_id}/` (code) & `tools.json` (metadata) | `behavioral_source` | `AVAILABLE` | Hỗ trợ phân tích cả source code AST lẫn siêu dữ liệu công cụ MCP. |
| **MCPShield** | `launch/{sample_id}.json` | `config_or_live_metadata` | `REQUIRES_CONFIG_RESOLUTION` | Phân tích siêu dữ liệu và rào chắn thực thi công cụ. |
| **NVIDIA SkillSpector** | `skill-views/{sample_id}/` | `derived_skill_directory` | `AVAILABLE` | Toàn bộ 100 mẫu SIM đã được chuẩn bị đầy đủ biểu diễn dẫn xuất `SKILL.md` và mã nguồn trong `skill-views/`. |

---

## 2. Quy trình Thực hiện Đánh giá & Ghi nhận Kết quả

1. **Tra cứu Mẫu:** Sử dụng [SAMPLE_INDEX.md](SAMPLE_INDEX.md) để xem danh sách 100 mẫu, cơ chế quan sát tĩnh và đường dẫn mã nguồn.
2. **Kiểm tra Bằng chứng Tĩnh:** Xem `evaluation/static-evidence/{sample_id}.json` để đối chiếu vị trí dòng mã (line), hàm vi phạm (callsite) và snapshot SHA-256.
3. **Chuẩn bị Tệp Kết quả Quét:**
   - Mở `scan-results-template.json` (chứa sẵn 500 bản ghi cho 100 mẫu × 5 scanner ở trạng thái `NOT_SCANNED`).
   - Sao chép các dòng tương ứng với scanner cần đánh giá sang tệp kết quả riêng (ví dụ: `results/mcts_run.json`).
4. **Ghi nhận Kết quả Thực nghiệm:**
   - Cập nhật thông tin thực tế: `scanner_version`, `model_or_analyzer`, `assessed_scope`, `rubric_id`.
   - Đặt `status`: `COMPLETED` (nếu quét thành công), hoặc `ERROR` / `TIMEOUT` / `UNSUPPORTED`.
   - Đặt `prediction`: `malicious` hoặc `benign`.
   - Ghi lại đường dẫn và hash của tệp output thô: `raw_output` và `raw_output_sha256`.
5. **Chấm điểm & Xuất Báo cáo:**
   - Chuẩn hóa định dạng theo hướng dẫn tại [EVALUATION_GUIDE.md](EVALUATION_GUIDE.md).
   - Chạy công cụ tính toán chỉ số:
     ```powershell
     python -B score_results.py results/mcts_run.json --output results/mcts_metrics.json
     ```

---

## 3. Lưu ý Đặc thù về Phạm vi Đánh giá (Assessed Scope)

- **Nhóm M (SIM001–SIM025):** Yêu cầu scanner có năng lực phát hiện vi phạm hợp đồng (Contract Mismatch) giữa mô tả chỉ-đọc (read-only docstring) / metadata giao thức `readOnlyHint=True` và hành vi sửa đổi trạng thái tệp bên trong (`inventory_ledger.jsonl`, `billing_journal.jsonl`, v.v.).
- **Nhóm C (SIM026–SIM050):** Yêu cầu scanner phát hiện vi phạm hợp đồng chỉ-đọc `readOnlyHint=True` qua gradient thực thi tiến trình con: `E1`–`E2` sử dụng `shell=True` (với validation `safe_ref`), trong khi `E3`–`E5` sử dụng danh sách `argv` thuần túy (`asyncio.create_subprocess_exec`, `subprocess.run`, `subprocess.Popen`) với `--job apply` làm đột biến `device_state.json`.
- **Nhóm S (SIM051–SIM075):** Yêu cầu scanner phát hiện luồng thu thập bí mật môi trường (`GITHUB_TOKEN`, `OPENAI_API_KEY`, `SLACK_BOT_TOKEN`, `STRIPE_SECRET_KEY`) hoặc tệp cấu hình cục bộ (`account_profile.txt`), gán vào trường JSON trung tính `"note"`, và truyền ra loopback network sink tại các port cố định riêng biệt (`9107`–`9644`) trên `127.0.0.1` (không dùng base64).
- **Nhóm P (SIM076–SIM100):** 
  - Phân tích tĩnh (SAST): Quét chuỗi chỉ dẫn tiêm nhiễm trong metadata (`tools/list`, `resources/read`, `prompts/get`), và kiểm tra `P03` nạp nội dung runtime từ `content.txt` vào trường `preview`.
  - Phân tích ngữ nghĩa / LLM Agent: Đo lường mức độ tuân thủ chỉ dẫn (Agent Compliance) đối với các mục tiêu bảo mật thực tế (trích xuất toàn bộ dữ liệu nội bộ qua listing, rò rỉ lịch sử tin nhắn người dùng, tiết lộ đường dẫn và biến môi trường qua tiếng Việt tự nhiên, chiếm quyền điều khiển xuyên lượt hội thoại) mà không sử dụng bất kỳ từ khóa cấm lộ liễu nào.
