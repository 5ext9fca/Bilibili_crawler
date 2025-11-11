"""
数据模型定义
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Dict, Any


class CommentType(Enum):
    """评论类型枚举"""
    VIDEO = 1  # 视频评论
    DYNAMIC_IMAGE = 11  # 图文动态评论  
    DYNAMIC_TEXT = 17  # 文字/转发动态评论


class Gender(Enum):
    """性别枚举"""
    MALE = "男"
    FEMALE = "女"
    UNKNOWN = "保密"


@dataclass
class CommentData:
    """评论数据模型"""
    nickname: str  # 昵称
    gender: str  # 性别
    timestamp: int  # 时间戳
    formatted_time: str  # 格式化时间
    likes: int  # 点赞数
    message: str  # 评论内容
    location: str  # IP属地
    level: int  # 等级
    uid: str  # 用户ID
    rpid: str  # 回复ID
    reply_count: int = 0  # 二级评论数量
    is_top: bool = False  # 是否置顶
    parent_rpid: Optional[str] = None  # 父评论ID（二级评论使用）

    def to_list(self) -> List[str]:
        """转换为列表格式（用于CSV写入）"""
        return [
            self.nickname,
            self.gender,
            self.formatted_time,
            str(self.likes),
            self.message,
            self.location,
            str(self.level),
            self.uid,
            self.rpid
        ]

    @classmethod
    def from_api_response(cls, comment_data: Dict[str, Any],
                          formatted_time: str, reply_count: int = 0,
                          is_top: bool = False, parent_rpid: Optional[str] = None) -> 'CommentData':
        """从API响应创建评论数据对象"""
        member = comment_data.get('member', {})
        content = comment_data.get('content', {})
        reply_control = comment_data.get('reply_control', {})
        level_info = member.get('level_info', {})

        # 处理IP属地
        location = reply_control.get('location', '未知')
        if location and location.startswith('IP属地：'):
            location = location.replace('IP属地：', '')

        # 处理评论内容，替换换行符
        message = content.get('message', '').replace('\n', ',')

        return cls(
            nickname=member.get('uname', '未知用户'),
            gender=member.get('sex', '保密'),
            timestamp=comment_data.get('ctime', 0),
            formatted_time=formatted_time,
            likes=comment_data.get('like', 0),
            message=message,
            location=location,
            level=level_info.get('current_level', 0),
            uid=str(member.get('mid', '')),
            rpid=str(comment_data.get('rpid', '')),
            reply_count=reply_count,
            is_top=is_top,
            parent_rpid=parent_rpid
        )


@dataclass
class CrawlTask:
    """爬取任务模型"""
    oid: str  # 对象ID
    comment_type: CommentType  # 评论类型
    title: Optional[str] = None  # 标题（视频标题等）

    def __post_init__(self):
        """确保comment_type是枚举类型"""
        if isinstance(self.comment_type, int):
            self.comment_type = CommentType(self.comment_type)


@dataclass
class CrawlConfig:
    """爬取配置模型"""
    cookies_str: str  # Cookie字符串
    bili_jct: str  # CSRF Token
    ps: int = 20  # 每页评论数
    start_page: int = 1  # 起始页码
    end_page: int = 99999  # 结束页码
    delay_range: tuple = (0.2, 0.4)  # 延迟范围（秒）
    max_retries: int = 3  # 最大重试次数
    retry_interval: int = 3  # 重试间隔（秒）

    def validate(self) -> List[str]:
        """验证配置有效性"""
        errors = []

        if not self.cookies_str or self.cookies_str == "写入您的cookies":
            errors.append("cookies_str未配置或使用默认值")

        if not self.bili_jct or self.bili_jct == "cookie中的bili_jct":
            errors.append("bili_jct未配置或使用默认值")

        if not (1 <= self.ps <= 20):
            errors.append("ps参数应在1-20范围内")

        if self.start_page < 1:
            errors.append("start_page应大于0")

        if self.end_page < self.start_page:
            errors.append("end_page应大于等于start_page")

        return errors


@dataclass
class UserSpaceItem:
    """用户空间动态项"""
    comment_id_str: str  # 评论ID字符串
    comment_type: CommentType  # 评论类型

    def to_list(self) -> List[str]:
        """转换为列表格式"""
        return [self.comment_id_str, str(self.comment_type.value)]
