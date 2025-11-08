"""
B站API客户端
"""
import requests
import time
import random
from urllib3.util.retry import Retry
from typing import Dict, Any, Optional, List
from models.data_models import CrawlConfig, CommentType
from utils.file_utils import setup_logger
from utils.time_utils import timestamp_to_beijing_time

logger = setup_logger(__name__)


class BilibiliApiClient:
    """B站API客户端"""
    
    # API端点
    MAIN_COMMENT_URL = 'https://api.bilibili.com/x/v2/reply/main'
    REPLY_COMMENT_URL = 'https://api.bilibili.com/x/v2/reply/reply'
    VIDEO_INFO_URL = 'https://api.bilibili.com/x/web-interface/view'
    USER_SPACE_URL = 'https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/space'
    
    def __init__(self, config: CrawlConfig):
        """
        初始化API客户端
        
        Args:
            config: 爬取配置
        """
        self.config = config
        self.session = self._create_session()
        self.headers = self._create_headers()
        
    def _create_session(self) -> requests.Session:
        """创建requests会话"""
        session = requests.Session()
        
        # 配置重试策略
        retries = Retry(
            total=self.config.max_retries,
            backoff_factor=0.1,
            status_forcelist=[500, 502, 503, 504]
        )
        
        adapter = requests.adapters.HTTPAdapter(max_retries=retries)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        return session
    
    def _create_headers(self) -> Dict[str, str]:
        """创建请求头"""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Cookie': self.config.cookies_str,
            'csrf': self.config.bili_jct,
        }
    
    def _sleep_random(self):
        """随机延迟"""
        delay = random.uniform(*self.config.delay_range)
        time.sleep(delay)
    
    def get_video_info(self, bvid: str) -> Optional[Dict[str, Any]]:
        """
        获取视频信息
        
        Args:
            bvid: BV号
            
        Returns:
            Dict: 视频信息或None
        """
        try:
            params = {'bvid': bvid}
            response = self.session.get(
                self.VIDEO_INFO_URL, 
                params=params, 
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    return data.get('data')
                else:
                    logger.error(f"获取视频信息失败: {data.get('message')}")
            else:
                logger.error(f"请求失败，状态码: {response.status_code}")
                
        except Exception as e:
            logger.error(f"获取视频信息异常: {e}")
            
        return None
    
    def get_main_comments(self, oid: str, comment_type: CommentType, 
                         page: int = 1) -> Optional[Dict[str, Any]]:
        """
        获取主评论
        
        Args:
            oid: 对象ID
            comment_type: 评论类型
            page: 页码
            
        Returns:
            Dict: API响应数据或None
        """
        try:
            params = {
                'next': str(page),
                'type': comment_type.value,
                'oid': oid,
                'ps': self.config.ps,
                'mode': '3'
            }
            
            response = self.session.get(
                self.MAIN_COMMENT_URL,
                params=params,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    logger.info(f"成功获取第{page}页主评论，URL: {response.url}")
                    return data.get('data')
                else:
                    logger.error(f"获取主评论失败: {data.get('message')}")
            else:
                logger.error(f"请求失败，状态码: {response.status_code}")
                
        except Exception as e:
            logger.error(f"获取主评论异常: {e}")
            
        return None
    
    def get_reply_comments(self, oid: str, comment_type: CommentType,
                          root_rpid: str, page: int = 1) -> Optional[Dict[str, Any]]:
        """
        获取二级评论
        
        Args:
            oid: 对象ID
            comment_type: 评论类型
            root_rpid: 根评论ID
            page: 页码
            
        Returns:
            Dict: API响应数据或None
        """
        try:
            params = {
                'type': comment_type.value,
                'oid': oid,
                'ps': self.config.ps,
                'pn': str(page),
                'root': root_rpid
            }
            
            response = self.session.get(
                self.REPLY_COMMENT_URL,
                params=params,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    logger.info(f"成功获取二级评论，根评论ID: {root_rpid}, 页码: {page}")
                    return data.get('data')
                else:
                    logger.error(f"获取二级评论失败: {data.get('message')}")
            else:
                logger.error(f"请求失败，状态码: {response.status_code}")
                
        except Exception as e:
            logger.error(f"获取二级评论异常: {e}")
            
        return None
    
    def get_user_space_dynamics(self, mid: str, offset: str = None) -> Optional[Dict[str, Any]]:
        """
        获取用户空间动态
        
        Args:
            mid: 用户ID
            offset: 偏移量
            
        Returns:
            Dict: API响应数据或None
        """
        try:
            params = {'host_mid': mid}
            if offset:
                params.update({
                    'next': '2',
                    'offset': str(offset)
                })
            
            response = self.session.get(
                self.USER_SPACE_URL,
                params=params,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    logger.info(f"成功获取用户空间动态，用户ID: {mid}")
                    return data.get('data')
                else:
                    logger.error(f"获取用户空间动态失败: {data.get('message')}")
            else:
                logger.error(f"请求失败，状态码: {response.status_code}")
                
        except Exception as e:
            logger.error(f"获取用户空间动态异常: {e}")
            
        return None
    
    def close(self):
        """关闭会话"""
        if self.session:
            self.session.close()