__name__#!/usr/bin/env python3
"""
重构后的单个目标爬虫
支持从config.json读取单个目标配置
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.crawler import BilibiliCrawler
from core.config_manager import ConfigManager
from models.data_models import CommentType
from utils.file_utils import setup_logger

logger = setup_logger(__name__)


def main():
    """主函数"""
    try:
        logger.info("=" * 50)
        logger.info("Bilibili单个目标评论爬虫启动")
        logger.info("=" * 50)
        
        # 初始化配置管理器
        config_manager = ConfigManager()
        
        # 加载配置
        if not config_manager.load_config():
            logger.error("配置加载失败，程序退出")
            return False
        
        # 获取单个目标配置
        simple_config = config_manager.get_simple_config()
        
        # 验证必需配置
        required_keys = ['oid', 'type']
        for key in required_keys:
            if key not in simple_config:
                logger.error(f"config.json中缺少必需配置: {key}")
                logger.info("请在config.json中添加以下配置:")
                logger.info('  "oid": "目标ID",')
                logger.info('  "type": 1,  // 1=视频, 11=图文动态, 17=文字动态')
                logger.info('  "down": 1,  // 起始页码')
                logger.info('  "up": 100  // 结束页码')
                return False

        # 解析配置
        config = {
            'oid': str(simple_config['oid']),
            'comment_type': CommentType(int(simple_config['type'])),
            'start_page': simple_config.get('down', 1),
            'end_page': simple_config.get('up', 100),
        }

        logger.info(f"目标配置: OID={config['oid']}, 类型={config['comment_type.name']}, 页码范围={config['start_page']}-{config['end_page']}")
        
        # 创建爬虫实例
        crawler = BilibiliCrawler(config_manager)
        
        # 执行爬取
        success = crawler.crawl_single_target(**config)
        
        if success:
            logger.info("单个目标爬取完成")
            return True
        else:
            logger.error("单个目标爬取失败")
            return False
            
    except KeyboardInterrupt:
        logger.info("用户中断程序")
        return False
    except ValueError as e:
        logger.error(f"配置值错误: {e}")
        return False
    except Exception as e:
        logger.error(f"程序运行时发生异常: {e}")
        return False
    finally:
        logger.info("程序结束")


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)