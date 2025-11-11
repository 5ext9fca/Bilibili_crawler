"""
时间处理工具函数
"""
import datetime
from typing import Optional

import pytz


def timestamp_to_beijing_time(timestamp: int, format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
    """
    将时间戳转换为北京时间字符串
    
    Args:
        timestamp: Unix时间戳
        format_str: 时间格式字符串
        
    Returns:
        str: 格式化的北京时间字符串
    """
    try:
        # 转换为UTC时间
        dt_object = datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc)

        # 转换为北京时间
        beijing_tz = pytz.timezone('Asia/Shanghai')
        beijing_time = dt_object.astimezone(beijing_tz)

        return beijing_time.strftime(format_str)
    except (ValueError, OSError) as e:
        return f"时间转换错误: {e}"


def get_current_beijing_time(format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
    """
    获取当前北京时间
    
    Args:
        format_str: 时间格式字符串
        
    Returns:
        str: 格式化的当前北京时间
    """
    beijing_tz = pytz.timezone('Asia/Shanghai')
    now = datetime.datetime.now(beijing_tz)
    return now.strftime(format_str)


def validate_timestamp(timestamp: int) -> bool:
    """
    验证时间戳是否有效
    
    Args:
        timestamp: Unix时间戳
        
    Returns:
        bool: 是否为有效时间戳
    """
    try:
        # 检查时间戳范围（1970年到2050年）
        min_timestamp = 0
        max_timestamp = 2524608000  # 2050年

        return min_timestamp <= timestamp <= max_timestamp
    except (TypeError, ValueError):
        return False


def parse_time_string(time_str: str) -> Optional[datetime.datetime]:
    """
    解析时间字符串
    
    Args:
        time_str: 时间字符串
        
    Returns:
        datetime对象或None
    """
    # 常见的时间格式
    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M:%S 北京时间',
        '%Y/%m/%d %H:%M:%S',
        '%Y-%m-%d',
    ]

    # 清理时间字符串
    cleaned_time = time_str.strip()
    if ' 北京时间' in cleaned_time:
        cleaned_time = cleaned_time.replace(' 北京时间', '')

    for fmt in formats:
        try:
            return datetime.datetime.strptime(cleaned_time, fmt)
        except ValueError:
            continue

    return None
