#!/usr/bin/env python3
"""
重构后的数据分析脚本
使用面向对象设计，提供清晰的分析流程
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analyzers.comment_analyzer import CommentDataAnalyzer
from utils.file_utils import setup_logger

logger = setup_logger(__name__)


def main():
    """主函数"""
    try:
        logger.info("=" * 50)
        logger.info("Bilibili评论数据分析器启动")
        logger.info("=" * 50)
        
        # 获取数据文件路径
        data_file = input("请输入数据文件路径 (直接回车使用默认 data.csv): ").strip()
        if not data_file:
            data_file = 'data.csv'
        
        logger.info(f"使用数据文件: {data_file}")
        
        # 创建分析器
        analyzer = CommentDataAnalyzer(data_file)
        
        # 询问分析类型
        print("\n请选择分析类型:")
        print("1. 完整分析 (推荐)")
        print("2. 昵称发言频次分析")
        print("3. 时间分布分析")
        print("4. IP属地分布分析")
        print("5. 等级分布分析")
        print("6. 性别分布分析")
        print("7. 等级-点赞关系分析")
        
        choice = input("请输入选项 (1-7): ").strip()
        
        # 加载和清理数据
        if not analyzer.load_data():
            logger.error("数据加载失败")
            return False
        
        if not analyzer.clean_data():
            logger.error("数据清理失败")
            return False
        
        # 执行分析
        success = False
        
        if choice == '1':
            # 完整分析
            success = analyzer.run_full_analysis()
        elif choice == '2':
            success = analyzer.analyze_nickname_frequency()
        elif choice == '3':
            success = analyzer.analyze_time_distribution()
        elif choice == '4':
            success = analyzer.analyze_ip_location()
        elif choice == '5':
            success = analyzer.analyze_level_distribution()
        elif choice == '6':
            success = analyzer.analyze_gender_distribution()
        elif choice == '7':
            success = analyzer.analyze_level_likes_relationship()
        else:
            logger.error("无效的选项")
            return False
        
        if success:
            logger.info("数据分析完成")
            logger.info("结果保存在 analysis_output/ 目录下")
            return True
        else:
            logger.error("数据分析失败")
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