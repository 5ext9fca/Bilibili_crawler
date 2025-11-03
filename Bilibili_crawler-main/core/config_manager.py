"""
配置管理器
"""
import os
from typing import Dict, Any, List
from models.data_models import CrawlConfig
from utils.file_utils import load_json_config, save_json_config, setup_logger

logger = setup_logger(__name__)


class ConfigManager:
    """配置管理器"""
    
    DEFAULT_CONFIG_PATH = 'config.json'
    
    def __init__(self, config_path: str = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self._config_data = {}
        self._crawl_config = None
        
    def load_config(self) -> bool:
        """
        加载配置文件
        
        Returns:
            bool: 是否加载成功
        """
        try:
            self._config_data = load_json_config(self.config_path)
            if not self._config_data:
                logger.error(f"配置文件为空或不存在: {self.config_path}")
                return False
                
            # 创建爬取配置对象
            self._crawl_config = self._create_crawl_config()
            
            # 验证配置
            errors = self._crawl_config.validate()
            if errors:
                logger.error("配置验证失败:")
                for error in errors:
                    logger.error(f"  - {error}")
                return False
                
            logger.info("配置加载成功")
            return True
            
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return False
    
    def _create_crawl_config(self) -> CrawlConfig:
        """创建爬取配置对象"""
        return CrawlConfig(
            cookies_str=self._config_data.get('cookies_str', ''),
            bili_jct=self._config_data.get('bili_jct', ''),
            ps=int(self._config_data.get('ps', 20)),
            start_page=int(self._config_data.get('start', 1)),
            end_page=int(self._config_data.get('end', 99999)),
            delay_range=(0.2, 0.4),
            max_retries=3,
            retry_interval=3
        )
    
    @property
    def crawl_config(self) -> CrawlConfig:
        """获取爬取配置"""
        if self._crawl_config is None:
            raise RuntimeError("配置未加载，请先调用load_config()")
        return self._crawl_config
    
    def get_simple_config(self) -> Dict[str, Any]:
        """获取simple_bili_crawler的配置"""
        required_keys = ['oid', 'type', 'file_path_1', 'file_path_2', 'file_path_3', 'down', 'up']
        config = {}
        
        for key in required_keys:
            if key in self._config_data:
                config[key] = self._config_data[key]
            else:
                logger.warning(f"simple_bili_crawler配置缺少必需键: {key}")
                
        return config
    
    def save_config(self, new_config: Dict[str, Any]) -> bool:
        """
        保存配置文件
        
        Args:
            new_config: 新的配置字典
            
        Returns:
            bool: 是否保存成功
        """
        try:
            self._config_data.update(new_config)
            return save_json_config(self.config_path, self._config_data)
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
            return False
    
    def get_user_agent(self) -> str:
        """获取User-Agent"""
        return self._config_data.get(
            'user_agent', 
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        )
    
    def get_output_paths(self, base_name: str) -> Dict[str, str]:
        """
        获取输出文件路径
        
        Args:
            base_name: 基础文件名
            
        Returns:
            Dict: 包含不同类型文件路径的字典
        """
        return {
            'main_comments': f"comments/{base_name}_1.csv",
            'sub_comments': f"comments/{base_name}_2.csv", 
            'all_comments': f"comments/{base_name}_3.csv"
        }
    
    def create_default_config(self) -> bool:
        """创建默认配置文件"""
        default_config = {
            "cookies_str": "写入您的cookies",
            "bili_jct": "cookie中的bili_jct",
            "ps": "20",
            "start": 1,
            "end": 99999,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
        
        try:
            return save_json_config(self.config_path, default_config)
        except Exception as e:
            logger.error(f"创建默认配置文件失败: {e}")
            return False