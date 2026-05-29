"""文件分类和关联文件识别的启发式规则

不做 AST 解析，仅通过路径模式匹配进行分类。
"""

# 模块类型分类规则：按路径前缀/后缀匹配
MODULE_RULES: list[tuple[str, list[str]]] = [
    ("tests", ["test_", "_test.", "tests/", "test/", "spec/", "__tests__/"]),
    ("config", [".json", ".yaml", ".yml", ".toml", ".cfg", ".ini", ".env", "dockerfile", "makefile"]),
    ("docs", [".md", ".rst", ".txt", "docs/", "documentation/", "readme"]),
    ("frontend", ["frontend/", "src/components/", "src/pages/", "src/views/",
                  ".vue", ".tsx", ".jsx", ".css", ".scss", ".less"]),
    ("backend", ["backend/", "app/", "api/", "services/", "models/", "routes/",
                 "middleware/", "utils/", ".py"]),
]


def classify_file(path: str, status: str = "modified") -> str:
    """根据文件路径分类为模块类型

    按优先级从上到下匹配，命中即返回。未命中返回 "unknown"。
    """
    path_lower = path.lower()

    for module_type, patterns in MODULE_RULES:
        for pattern in patterns:
            if pattern in path_lower:
                return module_type

    return "unknown"


def find_related_tests(file_path: str) -> list[str]:
    """根据源文件路径推测关联的测试文件路径

    规则：
    - backend/app/services/foo.py → backend/tests/test_foo.py
    - frontend/src/components/Bar.vue → 暂无自动生成，返回空
    - 已经是测试文件则不返回
    """
    path_lower = file_path.lower()
    is_test = any(seg in path_lower for seg in ["test_", "_test.", "tests/", "test/", "spec/", "__tests__/"])

    if is_test:
        return []

    candidates: list[str] = []

    # Python 后端: app/services/foo.py → tests/test_foo.py
    if file_path.endswith(".py"):
        parts = file_path.rsplit("/", 1)
        filename = parts[-1] if len(parts) > 1 else file_path
        name = filename.replace(".py", "")
        # 尝试多种路径模式
        if "/app/" in file_path or file_path.startswith("app/"):
            candidates.append(f"{file_path.split('/app/')[0]}/tests/test_{name}.py")
        candidates.append(f"tests/test_{name}.py")

    # Vue/React 前端: src/components/Foo.vue → src/components/__tests__/Foo.spec.ts
    if any(file_path.endswith(ext) for ext in [".vue", ".tsx", ".jsx"]):
        parts = file_path.rsplit("/", 1)
        filename = parts[-1] if len(parts) > 1 else file_path
        name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        dir_path = parts[0] if len(parts) > 1 else ""
        candidates.append(f"{dir_path}/__tests__/{name}.spec.ts")

    return candidates
