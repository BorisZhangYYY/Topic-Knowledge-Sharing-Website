from __future__ import annotations

import os
from configparser import ConfigParser
from pathlib import Path
from typing import Dict, Mapping, Optional


def read_global_conf(path: Optional[str] = None) -> Dict[str, Dict[str, str]]:
    """从 global.conf 读取键值配置。

    本函数加载 INI 风格的配置文件（包含 [flask]、[postgres] 等章节），
    并返回嵌套字典。如果文件缺失，则返回空字典。在本项目中，
    global.conf 中的值优先于进程环境变量；如果某个键在 global.conf 中
    不存在，则回退到环境变量，然后是内置默认值。

    Args:
        path: 配置文件的绝对或相对路径。如果为 None，函数会在本模块
            所在目录中查找名为 'global.conf' 的文件。

    Returns:
        嵌套字典，将章节名称映射到键值对（字符串键和值）的字典。
    """
    cfg_path = Path(path) if path else Path(__file__).resolve().parent / "global.conf"
    if not cfg_path.exists():
        return {}
    parser = ConfigParser()
    parser.read(cfg_path)
    result: Dict[str, Dict[str, str]] = {}
    for section in parser.sections():
        result[section] = {k: v for k, v in parser.items(section)}
    return result


_GLOBAL_CONF: Mapping[str, Mapping[str, str]] = read_global_conf()


def get_conf_str(section: str, key: str, env_key: str, default: str) -> str:
    """使用项目优先级规则读取字符串配置。"""
    sec = _GLOBAL_CONF.get(section, {})
    val = sec.get(key)
    if val is not None:
        return str(val)
    env_val = os.getenv(env_key)
    if env_val is not None:
        return env_val
    return default


def get_conf_int(section: str, key: str, env_key: str, default: int) -> int:
    """使用项目优先级规则读取整数配置。"""
    sec = _GLOBAL_CONF.get(section, {})
    sec_val = sec.get(key)
    if sec_val is not None:
        try:
            return int(sec_val)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return default
    env_val = os.getenv(env_key)
    if env_val is not None:
        try:
            return int(env_val)
        except ValueError:
            return default
    return default


def get_conf_bool(section: str, key: str, env_key: str, default: bool) -> bool:
    """使用项目优先级规则读取布尔配置。"""
    truthy = {"1", "true", "yes", "on"}
    falsy = {"0", "false", "no", "off"}
    sec_val = _GLOBAL_CONF.get(section, {}).get(key)
    if sec_val is not None:
        val = str(sec_val).strip().lower()
        if val in truthy:
            return True
        if val in falsy:
            return False
    env_val = os.getenv(env_key)
    if env_val is not None:
        val = env_val.strip().lower()
        if val in truthy:
            return True
        if val in falsy:
            return False
    return default

def build_postgres_dsn(user: str, password: str, host: str, port: int, db: str) -> str:
    """构建 PostgreSQL DSN 字符串。

    Args:
        user: 数据库用户名。
        password: 数据库密码，可能为空。
        host: 数据库主机地址。
        port: 数据库端口。
        db: 数据库名称。

    Returns:
        形如 postgresql://user[:password]@host:port/db 的 DSN 字符串。
    """
    auth = f"{user}:{password}@" if password else f"{user}@"
    return f"postgresql://{auth}{host}:{port}/{db}"
