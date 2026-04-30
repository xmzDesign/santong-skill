#!/usr/bin/env python3
"""
Claude hook/CLI: check Java/MyBatis SQL conventions on changed files.
"""

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

JAVA_EXTENSIONS = {".java"}
SQL_EXTENSIONS = {".xml", ".sql"}
FRONTEND_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx", ".vue", ".css", ".scss", ".less"}
STYLE_EXTENSIONS = {".css", ".scss", ".less", ".vue"}
IGNORED_PARTS = {
    ".git",
    ".idea",
    ".vscode",
    "target",
    "build",
    "dist",
    "node_modules",
    ".harness",
    "coverage",
    ".next",
}

SQL_RULE_CARD = [
    "SQL/ORM 门禁：",
    "1. SQL 必须写在 XML Mapper，禁止 Java 注解内联 SQL。",
    "2. 查询列必须显式列出，禁止 select *。",
    "3. XML 参数使用 #{}，禁止 ${}。",
    "4. 返回映射必须使用 resultMap，禁止 resultClass。",
    "5. 行数统计必须使用 count(*)，禁止 count(column) 或 count(常量)。",
    "6. sum() 结果必须用 IFNULL/COALESCE 兜底 NULL。",
    "7. 更新记录必须维护 update_time。",
    "8. 禁止外键、级联和存储过程承载业务逻辑。",
]

JAVA_RULE_CARD = [
    "Java 总门禁与维度核心门禁：",
    "1. 先契约后实现，先本地后通用，风险必须写入验收项。",
    "2. Controller / Dubbo Provider / Job Handler 只能依赖应用服务接口，禁止依赖 *Impl。",
    "3. MapStruct 必须设置 unmappedTargetPolicy = ReportingPolicy.ERROR。",
    "4. 新增/修改方法必须有中文注释，覆盖用途、参数、返回值和副作用。",
    "5. 金额必须使用 Java BigDecimal 和 DDL DECIMAL(18,3)，禁止 double/float。",
    "6. PageHelper 分页必须有稳定排序。",
    "7. Redis key 必须有命名空间，业务缓存写入必须有 TTL。",
    "8. 密钥必须来自受管配置，禁止硬编码。",
    "9. 公共 client API 必须返回 ApiResponse<T>；Public DTO 必须 Serializable + serialVersionUID。",
    "10. 公共枚举使用 name() 或稳定 code，禁止 ordinal()；日志和外部错误必须脱敏。",
    "11. Domain 不依赖基础设施；Application 不直接操作 MyBatis Mapper。",
]

DISTRIBUTED_JAVA_RULE_CARD = [
    "分布式 Java 门禁：",
    "1. 所有 Java 改动必须声明未触发理由，或列出触发条款、证据和人工确认项。",
    "2. 外部调用必须有超时、重试上限、退避策略和幂等前提。",
    "3. 线程池、队列、worker 必须有业务命名、容量限制、隔离和拒绝策略。",
    "4. 分布式锁必须有命名空间 key、等待/租约超时、finally 释放和持有者校验。",
    "5. 事务边界必须短；跨服务一致性必须有 Outbox/Saga/TCC/补偿路径。",
    "6. 消息必须有 traceId/messageId/业务键，消费者幂等，并有重试/死信/补偿路径。",
    "7. 异步边界必须传递并清理 MDC/ThreadLocal，核心链路必须有日志、指标和 trace。",
]

FRONTEND_RULE_CARD = [
    "前端门禁：",
    "1. 业务样式应使用设计 token/theme 变量；token/theme 文件外不允许硬编码颜色。",
    "2. TSX/JSX/Vue 禁止 inline style，除非是已记录的动态几何、图表或虚拟列表例外。",
    "3. 避免裸全局覆盖；Antd 覆盖必须通过 CSS Modules 或根 class 限定作用域。",
    "4. 禁止使用 !important，除非说明第三方兼容例外。",
    "5. 避免紫色渐变、玻璃拟态、装饰圆球等通用 AI 产品视觉。",
    "6. 前端变更需覆盖适用的 loading/empty/error/disabled/focus-visible 状态。",
]


@dataclass
class Finding:
    severity: str
    rule: str
    path: str
    line: int
    message: str
    snippet: str

    def to_dict(self):
        return {
            "severity": self.severity,
            "rule": self.rule,
            "path": self.path,
            "line": self.line,
            "message": self.message,
            "snippet": self.snippet,
        }


def repo_root() -> Path:
    try:
        output = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL,
            timeout=5,
        )
        return Path(output.decode().strip())
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return Path.cwd()


def is_relevant(path: Path) -> bool:
    return path.suffix.lower() in (JAVA_EXTENSIONS | SQL_EXTENSIONS | FRONTEND_EXTENSIONS)


def is_ignored(path: Path) -> bool:
    return any(part in IGNORED_PARTS for part in path.parts)


def git_changed_files(root: Path) -> list[Path]:
    commands = [
        ["git", "diff", "--name-only", "--diff-filter=ACMRT", "HEAD"],
        ["git", "diff", "--name-only", "--cached", "--diff-filter=ACMRT", "HEAD"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    ]
    seen = set()
    files = []
    for command in commands:
        try:
            output = subprocess.check_output(command, cwd=root, stderr=subprocess.DEVNULL, timeout=10)
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            continue
        for raw in output.decode().splitlines():
            rel = raw.strip()
            if not rel or rel in seen:
                continue
            seen.add(rel)
            path = root / rel
            if path.is_file() and is_relevant(path) and not is_ignored(path):
                files.append(path)
    return files


def all_relevant_files(root: Path) -> list[Path]:
    files = []
    for path in root.rglob("*"):
        if not path.is_file() or not is_relevant(path):
            continue
        if is_ignored(path):
            continue
        files.append(path)
    return files


def rel_path(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")


def is_frontend_token_or_theme_file(root: Path, path: Path) -> bool:
    rel = rel_path(root, path).replace("\\", "/").lower()
    name = path.name.lower()
    return (
        "/tokens/" in rel
        or "/theme/" in rel
        or "/styles/variables" in rel
        or "token" in name
        or "theme" in name
        or name in {"variables.scss", "variables.less", "antd-theme.less"}
    )


def add_finding(findings: list[Finding], severity: str, rule: str, root: Path, path: Path, line_no: int, message: str, line: str):
    findings.append(
        Finding(
            severity=severity,
            rule=rule,
            path=rel_path(root, path),
            line=line_no,
            message=message,
            snippet=line.strip()[:180],
        )
    )


AMOUNT_NAME_RE = re.compile(
    r"(amount|amt|price|fee|cost|money|balance|payment|refund|charge|pay|total|subtotal|discount)",
    re.IGNORECASE,
)
SECRET_NAME_RE = re.compile(
    r"(password|passwd|secret|token|access_?key|secret_?key|private_?key|ak|sk)",
    re.IGNORECASE,
)
SENSITIVE_LOG_RE = re.compile(
    r"(authInfo|password|passwd|secret|apiSecret|appSecret|clientSecret|token|accessToken|refreshToken|authorization|signature|apiKey|x-api-key|privateKey|skey|appKey)",
    re.IGNORECASE,
)
MESSAGE_SEND_RE = re.compile(r"(rocketMQTemplate|kafkaTemplate|rabbitTemplate|jmsTemplate)\s*\.\s*(send|convertAndSend|syncSend|asyncSend)")
ASYNC_BOUNDARY_RE = re.compile(r"(@Async\b|CompletableFuture\.(runAsync|supplyAsync)|new\s+Thread\s*\()")


def java_class_line(text: str, class_name: str) -> int:
    for index, line in enumerate(text.splitlines(), start=1):
        if re.search(rf"\b(class|interface|enum)\s+{re.escape(class_name)}\b", line):
            return index
    return 1


def is_java_entry_path(path: Path) -> bool:
    lowered = str(path).replace("\\", "/").lower()
    name = path.name.lower()
    return (
        any(part in lowered for part in ("/controller/", "/provider/", "/job/", "/handler/"))
        or any(token in name for token in ("controller", "provider", "jobhandler", "handler"))
    )


def normalized_path(path: Path) -> str:
    return str(path).replace("\\", "/").lower()


def is_client_service_file(path: Path, class_name) -> bool:
    lowered = normalized_path(path)
    return "/client/service/" in lowered or "/api/service/" in lowered or (class_name or "").endswith("ClientService")


def is_public_dto_file(path: Path, class_name) -> bool:
    lowered = normalized_path(path)
    return (
        "/client/request/" in lowered
        or "/client/response/" in lowered
        or "/api/request/" in lowered
        or "/api/response/" in lowered
        or ("/client/" in lowered and bool(re.search(r"(Request|Response|DTO)$", class_name or "")))
        or ("/api/" in lowered and bool(re.search(r"(Request|Response|DTO)$", class_name or "")))
    )


def is_domain_file(path: Path) -> bool:
    return "/domain/" in normalized_path(path)


def is_application_file(path: Path) -> bool:
    return "/application/" in normalized_path(path)


def previous_comment_has_chinese(lines: list[str], index: int) -> bool:
    start = max(0, index - 4)
    previous = "\n".join(lines[start:index])
    return bool(re.search(r"[\u4e00-\u9fff]", previous)) and ("/**" in previous or "//" in previous or "*" in previous)


def looks_like_java_method(line: str) -> bool:
    stripped = line.strip()
    if not re.search(r"\b(public|protected|private)\s+", stripped):
        return False
    if re.search(r"\b(class|interface|enum)\b", stripped):
        return False
    if re.search(r"\b(if|for|while|switch|catch)\s*\(", stripped):
        return False
    if not re.search(r"\)\s*(\{|throws\b|$)", stripped):
        return False
    return bool(re.search(r"\b[\w<>\[\], ?]+\s+\w+\s*\(", stripped))


def looks_like_contract_method(line: str) -> bool:
    stripped = line.strip()
    if not stripped or stripped.startswith(("//", "*", "@")):
        return False
    if re.search(r"\b(class|interface|enum|if|for|while|switch|catch|return)\b", stripped):
        return False
    return bool(re.search(r"\w[\w<>\[\], ?]+\s+\w+\s*\([^)]*\)\s*(?:throws\s+[\w, .]+)?;", stripped))


def is_trivial_java_method(line: str) -> bool:
    return bool(re.search(r"\b(get|set|is|equals|hashCode|toString)\w*\s*\(", line))


def scan_java(root: Path, path: Path, findings: list[Finding]):
    text = read_text(path)
    lines = text.splitlines()
    entry_file = is_java_entry_path(path)
    type_match = re.search(r"\b(class|interface|enum)\s+(\w+)", text)
    class_name = type_match.group(2) if type_match else None
    class_kind = type_match.group(1) if type_match else None
    client_service_file = is_client_service_file(path, class_name)
    public_dto_file = is_public_dto_file(path, class_name)
    if type_match and class_name:
        class_line = java_class_line(text, class_name)
        if class_name.endswith("AppService") and not class_name.endswith("AppServiceImpl"):
            if class_kind != "interface":
                add_finding(findings, "fail", "JAVA_SERVICE_INTERFACE_REQUIRED", root, path, class_line, "AppService 必须是接口；实现放在 XxxAppServiceImpl。", lines[class_line - 1] if lines else "")
        if class_name.endswith("AppServiceImpl"):
            expected_interface = class_name[:-4]
            if not re.search(rf"\bimplements\s+[^\{{;]*\b{re.escape(expected_interface)}\b", text):
                add_finding(findings, "fail", "JAVA_SERVICE_IMPL_CONTRACT", root, path, class_line, f"{class_name} 必须实现 {expected_interface}。", lines[class_line - 1] if lines else "")
        if public_dto_file:
            if not re.search(r"\bimplements\s+[^{;]*\bSerializable\b", text):
                add_finding(findings, "fail", "JAVA_PUBLIC_DTO_SERIALIZABLE", root, path, class_line, "Public DTO 必须实现 Serializable。", lines[class_line - 1] if lines else "")
            if "serialVersionUID" not in text:
                add_finding(findings, "fail", "JAVA_PUBLIC_DTO_SERIAL_VERSION_UID", root, path, class_line, "Public DTO 必须声明 private static final long serialVersionUID = 1L。", lines[class_line - 1] if lines else "")

    if "org.mapstruct.Mapper" in text and "@Mapper" in text:
        mapper_line = next((i for i, item in enumerate(lines, start=1) if "@Mapper" in item), 1)
        mapper_snippet = lines[mapper_line - 1] if lines else ""
        if "unmappedTargetPolicy" not in text:
            add_finding(findings, "fail", "JAVA_MAPSTRUCT_UNMAPPED_POLICY", root, path, mapper_line, "MapStruct 必须设置 unmappedTargetPolicy = ReportingPolicy.ERROR。", mapper_snippet)
        elif not re.search(r"unmappedTargetPolicy\s*=\s*(?:ReportingPolicy\.)?ERROR\b", text):
            add_finding(findings, "fail", "JAVA_MAPSTRUCT_UNMAPPED_POLICY", root, path, mapper_line, "MapStruct 的 unmappedTargetPolicy 必须是 ReportingPolicy.ERROR。", mapper_snippet)

    for index, line in enumerate(lines):
        line_no = index + 1
        if is_domain_file(path) and re.search(r"^\s*import\s+.*\b(springframework|mybatis|redis|rocketmq|kafka|feign|okhttp|retrofit)\b", line):
            add_finding(findings, "fail", "JAVA_DOMAIN_INFRA_DEPENDENCY", root, path, line_no, "Domain 代码禁止依赖 Spring 基础设施、MyBatis、Redis、MQ 或 HTTP Client。", line)
        if is_application_file(path) and re.search(r"\b(@Resource|@Autowired|private\s+(?:final\s+)?\w*Mapper\b|\w+Mapper\s+\w+\s*;)", line):
            add_finding(findings, "warn", "JAVA_APPLICATION_DIRECT_MAPPER", root, path, line_no, "Application 层不应直接操作 MyBatis Mapper；请通过 Domain Repository 抽象访问。", line)
        if client_service_file and looks_like_contract_method(line):
            if "ApiResponse" not in line:
                add_finding(findings, "fail", "JAVA_PUBLIC_API_RESPONSE_WRAPPER", root, path, line_no, "公共 client service 方法必须返回 ApiResponse<T>。", line)
            if re.search(r"\b(Entity|DO|Domain|Infrastructure)\b", line):
                add_finding(findings, "fail", "JAVA_PUBLIC_API_INTERNAL_TYPE_LEAK", root, path, line_no, "公共 API 契约禁止暴露 Domain 模型、数据库 Entity 或 Infrastructure 内部类型。", line)
        if re.search(r"@(Select|Update|Insert|Delete)\s*\(", line):
            add_finding(findings, "fail", "JAVA_ANNOTATION_SQL", root, path, line_no, "MyBatis SQL 必须写在 XML Mapper，禁止写在 Java 注解中。", line)
        if re.search(r"\bqueryForList\s*\([^;\n]+,\s*[^,\n]+,\s*[^)\n]+\)", line):
            add_finding(findings, "fail", "IBATIS_MEMORY_PAGING", root, path, line_no, "禁止使用 iBATIS queryForList(statementName, start, size) 做内存分页；分页必须下推到 SQL。", line)
        if re.search(r"\b(HashMap|Hashtable)\s*<", line) and re.search(r"\b(Mapper|Dao|DAO|Repository)\b", path.name + " " + line):
            add_finding(findings, "fail", "MAP_RESULT_OUTPUT", root, path, line_no, "数据库查询结果禁止直接暴露 HashMap/Hashtable；请定义 DO/DTO 和 resultMap。", line)
        if entry_file and re.search(r"\b[A-Z]\w*AppServiceImpl\b", line):
            add_finding(findings, "fail", "JAVA_ENTRY_DEPENDS_ON_IMPL", root, path, line_no, "Controller / Provider / Job Handler 必须依赖 AppService 接口，禁止依赖 AppServiceImpl。", line)
        if re.search(r"\b(?:double|Double|float|Float)\s+\w*", line) and AMOUNT_NAME_RE.search(line):
            add_finding(findings, "fail", "JAVA_MONEY_FLOAT", root, path, line_no, "金额字段必须使用 BigDecimal，禁止 double/float。", line)
        if SECRET_NAME_RE.search(line) and re.search(r"=\s*\"[^\"]{4,}\"", line):
            add_finding(findings, "fail", "JAVA_HARDCODED_SECRET", root, path, line_no, "疑似密钥配置必须外置并可审计，禁止硬编码字面量。", line)
        if re.search(r"\blog\.(trace|debug|info|warn|error)\s*\(", line) and SENSITIVE_LOG_RE.search(line) and not re.search(r"(sanitize|mask|desensit|LogSanitizer)", line):
            add_finding(findings, "fail", "JAVA_LOG_SENSITIVE_DATA", root, path, line_no, "敏感字段写日志前必须脱敏。", line)
        if re.search(r"\bApiResponse\.error\s*\([^;\n]*(?:exception|ex|e)\.getMessage\s*\(", line):
            add_finding(findings, "fail", "JAVA_RAW_EXCEPTION_MESSAGE", root, path, line_no, "外部错误响应禁止暴露原始系统异常消息。", line)
        if "ordinal()" in line:
            add_finding(findings, "fail", "JAVA_ENUM_ORDINAL", root, path, line_no, "外部可见或持久化业务值禁止使用 enum ordinal()；请使用 name() 或显式稳定 code。", line)
        if "PageHelper.startPage" in line:
            window = "\n".join(lines[index:index + 10]).lower()
            if not re.search(r"(order\s+by|\.orderby\s*\(|setorderby\s*\()", window):
                add_finding(findings, "warn", "JAVA_PAGEHELPER_STABLE_ORDER", root, path, line_no, "PageHelper 分页必须包含稳定排序，例如 id desc 或 created_time desc。", line)
        if re.search(r"(redisTemplate|stringRedisTemplate).+\.set\s*\(", line):
            window = "\n".join(lines[index:index + 6])
            if not re.search(r"(TimeUnit|Duration|expire\s*\(|setex|opsForValue\(\)\.set\s*\([^;\n]+,\s*[^;\n]+,\s*\d+\s*,)", window):
                add_finding(findings, "fail", "JAVA_REDIS_TTL", root, path, line_no, "Redis 业务缓存写入必须设置 TTL。", line)
            string_keys = re.findall(r"\"([A-Za-z0-9_.-]{3,})\"", line)
            if string_keys and all(":" not in item for item in string_keys):
                add_finding(findings, "warn", "JAVA_REDIS_KEY_NAMESPACE", root, path, line_no, "Redis key 应包含命名空间，例如 order:detail:{id}。", line)
        if re.search(r"Executors\.newCachedThreadPool\s*\(|new\s+LinkedBlocking(?:Queue|Deque)\s*<[^>]*>\s*\(\s*\)", line):
            add_finding(findings, "fail", "DIST_JAVA_UNBOUNDED_EXECUTOR", root, path, line_no, "分布式 Java 门禁：线程池和队列必须有界、有命名、有隔离，并声明拒绝策略。", line)
        if re.search(r"\.lock\s*\(\s*\)", line):
            add_finding(findings, "warn", "DIST_JAVA_LOCK_WITHOUT_TIMEOUT", root, path, line_no, "分布式 Java 门禁：锁必须有等待超时、租约超时、finally 释放和持有者校验。", line)
        if re.search(r"\.tryLock\s*\(\s*\)", line):
            add_finding(findings, "warn", "DIST_JAVA_LOCK_TRYLOCK_NO_TIMEOUT", root, path, line_no, "分布式 Java 门禁：用于分布式或跨线程协作的 tryLock 应包含有限等待和租约时间。", line)
        if re.search(r"new\s+(?:[A-Za-z0-9_.]+\.)?(RestTemplate|OkHttpClient)\s*\(\s*\)", line):
            add_finding(findings, "warn", "DIST_JAVA_EXTERNAL_CLIENT_TIMEOUT", root, path, line_no, "分布式 Java 门禁：外部 client 必须声明连接/读取超时和重试边界。", line)
        if "@Transactional" in text and re.search(r"(restTemplate|webClient|Feign|Dubbo|rocketMQTemplate|kafkaTemplate|rabbitTemplate|jmsTemplate).*\.(get|post|exchange|invoke|send|convertAndSend|syncSend|asyncSend)\s*\(", line, re.IGNORECASE):
            add_finding(findings, "warn", "DIST_JAVA_TRANSACTION_EXTERNAL_CALL", root, path, line_no, "分布式 Java 门禁：避免在长事务内执行 RPC/MQ/外部调用；必须定义边界和补偿路径。", line)
        if MESSAGE_SEND_RE.search(line):
            window = "\n".join(lines[max(0, index - 4):index + 6])
            if not re.search(r"\b(traceId|messageId)\b", window):
                add_finding(findings, "warn", "DIST_JAVA_MESSAGE_CONTEXT", root, path, line_no, "分布式 Java 门禁：消息必须携带 traceId、messageId 和业务 key，用于幂等与重放。", line)
        if ASYNC_BOUNDARY_RE.search(line):
            window = "\n".join(lines[max(0, index - 4):index + 8])
            if not re.search(r"\b(MDC|traceId|Trace|TransmittableThreadLocal|TTL)\b", window):
                add_finding(findings, "warn", "DIST_JAVA_ASYNC_CONTEXT", root, path, line_no, "分布式 Java 门禁：异步边界必须传递并清理 trace/MDC/ThreadLocal 上下文。", line)
        if re.search(r"\bcatch\s*\(", line):
            block = "\n".join(lines[index:index + 8])
            if re.search(r"\blog\.(warn|error)\s*\(", block) and not re.search(r"(throw|return|compensat|retry|dead.?letter|alarm|alert|fail)", block, re.IGNORECASE):
                add_finding(findings, "warn", "DIST_JAVA_CATCH_ONLY_LOG", root, path, line_no, "分布式 Java 门禁：失败必须可追踪、可恢复，catch 块不能只打日志后继续。", line)
        if looks_like_java_method(line) and not is_trivial_java_method(line) and not previous_comment_has_chinese(lines, index):
            add_finding(findings, "warn", "JAVA_METHOD_COMMENT", root, path, line_no, "新增/修改方法需要中文注释，说明用途、参数、返回值和副作用。", line)


def scan_xml_config(root: Path, path: Path, findings: list[Finding]):
    text = read_text(path)
    for line_no, line in enumerate(text.splitlines(), start=1):
        if "logback" in line.lower():
            add_finding(findings, "fail", "JAVA_LOGBACK_DEPENDENCY", root, path, line_no, "禁止引入 logback 依赖或 API；请遵循项目 Log4j2 日志基线。", line)


def contains_mapper_sql(text: str, path: Path) -> bool:
    lowered = text.lower()
    return (
        path.suffix.lower() == ".sql"
        or "mapper" in str(path).lower()
        or "<mapper" in lowered
        or "<select" in lowered
        or "<update" in lowered
        or "<insert" in lowered
        or "<delete" in lowered
    )


def scan_sql(root: Path, path: Path, findings: list[Finding]):
    text = read_text(path)
    if path.suffix.lower() == ".xml" and not contains_mapper_sql(text, path):
        return
    for line_no, line in enumerate(text.splitlines(), start=1):
        lowered = line.lower()
        if re.search(r"\bselect\s+\*", lowered):
            add_finding(findings, "fail", "SQL_SELECT_STAR", root, path, line_no, "查询字段必须显式列出，禁止 select *。", line)
        if "${" in line:
            add_finding(findings, "fail", "SQL_DOLLAR_PARAM", root, path, line_no, "XML SQL 参数必须使用 #{}，禁止 ${}。", line)
        if re.search(r"\bresultclass\s*=", lowered):
            add_finding(findings, "fail", "MYBATIS_RESULT_CLASS", root, path, line_no, "必须使用显式 <resultMap>，禁止 resultClass。", line)
        if re.search(r"\bcount\s*\(\s*(?!\*\s*\)|distinct\b)[^)]*\)", lowered):
            add_finding(findings, "fail", "SQL_COUNT_NOT_STAR", root, path, line_no, "行数统计必须使用 count(*)，禁止 count(column/constant)。", line)
        if re.search(r"\b(foreign\s+key|references\s+\w+|on\s+(delete|update)\s+cascade)\b", lowered):
            add_finding(findings, "fail", "SQL_FOREIGN_KEY_OR_CASCADE", root, path, line_no, "禁止数据库外键和级联动作；关系语义应在应用/领域逻辑维护。", line)
        if re.search(r"\b(create\s+procedure|create\s+function|call\s+\w+)\b", lowered):
            add_finding(findings, "fail", "SQL_STORED_PROCEDURE", root, path, line_no, "禁止使用存储过程/函数承载业务逻辑。", line)
        if re.search(r"\btruncate\s+table\b", lowered):
            add_finding(findings, "warn", "SQL_TRUNCATE_TABLE", root, path, line_no, "TRUNCATE TABLE is risky in application code; confirm approval, backup, and rollback path.", line)
        if AMOUNT_NAME_RE.search(lowered) and re.search(r"\b(double|float)\b", lowered):
            add_finding(findings, "fail", "SQL_MONEY_FLOAT", root, path, line_no, "金额列必须使用 DECIMAL(18,3)，禁止 double/float。", line)
        if AMOUNT_NAME_RE.search(lowered) and re.search(r"\bdecimal\s*\((?!\s*18\s*,\s*3\s*\))", lowered):
            add_finding(findings, "fail", "SQL_MONEY_DECIMAL_SCALE", root, path, line_no, "金额列必须使用 DECIMAL(18,3)。", line)
        if re.search(r"\bsum\s*\(", lowered) and not re.search(r"\b(ifnull|coalesce)\s*\([^;\n]*sum\s*\(", lowered):
            add_finding(findings, "warn", "SQL_SUM_NULL_SAFE", root, path, line_no, "sum() can return NULL; wrap with IFNULL/COALESCE unless caller explicitly handles NULL.", line)
        if re.search(r"\bis\s+null\b|\bis\s+not\s+null\b", lowered):
            add_finding(findings, "warn", "SQL_NULL_CHECK", root, path, line_no, "Prefer ISNULL(column) / NOT ISNULL(column) for NULL checks per project convention.", line)
        if re.search(r"\bupdate\s+\w+", lowered) and "update_time" not in lowered:
            add_finding(findings, "warn", "SQL_UPDATE_TIME", root, path, line_no, "记录更新必须同步维护 update_time；请确认本更新可豁免或补充 update_time。", line)


def scan_frontend(root: Path, path: Path, findings: list[Finding]):
    text = read_text(path)
    suffix = path.suffix.lower()
    is_token_or_theme = is_frontend_token_or_theme_file(root, path)
    for line_no, line in enumerate(text.splitlines(), start=1):
        lowered = line.lower()
        if suffix in {".tsx", ".jsx", ".vue"} and re.search(r"\bstyle\s*=\s*\{\{", line):
            add_finding(findings, "fail", "FE_INLINE_STYLE", root, path, line_no, "禁止 inline style，除非这是已记录的动态几何、图表或虚拟列表例外。", line)
        if not is_token_or_theme and re.search(r"#[0-9a-fA-F]{3,8}\b", line):
            severity = "fail" if suffix in STYLE_EXTENSIONS else "warn"
            add_finding(findings, severity, "FE_HARDCODED_COLOR", root, path, line_no, "Hardcoded color found outside token/theme files; use semantic token or existing theme variable.", line)
        if not is_token_or_theme and re.search(r"var\(--color-[^)]+\)", line):
            add_finding(findings, "warn", "FE_PRIMITIVE_TOKEN", root, path, line_no, "Primitive color token referenced in component/business style; prefer semantic token such as bg/fg/border/intent/agent.", line)
        if suffix in STYLE_EXTENSIONS and "!important" in line:
            add_finding(findings, "warn", "FE_IMPORTANT", root, path, line_no, "Avoid !important; scope overrides or explain the third-party compatibility exception.", line)
        if suffix in STYLE_EXTENSIONS and ".ant-" in line and ":global" not in line and ":where" not in line:
            add_finding(findings, "warn", "FE_NAKED_ANTD_OVERRIDE", root, path, line_no, "Antd override appears unscoped; wrap it in CSS Modules :global under a module root class.", line)
        if "backdrop-filter" in lowered:
            add_finding(findings, "warn", "FE_GLASSMORPHISM", root, path, line_no, "Glassmorphism is not part of the default B2B SaaS visual baseline; remove or justify.", line)
        if "linear-gradient" in lowered and re.search(r"(8b5cf6|7c3aed|a855f7|purple|violet)", lowered):
            add_finding(findings, "warn", "FE_AI_PURPLE_GRADIENT", root, path, line_no, "Avoid generic purple AI gradients unless explicitly required by the product design system.", line)


def scan_files(root: Path, files: list[Path]) -> list[Finding]:
    findings: list[Finding] = []
    for path in files:
        suffix = path.suffix.lower()
        if suffix in JAVA_EXTENSIONS:
            scan_java(root, path, findings)
        elif suffix in SQL_EXTENSIONS:
            scan_xml_config(root, path, findings)
            if path.name.lower() != "pom.xml":
                scan_sql(root, path, findings)
        elif suffix in FRONTEND_EXTENSIONS:
            scan_frontend(root, path, findings)
    return findings


def format_text(findings: list[Finding], files: list[Path]) -> str:
    if not findings:
        return f"Convention check passed ({len(files)} changed relevant files scanned)."
    fails = [item for item in findings if item.severity == "fail"]
    warns = [item for item in findings if item.severity == "warn"]
    lines = []
    if any(item.rule.startswith("JAVA_") for item in findings):
        lines.extend(JAVA_RULE_CARD)
        lines.append("")
    if any(item.rule.startswith("DIST_JAVA_") for item in findings):
        lines.extend(DISTRIBUTED_JAVA_RULE_CARD)
        lines.append("")
    if any(
        item.rule.startswith(("SQL_", "MYBATIS_", "IBATIS_", "MAP_")) or item.rule == "JAVA_ANNOTATION_SQL"
        for item in findings
    ):
        lines.extend(SQL_RULE_CARD)
        lines.append("")
    if any(item.rule.startswith("FE_") for item in findings):
        lines.extend(FRONTEND_RULE_CARD)
        lines.append("")
    lines.append(f"规范检查在 {len(files)} 个相关文件中发现 {len(fails)} 个 FAIL、{len(warns)} 个 WARN。")
    for item in findings[:60]:
        label = "FAIL" if item.severity == "fail" else "WARN"
        lines.append(f"- [{label}] {item.path}:{item.line} {item.rule}: {item.message}")
        if item.snippet:
            lines.append(f"  `{item.snippet}`")
    if len(findings) > 60:
        lines.append(f"- ... 还有 {len(findings) - 60} 个问题未展示。")
    if fails:
        lines.append("")
        lines.append("现在不要结束任务。请先修复 FAIL 项，重新运行检查后再继续。")
    if warns:
        lines.append("WARN 项必须修复，或在最终回复中明确说明原因与风险。")
    return "\n".join(lines)


def emit_hook(findings: list[Finding], files: list[Path]):
    text = format_text(findings, files)
    fails = [item for item in findings if item.severity == "fail"]
    warns = [item for item in findings if item.severity == "warn"]
    if fails:
        print(json.dumps({"decision": "block", "reason": text}, ensure_ascii=False))
        return
    if warns:
        print(json.dumps({"systemMessage": text}, ensure_ascii=False))
        return
    print(json.dumps({}))


def parse_args():
    parser = argparse.ArgumentParser(description="Check Java/MyBatis SQL coding conventions.")
    parser.add_argument("--changed-only", action="store_true", help="scan changed files only")
    parser.add_argument("--format", choices=["text", "json", "hook"], default="text")
    return parser.parse_args()


def should_run_hook() -> bool:
    raw = sys.stdin.read()
    if not raw.strip():
        return True
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return True
    if payload.get("hook_event_name") == "Stop":
        return True
    if payload.get("tool_name") == "TaskUpdate":
        tool_input = payload.get("tool_input", {})
        return isinstance(tool_input, dict) and tool_input.get("status") == "completed"
    return True


def main():
    args = parse_args()
    if args.format == "hook" and not should_run_hook():
        print(json.dumps({}))
        return
    root = repo_root()
    files = git_changed_files(root) if args.changed_only else all_relevant_files(root)
    findings = scan_files(root, files)

    if args.format == "json":
        print(
            json.dumps(
                {
                    "files_scanned": [rel_path(root, path) for path in files],
                    "findings": [item.to_dict() for item in findings],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    elif args.format == "hook":
        emit_hook(findings, files)
    else:
        print(format_text(findings, files))

    if args.format != "hook" and any(item.severity == "fail" for item in findings):
        sys.exit(1)


if __name__ == "__main__":
    main()
