"""守 RL-（Task 3 定號後回填）：三材質各有唯一的家、generated 禁手改。

tools/docsync：rev6 治理工具 package（純標準庫）。子命令見 __main__.py。
"""
import os

VERSION = "0.1.0"
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

# 路徑常數名冊（相對 ROOT）
EVENTS = "docs/ops/events.jsonl"
RULES = "docs/ops/RULES.md"
BACKLOG = "docs/ops/BACKLOG.md"
BACKLOG_DEFERRED = "docs/ops/BACKLOG-DEFERRED.md"
LESSONS_INDEX = "docs/ops/LESSONS.md"
LESSONS_DIR = "docs/ops/LESSONS"
ADR_DIR = "docs/arc42/decisions"
GENERATED_DIR = "docs/generated"
CONSTITUTION = ".specify/memory/constitution.md"
DEFAULT_BRANCH = "rev6-admin-root"
SUBMODULES = ("base-web", "rust-api")
COMPOSE_FILES = ("docker-compose.yml", "docker-compose.dev.yml", "docker-compose.example.yml")
