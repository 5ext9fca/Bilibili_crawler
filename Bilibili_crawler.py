#!/usr/bin/env python3
"""
重构后的Bilibili批量爬虫
使用面向对象设计，提升可读性和可维护性
"""
import sys

from lib.core.config_manager import ConfigManager
from lib.core.crawler import BilibiliCrawler
from lib.utils.file_utils import setup_logger, add_dir_to_path

add_dir_to_path(__file__)

logger = setup_logger(__name__)


def main():
    """主函数"""
    try:
        logger.info("=" * 50)
        logger.info("Bilibili批量评论爬虫启动")
        logger.info("=" * 50)

        # 初始化配置管理器
        config_manager = ConfigManager()

        # 加载配置
        if not config_manager.load_config():
            logger.error("配置加载失败，程序退出")
            return False

        # 创建爬虫实例
        crawler = BilibiliCrawler(config_manager)

        # 执行批量爬取
        success = crawler.crawl_batch_targets()

        if success:
            logger.info("批量爬取任务全部完成")
            return True
        else:
            logger.warning("部分批量爬取任务失败")
            return False

    except KeyboardInterrupt:
        logger.info("用户中断程序")
        return False
    except Exception as e:
        logger.error(f"程序运行时发生异常: {e}")
        return False
    finally:
        logger.info("程序结束")


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
