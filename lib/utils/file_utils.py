"""
文件操作工具函数
"""
import csv
import json
import logging
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

from lib.utils.login_utils import CONFIG_PATH


def setup_logger(name: str, log_file: str = 'crawler.log') -> logging.Logger:
    """
    设置日志记录器
    
    Args:
        name: 日志器名称
        log_file: 日志文件路径
        
    Returns:
        Logger: 配置好的日志器
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # 避免重复添加处理器
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    _add_handler(file_handler, formatter, logger)

    console_handler = logging.StreamHandler()
    _add_handler(console_handler, formatter, logger)

    return logger


def _add_handler(handler: logging.Handler, formatter: logging.Formatter, logger: logging.Logger):
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def write_csv(file_path: str, data: List[List[Any]], headers: Optional[List[str]] = None,
              mode: str = 'w', encoding: str = 'utf-8-sig') -> bool:
    """
    写入CSV文件
    
    Args:
        file_path: 文件路径
        data: 数据列表
        headers: 表头
        mode: 写入模式 ('w', 'a')
        encoding: 编码格式
        
    Returns:
        bool: 是否写入成功
    """
    try:
        ensure_directory_exists(os.path.dirname(file_path))

        with open(file_path, mode=mode, newline='', encoding=encoding) as file:
            writer = csv.writer(file)

            # 写入表头（仅在写入模式下）
            if headers and mode == 'w':
                writer.writerow(headers)

            # 写入数据
            if data:
                writer.writerows(data)

        return True
    except Exception as e:
        logging.error(f"写入CSV文件失败: {file_path}, 错误: {e}")
        return False


def read_csv(file_path: str, encoding: str = 'utf-8') -> List[List[str]]:
    """
    读取CSV文件
    
    Args:
        file_path: 文件路径
        encoding: 编码格式
        
    Returns:
        List[List[str]]: CSV数据
    """
    try:
        with open(file_path, mode='r', encoding=encoding) as file:
            reader = csv.reader(file)
            return list(reader)
    except Exception as e:
        logging.error(f"读取CSV文件失败: {file_path}, 错误: {e}")
        return []


def load_json_config(config_path: str) -> Dict[str, Any]:
    """
    加载JSON配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        Dict: 配置字典
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"配置文件不存在: {config_path}")
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"配置文件格式错误: {config_path}, 错误: {e}")
        return {}


def save_json_config(config_path: str, config: Dict[str, Any]) -> bool:
    """
    保存JSON配置文件
    
    Args:
        config_path: 配置文件路径
        config: 配置字典
        
    Returns:
        bool: 是否保存成功
    """
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logging.error(f"保存配置文件失败: {config_path}, 错误: {e}")
        return False


def ensure_directory_exists(directory: str) -> None:
    """
    确保目录存在，不存在则创建
    
    Args:
        directory: 目录路径
        
    Returns:
        bool: 是否创建成功或已存在
    """
    try:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
    except Exception as e:
        raise Exception(f"创建目录失败: {directory}, 错误: {e}")


def get_files_in_directory(directory: str, extension: str = '.csv') -> List[str]:
    """
    获取目录下指定扩展名的文件列表
    
    Args:
        directory: 目录路径
        extension: 文件扩展名
        
    Returns:
        List[str]: 文件路径列表
    """
    try:
        if not os.path.exists(directory):
            return []

        files = []
        for filename in os.listdir(directory):
            if filename.endswith(extension):
                files.append(os.path.join(directory, filename))

        return files
    except Exception as e:
        logging.error(f"读取目录文件失败: {directory}, 错误: {e}")
        return []


def append_to_file(file_path: str, content: str, encoding: str = 'utf-8') -> bool:
    """
    追加内容到文件
    
    Args:
        file_path: 文件路径
        content: 要追加的内容
        encoding: 编码格式
        
    Returns:
        bool: 是否追加成功
    """
    try:
        # 确保目录存在
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        with open(file_path, 'a', encoding=encoding) as f:
            f.write(content)
        return True
    except Exception as e:
        logging.error(f"追加文件内容失败: {file_path}, 错误: {e}")
        return False


def add_dir_to_path(file):
    """添加文件所在目录到Python路径"""
    sys.path.insert(0, os.path.dirname(os.path.abspath(file)))


def merge_config(cookies_str: str, bili_jct: str, config_path: Path = CONFIG_PATH) -> bool:
    config = load_json_config(str(config_path)) or {}
    config.update({"cookies_str": cookies_str, "bili_jct": bili_jct})
    return save_json_config(str(config_path), config)
