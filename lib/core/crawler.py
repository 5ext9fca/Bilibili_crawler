"""
B站爬虫核心类
"""
import math
from typing import List, Optional, Dict

from lib.core.api_client import BilibiliApiClient
from lib.core.config_manager import ConfigManager
from lib.models.data_models import CrawlTask, CommentData, CommentType
from lib.utils.file_utils import setup_logger, write_csv, ensure_directory_exists, get_files_in_directory, read_csv
from lib.utils.time_utils import timestamp_to_beijing_time
from lib.utils.platform_utils import av2bv, clean_filename

logger = setup_logger(__name__)


class BilibiliCrawler:
    """B站评论爬虫主类"""

    # CSV表头
    CSV_HEADERS = ['昵称', '性别', '时间', '点赞', '评论', 'IP属地', '等级', 'uid', 'rpid']

    def __init__(self, config_manager: ConfigManager):
        """
        初始化爬虫
        
        Args:
            config_manager: 配置管理器
        """
        self.config_manager = config_manager
        self.api_client = BilibiliApiClient(config_manager.crawl_config)
        self.progress_tracker = ProgressTracker()

        # 确保输出目录存在
        ensure_directory_exists('comments')
        ensure_directory_exists('user')

    def crawl_single_target(self, oid: str, comment_type: CommentType,
                            start_page: int = None, end_page: int = None) -> bool:
        """
        爬取单个目标的评论
        
        Args:
            oid: 对象ID
            comment_type: 评论类型
            start_page: 起始页码
            end_page: 结束页码
            
        Returns:
            bool: 是否爬取成功
        """
        try:
            logger.info(f"开始爬取单个目标: OID={oid}, 类型={comment_type.name}")

            # 获取文件名
            file_base_name = self._get_file_base_name(oid, comment_type)
            if not file_base_name:
                logger.error("无法生成文件名")
                return False

            # 获取输出路径
            output_paths = self.config_manager.get_output_paths(file_base_name)

            # 初始化CSV文件
            self._init_csv_files(output_paths)

            # 爬取置顶评论
            self._crawl_top_comments(oid, comment_type, output_paths)

            # 爬取普通评论
            config = self.config_manager.crawl_config
            start = start_page or config.start_page
            end = end_page or config.end_page

            success = self._crawl_main_comments(oid, comment_type, output_paths, start, end)

            if success:
                logger.info(f"单个目标爬取完成: {file_base_name}")
                return True
            else:
                logger.error(f"单个目标爬取失败: {file_base_name}")
                return False

        except Exception as e:
            logger.error(f"爬取单个目标时发生异常: {e}")
            return False
        finally:
            self.api_client.close()

    def crawl_batch_targets(self) -> bool:
        """
        批量爬取目标评论
        
        Returns:
            bool: 是否全部爬取成功
        """
        try:
            logger.info("开始批量爬取")

            # 获取任务列表
            tasks = self._load_batch_tasks()
            if not tasks:
                logger.error("没有找到批量任务")
                return False

            logger.info(f"找到 {len(tasks)} 个爬取任务")

            success_count = 0
            total_count = len(tasks)

            for i, task in enumerate(tasks, 1):
                logger.info(f"处理第 {i}/{total_count} 个任务: OID={task.oid}")

                try:
                    if self.crawl_single_target(task.oid, task.comment_type):
                        success_count += 1
                        # 记录进度
                        self.progress_tracker.record_completed_task(task)
                    else:
                        logger.error(f"任务失败: OID={task.oid}")

                except Exception as e:
                    logger.error(f"处理任务时发生异常: OID={task.oid}, 错误: {e}")

                # 随机延迟
                self.api_client._sleep_random()

            logger.info(f"批量爬取完成，成功: {success_count}/{total_count}")
            return success_count == total_count

        except Exception as e:
            logger.error(f"批量爬取时发生异常: {e}")
            return False
        finally:
            self.api_client.close()

    def _load_batch_tasks(self) -> List[CrawlTask]:
        """加载批量任务"""
        tasks = []
        csv_files = get_files_in_directory('user', '.csv')

        for file_path in csv_files:
            try:
                data = read_csv(file_path)
                # 跳过表头
                for row in data[1:]:
                    if len(row) >= 2:
                        oid = row[0].strip()
                        comment_type = CommentType(int(row[1]))
                        tasks.append(CrawlTask(oid=oid, comment_type=comment_type))

            except Exception as e:
                logger.error(f"读取任务文件失败: {file_path}, 错误: {e}")

        return tasks

    def _get_file_base_name(self, oid: str, comment_type: CommentType) -> Optional[str]:
        """获取文件基础名称"""
        try:
            if comment_type == CommentType.VIDEO:
                # 获取视频标题
                bvid = av2bv(int(oid))
                video_info = self.api_client.get_video_info(bvid)
                if video_info and 'title' in video_info:
                    title = clean_filename(video_info['title'])
                    return title
                else:
                    logger.warning(f"无法获取视频标题，使用OID: {oid}")
                    return f"video_{oid}"
            else:
                # 动态使用OID作为文件名
                return f"dynamic_{oid}"

        except Exception as e:
            logger.error(f"生成文件名失败: {e}")
            return None

    def _init_csv_files(self, output_paths: Dict[str, str]):
        """初始化CSV文件"""
        for file_path in output_paths.values():
            write_csv(file_path, [], self.CSV_HEADERS, mode='w')

    def _crawl_top_comments(self, oid: str, comment_type: CommentType,
                            output_paths: Dict[str, str]):
        """爬取置顶评论"""
        try:
            data = self.api_client.get_main_comments(oid, comment_type, page=1)
            if not data:
                return

            top_replies = data.get('top_replies')
            if not top_replies:
                logger.info("没有置顶评论")
                return

            logger.info(f"发现 {len(top_replies)} 条置顶评论")

            for reply in top_replies:
                # 处理主评论
                formatted_time = timestamp_to_beijing_time(reply.get('ctime', 0))
                reply_count = reply.get('rcount', 0)

                comment = CommentData.from_api_response(
                    reply, formatted_time, reply_count, is_top=True
                )

                # 写入文件
                self._write_comment_to_files(comment, output_paths)

                # 处理二级评论
                if reply_count > 0:
                    self._crawl_sub_comments(
                        oid, comment_type, comment.rpid,
                        reply_count, output_paths
                    )

        except Exception as e:
            logger.error(f"爬取置顶评论失败: {e}")

    def _crawl_main_comments(self, oid: str, comment_type: CommentType,
                             output_paths: Dict[str, str], start_page: int,
                             end_page: int) -> bool:
        """爬取主评论"""
        try:
            for page in range(start_page, end_page + 1):
                try:
                    data = self.api_client.get_main_comments(oid, comment_type, page)

                    if not data:
                        logger.warning(f"第 {page} 页没有数据")
                        break

                    replies = data.get('replies')
                    if not replies:
                        logger.info(f"第 {page} 页没有评论，停止爬取")
                        break

                    # 处理每条评论
                    for reply in replies:
                        formatted_time = timestamp_to_beijing_time(reply.get('ctime', 0))
                        reply_count = reply.get('rcount', 0)

                        comment = CommentData.from_api_response(
                            reply, formatted_time, reply_count
                        )

                        # 写入文件
                        self._write_comment_to_files(comment, output_paths)

                        # 处理二级评论
                        if reply_count > 0:
                            self._crawl_sub_comments(
                                oid, comment_type, comment.rpid,
                                reply_count, output_paths
                            )

                    logger.info(f"第 {page} 页处理完成")

                    # 延迟
                    self.api_client._sleep_random()

                except Exception as e:
                    logger.error(f"处理第 {page} 页时发生异常: {e}")
                    continue

            return True

        except Exception as e:
            logger.error(f"爬取主评论失败: {e}")
            return False

    def _crawl_sub_comments(self, oid: str, comment_type: CommentType,
                            root_rpid: str, total_count: int,
                            output_paths: Dict[str, str]):
        """爬取二级评论"""
        try:
            ps = self.config_manager.crawl_config.ps
            total_pages = math.ceil(total_count / ps)

            logger.info(f"开始爬取二级评论，根评论ID: {root_rpid}, 总数: {total_count}")

            for page in range(1, total_pages + 1):
                try:
                    data = self.api_client.get_reply_comments(
                        oid, comment_type, root_rpid, page
                    )

                    if not data:
                        continue

                    replies = data.get('replies')
                    if not replies:
                        continue

                    for reply in replies:
                        formatted_time = timestamp_to_beijing_time(reply.get('ctime', 0))

                        comment = CommentData.from_api_response(
                            reply, formatted_time, parent_rpid=root_rpid
                        )

                        # 写入文件（二级评论写入all_comments）
                        write_csv(
                            output_paths['all_comments'],
                            [comment.to_list()],
                            mode='a'
                        )

                    # 延迟
                    self.api_client._sleep_random()

                except Exception as e:
                    logger.error(f"处理二级评论第 {page} 页时发生异常: {e}")
                    continue

        except Exception as e:
            logger.error(f"爬取二级评论失败: {e}")

    def _write_comment_to_files(self, comment: CommentData,
                                output_paths: Dict[str, str]):
        """将评论写入文件"""
        try:
            # 写入总评论文件
            write_csv(
                output_paths['all_comments'],
                [comment.to_list()],
                mode='a'
            )

        except Exception as e:
            logger.error(f"写入评论文件失败: {e}")


class ProgressTracker:
    """进度跟踪器"""

    def __init__(self, progress_file: str = '记录.txt'):
        """
        初始化进度跟踪器
        
        Args:
            progress_file: 进度文件路径
        """
        self.progress_file = progress_file

    def record_completed_task(self, task: CrawlTask):
        """记录已完成的任务"""
        try:
            content = f"爬取了{task.oid}{'视频' if task.comment_type == CommentType.VIDEO else '动态'}，类型：{task.comment_type.value}\n"

            with open(self.progress_file, 'a', encoding='utf-8') as f:
                f.write(content)

        except Exception as e:
            logger.error(f"记录进度失败: {e}")
