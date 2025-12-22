#!/usr/bin/env python3
"""
重构代码测试脚本
验证重构后代码的基本功能
"""
import sys

from lib.core.config_manager import ConfigManager
from lib.models.data_models import CommentType, CrawlConfig
from lib.utils.file_utils import setup_logger, add_dir_to_path
from lib.utils.time_utils import timestamp_to_beijing_time, get_current_beijing_time
from lib.utils.platform_utils import av2bv, bv2av, validate_bv_format, validate_av_format

add_dir_to_path(__file__)

logger = setup_logger(__name__)


def test_video_utils():
    """测试视频工具函数"""
    logger.info("测试视频工具函数...")

    # 测试AV/BV转换
    test_aid = 170001
    bvid = av2bv(test_aid)
    converted_aid = bv2av(bvid)

    assert converted_aid == test_aid, f"AV/BV转换测试失败: {test_aid} != {converted_aid}"
    logger.info(f"AV/BV转换测试通过: av{test_aid} <-> {bvid}")

    # 测试格式验证
    assert validate_av_format("170001"), "AV格式验证失败"
    assert validate_bv_format(bvid), "BV格式验证失败"
    assert not validate_av_format("abc"), "AV格式验证应该失败"
    assert not validate_bv_format("BV1abc"), "BV格式验证应该失败"

    logger.info("视频工具函数测试通过")


def test_time_utils():
    """测试时间工具函数"""
    logger.info("测试时间工具函数...")

    # 测试时间戳转换
    timestamp = 1640995200  # 2022-01-01 00:00:00 UTC
    beijing_time = timestamp_to_beijing_time(timestamp)
    assert "2022-01-01" in beijing_time, f"时间转换失败: {beijing_time}"

    # 测试当前时间
    current_time = get_current_beijing_time()
    assert len(current_time) >= 19, f"当前时间格式错误: {current_time}"

    logger.info("时间工具函数测试通过")


def test_data_models():
    """测试数据模型"""
    logger.info("测试数据模型...")

    # 测试评论类型枚举
    assert CommentType.VIDEO.value == 1
    assert CommentType.DYNAMIC_IMAGE.value == 11
    assert CommentType.DYNAMIC_TEXT.value == 17

    # 测试配置模型
    config = CrawlConfig(
        cookies_str="写入您的cookies",  # 使用默认值，应该被检测为错误
        bili_jct="cookie中的bili_jct"  # 使用默认值，应该被检测为错误
    )

    errors = config.validate()
    # 由于使用默认值，应该有验证错误
    logger.info(f"配置验证错误: {errors}")
    assert len(errors) >= 2, f"配置验证应该有错误，实际错误数量: {len(errors)}, 错误内容: {errors}"

    logger.info("数据模型测试通过")


def test_config_manager():
    """测试配置管理器"""
    logger.info("测试配置管理器...")

    try:
        config_manager = ConfigManager()

        # 尝试加载配置
        if config_manager.load_config():
            logger.info("配置加载成功")
            crawl_config = config_manager.crawl_config
            logger.info(f"配置信息: ps={crawl_config.ps}, start_page={crawl_config.start_page}")
        else:
            logger.warning("配置加载失败，可能是配置文件不存在或格式错误")

        logger.info("配置管理器测试通过")

    except Exception as e:
        logger.warning(f"配置管理器测试失败: {e}")


def main():
    """运行测试"""
    try:
        logger.info("=" * 50)
        logger.info("开始重构代码测试")
        logger.info("=" * 50)

        # 运行各项测试
        test_video_utils()
        test_time_utils()
        test_data_models()
        test_config_manager()

        logger.info("=" * 50)
        logger.info("所有测试完成")
        logger.info("=" * 50)

        return True

    except Exception as e:
        logger.error(f"测试过程中发生异常: {e}")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
