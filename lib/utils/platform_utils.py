"""
视频相关工具函数
包含BV/AV号转换等功能
"""
import re

# BV/AV号转换常量
XOR_CODE = 23442827791579
MASK_CODE = 2251799813685247
MAX_AID = 1 << 51
ALPHABET = "FcwAPNKTMug3GV5Lj7EJnHpWsx4tb8haYeviqBz6rkCy12mUSDQX9RdoZf"
ENCODE_MAP = (8, 7, 0, 5, 1, 3, 2, 4, 6)
DECODE_MAP = tuple(reversed(ENCODE_MAP))
BASE = len(ALPHABET)
PREFIX = "BV1"
CODE_LEN = len(ENCODE_MAP)


def av2bv(aid: int) -> str:
    """
    将AV号转换为BV号
    
    Args:
        aid: AV号（整数）
        
    Returns:
        str: BV号字符串
    """
    if not isinstance(aid, int) or aid <= 0:
        raise ValueError("AV号必须是正整数")

    bvid = [""] * 9
    tmp = (MAX_AID | aid) ^ XOR_CODE

    for i in range(CODE_LEN):
        bvid[ENCODE_MAP[i]] = ALPHABET[tmp % BASE]
        tmp //= BASE

    return PREFIX + "".join(bvid)


def bv2av(bvid: str) -> int:
    """
    将BV号转换为AV号
    
    Args:
        bvid: BV号字符串
        
    Returns:
        int: AV号
    """
    if not isinstance(bvid, str) or not bvid.startswith(PREFIX):
        raise ValueError("BV号格式不正确")

    bvid = bvid[len(PREFIX):]
    if len(bvid) != 9:
        raise ValueError("BV号长度不正确")

    tmp = 0
    for i in range(CODE_LEN):
        if bvid[DECODE_MAP[i]] not in ALPHABET:
            raise ValueError("BV号包含无效字符")
        idx = ALPHABET.index(bvid[DECODE_MAP[i]])
        tmp = tmp * BASE + idx

    return (tmp & MASK_CODE) ^ XOR_CODE


def clean_filename(filename: str) -> str:
    """
    清理文件名，将非法字符替换为下划线
    
    Args:
        filename: 原始文件名
        
    Returns:
        str: 清理后的文件名
    """
    if not isinstance(filename, str):
        return str(filename)

    # 替换Windows文件名非法字符
    illegal_chars = r'[\\/:*?"<>|]'
    cleaned = re.sub(illegal_chars, '_', filename)

    # 替换换行符
    cleaned = re.sub(r'\r|\n', '_', cleaned)

    # 去除首尾空格并限制长度
    cleaned = cleaned.strip()[:200]

    return cleaned if cleaned else "unnamed_file"


def validate_bv_format(bvid: str) -> bool:
    """
    验证BV号格式是否正确
    
    Args:
        bvid: BV号字符串
        
    Returns:
        bool: 是否为有效格式
    """
    if not isinstance(bvid, str):
        return False

    if not bvid.startswith(PREFIX):
        return False

    if len(bvid) != len(PREFIX) + 9:
        return False

    body = bvid[len(PREFIX):]
    return all(c in ALPHABET for c in body)


def validate_av_format(aid: str) -> bool:
    """
    验证AV号格式是否正确
    
    Args:
        aid: AV号字符串或数字
        
    Returns:
        bool: 是否为有效格式
    """
    try:
        aid_int = int(aid)
        return aid_int > 0
    except (ValueError, TypeError):
        return False
