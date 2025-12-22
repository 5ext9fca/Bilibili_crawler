#!/usr/bin/env python3
"""
重构后的用户空间动态爬取器
"""
import sys

from lib.core.api_client import BilibiliApiClient
from lib.core.config_manager import ConfigManager
from lib.models.data_models import UserSpaceItem, CommentType
from lib.utils.file_utils import setup_logger, write_csv, ensure_directory_exists, add_dir_to_path

add_dir_to_path(__file__)

logger = setup_logger(__name__)


class UserSpaceCrawler:
    """用户空间动态爬取器"""

    CSV_HEADERS = ['comment_id_str', 'comment_type']

    def __init__(self, config_manager: ConfigManager):
        """
        初始化用户空间爬取器
        
        Args:
            config_manager: 配置管理器
        """
        self.config_manager = config_manager
        self.api_client = BilibiliApiClient(config_manager.crawl_config)

        # 确保user目录存在
        ensure_directory_exists('user')

    def crawl_user_dynamics(self, mid: str) -> bool:
        """
        爬取指定用户的所有动态
        
        Args:
            mid: 用户ID
            
        Returns:
            bool: 是否爬取成功
        """
        try:
            logger.info(f"开始爬取用户动态: {mid}")

            # 输出文件路径
            output_file = f"data/user/{mid}.csv"

            # 初始化CSV文件
            write_csv(output_file, [], self.CSV_HEADERS, mode='w')

            # 获取第一页数据
            data = self.api_client.get_user_space_dynamics(mid)
            if not data:
                logger.error("无法获取用户动态数据")
                return False

            # 处理第一页数据
            items_count = self._process_dynamics_data(data, output_file)
            logger.info(f"处理第一页，获得 {items_count} 个动态")

            # 获取后续页面
            offset = data.get('offset')
            page_count = 1

            while offset and data.get('has_more', False):
                try:
                    logger.info(f"获取第 {page_count + 1} 页数据，offset: {offset}")

                    data = self.api_client.get_user_space_dynamics(mid, offset)
                    if not data:
                        logger.warning("获取数据失败，停止爬取")
                        break

                    # 处理数据
                    items_count = self._process_dynamics_data(data, output_file)
                    logger.info(f"处理第 {page_count + 1} 页，获得 {items_count} 个动态")

                    # 更新offset
                    offset = data.get('offset')
                    page_count += 1

                    # 检查是否还有更多数据
                    if not data.get('has_more', False):
                        logger.info("没有更多数据")
                        break

                    # 延迟
                    self.api_client._sleep_random()

                except Exception as e:
                    logger.error(f"处理第 {page_count + 1} 页时发生异常: {e}")
                    break

            logger.info(f"用户动态爬取完成: {mid}，共处理 {page_count} 页")
            return True

        except Exception as e:
            logger.error(f"爬取用户动态失败: {e}")
            return False
        finally:
            self.api_client.close()

    def _process_dynamics_data(self, data: dict, output_file: str) -> int:
        """
        处理动态数据
        
        Args:
            data: API响应数据
            output_file: 输出文件路径
            
        Returns:
            int: 处理的动态数量
        """
        try:
            items = data.get('items', [])
            if not items:
                return 0

            dynamics_data = []

            for item in items:
                try:
                    # 提取基础信息
                    basic = item.get('basic', {})
                    comment_id_str = basic.get('comment_id_str', '')
                    comment_type_value = basic.get('comment_type', 0)

                    if comment_id_str and comment_type_value:
                        # 验证评论类型
                        try:
                            comment_type = CommentType(comment_type_value)

                            user_item = UserSpaceItem(
                                comment_id_str=comment_id_str,
                                comment_type=comment_type
                            )

                            dynamics_data.append(user_item.to_list())

                        except ValueError:
                            logger.warning(f"未知的评论类型: {comment_type_value}")
                            continue

                except Exception as e:
                    logger.warning(f"处理单个动态项时发生异常: {e}")
                    continue

            # 批量写入文件
            if dynamics_data:
                write_csv(output_file, dynamics_data, mode='a')

            return len(dynamics_data)

        except Exception as e:
            logger.error(f"处理动态数据失败: {e}")
            return 0


def main():
    """主函数"""
    try:
        logger.info("=" * 50)
        logger.info("Bilibili用户空间动态爬取器启动")
        logger.info("=" * 50)

        # 获取用户输入
        mid = input("请输入目标用户的UID: ").strip()
        if not mid:
            logger.error("用户ID不能为空")
            return False

        if not mid.isdigit():
            logger.error("用户ID必须是数字")
            return False

        logger.info(f"目标用户ID: {mid}")

        # 初始化配置管理器
        config_manager = ConfigManager()

        # 加载配置
        if not config_manager.load_config():
            logger.error("配置加载失败，程序退出")
            return False

        # 创建爬取器实例
        crawler = UserSpaceCrawler(config_manager)

        # 执行爬取
        success = crawler.crawl_user_dynamics(mid)

        if success:
            logger.info("用户动态爬取完成")
            logger.info(f"结果保存在: user/{mid}.csv")
            logger.info("可以使用批量爬虫对这些动态进行评论爬取")
            return True
        else:
            logger.error("用户动态爬取失败")
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
