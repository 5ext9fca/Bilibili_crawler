"""
数据分析器基类和工具函数
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Any, Optional
from pathlib import Path
import numpy as np
from utils.file_utils import setup_logger

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

logger = setup_logger(__name__)


class CommentDataAnalyzer:
    """评论数据分析器"""
    
    def __init__(self, data_file: str = 'data.csv'):
        """
        初始化分析器
        
        Args:
            data_file: 数据文件路径
        """
        self.data_file = data_file
        self.data = None
        self.output_dir = Path('analysis_output')
        self.output_dir.mkdir(exist_ok=True)
        
    def load_data(self) -> bool:
        """
        加载数据
        
        Returns:
            bool: 是否加载成功
        """
        try:
            if not Path(self.data_file).exists():
                logger.error(f"数据文件不存在: {self.data_file}")
                return False
            
            self.data = pd.read_csv(self.data_file)
            logger.info(f"成功加载数据，共 {len(self.data)} 条记录")
            logger.info(f"数据列: {list(self.data.columns)}")
            
            # 显示前几行数据
            logger.info("数据预览:")
            logger.info(str(self.data.head()))
            
            return True
            
        except Exception as e:
            logger.error(f"加载数据失败: {e}")
            return False
    
    def clean_data(self) -> bool:
        """
        清理数据
        
        Returns:
            bool: 是否清理成功
        """
        try:
            if self.data is None:
                logger.error("数据未加载")
                return False
            
            initial_rows = len(self.data)
            
            # 1. 删除uid列为空的行
            self.data = self.data.dropna(subset=['uid'])
            removed_rows = initial_rows - len(self.data)
            
            if removed_rows > 0:
                logger.info(f"删除了 {removed_rows} 行uid为空的数据")
            
            # 2. 清理时间列
            if '时间' in self.data.columns:
                self.data['时间'] = self.data['时间'].str.replace(' 北京时间', '', regex=False)
                self.data['时间'] = pd.to_datetime(self.data['时间'], errors='coerce')
                
                # 删除时间转换失败的行
                time_na_count = self.data['时间'].isna().sum()
                if time_na_count > 0:
                    logger.warning(f"发现 {time_na_count} 行时间格式错误，已删除")
                    self.data = self.data.dropna(subset=['时间'])
            
            # 3. 清理性别数据
            if '性别' in self.data.columns:
                self.data['性别'] = self.data['性别'].apply(
                    lambda x: x if x in ['男', '女'] else '保密'
                )
            
            # 4. 清理等级数据
            if '等级' in self.data.columns:
                valid_levels = [0, 1, 2, 3, 4, 5, 6]
                self.data = self.data[self.data['等级'].isin(valid_levels)]
            
            logger.info(f"数据清理完成，剩余 {len(self.data)} 条记录")
            return True
            
        except Exception as e:
            logger.error(f"数据清理失败: {e}")
            return False
    
    def analyze_nickname_frequency(self) -> bool:
        """分析昵称发言频次"""
        try:
            if '昵称' not in self.data.columns:
                logger.error("数据中缺少'昵称'列")
                return False
            
            nickname_counts = self.data['昵称'].value_counts().reset_index()
            nickname_counts.columns = ['昵称', '发言次数']
            
            output_file = self.output_dir / 'nickname_counts.csv'
            nickname_counts.to_csv(output_file, index=False, encoding='utf-8-sig')
            
            logger.info(f"昵称发言频次分析完成，结果保存至: {output_file}")
            logger.info(f"发言最多的前5位用户:")
            for _, row in nickname_counts.head().iterrows():
                logger.info(f"  {row['昵称']}: {row['发言次数']}次")
            
            return True
            
        except Exception as e:
            logger.error(f"昵称频次分析失败: {e}")
            return False
    
    def analyze_time_distribution(self) -> bool:
        """分析时间分布"""
        try:
            if '时间' not in self.data.columns:
                logger.error("数据中缺少'时间'列")
                return False
            
            # 按分钟统计
            time_counts_min = self.data['时间'].dt.floor('min').value_counts().sort_index()
            
            # 绘制分钟级分布图
            plt.figure(figsize=(40, 24))
            plt.plot(time_counts_min.index, time_counts_min.values, marker='o', label="发言人数")
            plt.title('不同时间下的发言人数 (按分钟)')
            plt.xlabel('时间 (按分钟)')
            plt.ylabel('发言人数')
            
            # 设置x轴间隔
            interval = min(30, len(time_counts_min) // 20)  # 自适应间隔
            if interval > 0:
                tick_positions = time_counts_min.index[::interval]
                plt.xticks(tick_positions, 
                          labels=[t.strftime('%Y-%m-%d %H:%M') for t in tick_positions], 
                          rotation=45)
            
            plt.tight_layout()
            min_output = self.output_dir / 'time_plot_min.png'
            plt.savefig(min_output, dpi=100, bbox_inches='tight')
            plt.close()
            
            # 按小时统计
            time_counts_hour = self.data['时间'].dt.floor('h').value_counts().sort_index()
            
            plt.figure(figsize=(12, 8))
            plt.plot(time_counts_hour.index, time_counts_hour.values, marker='o', label="发言人数")
            plt.title('不同时间下的发言人数 (按小时)')
            plt.xlabel('时间 (按小时)')
            plt.ylabel('发言人数')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            hour_output = self.output_dir / 'time_plot_hour.png'
            plt.savefig(hour_output, dpi=100, bbox_inches='tight')
            plt.close()
            
            logger.info(f"时间分布分析完成:")
            logger.info(f"  分钟级图表: {min_output}")
            logger.info(f"  小时级图表: {hour_output}")
            
            return True
            
        except Exception as e:
            logger.error(f"时间分布分析失败: {e}")
            return False
    
    def analyze_ip_location(self) -> bool:
        """分析IP属地分布"""
        try:
            if 'IP属地' not in self.data.columns:
                logger.error("数据中缺少'IP属地'列")
                return False
            
            # 统计前25名
            ip_counts = self.data['IP属地'].value_counts().head(25)
            
            plt.figure(figsize=(12, 10))
            ip_counts.plot.pie(
                autopct='%1.1f%%',
                startangle=90,
                labels=ip_counts.index,
                legend=False,
                cmap='viridis'
            )
            plt.title('IP属地发言次数分布 (前25名)')
            plt.ylabel('')  # 去掉默认的y轴标签
            
            output_file = self.output_dir / 'top_25_ip_pie_chart.png'
            plt.tight_layout()
            plt.savefig(output_file, dpi=100, bbox_inches='tight')
            plt.close()
            
            logger.info(f"IP属地分布分析完成，结果保存至: {output_file}")
            logger.info("发言最多的前5个地区:")
            for location, count in ip_counts.head().items():
                logger.info(f"  {location}: {count}次")
            
            return True
            
        except Exception as e:
            logger.error(f"IP属地分析失败: {e}")
            return False
    
    def analyze_level_distribution(self) -> bool:
        """分析等级分布"""
        try:
            if '等级' not in self.data.columns:
                logger.error("数据中缺少'等级'列")
                return False
            
            valid_levels = [0, 1, 2, 3, 4, 5, 6]
            level_data = self.data[self.data['等级'].isin(valid_levels)]
            level_counts = level_data['等级'].value_counts().sort_index()
            
            plt.figure(figsize=(10, 8))
            level_counts.plot.pie(
                autopct='%1.1f%%',
                startangle=90,
                labels=[f'LV{level}' for level in level_counts.index],
                legend=False,
                cmap='Set3'
            )
            plt.title('等级分布 (LV0-LV6)')
            plt.ylabel('')
            
            output_file = self.output_dir / 'level_pie_chart.png'
            plt.tight_layout()
            plt.savefig(output_file, dpi=100, bbox_inches='tight')
            plt.close()
            
            logger.info(f"等级分布分析完成，结果保存至: {output_file}")
            logger.info("各等级用户数量:")
            for level, count in level_counts.items():
                logger.info(f"  LV{level}: {count}人")
            
            return True
            
        except Exception as e:
            logger.error(f"等级分布分析失败: {e}")
            return False
    
    def analyze_gender_distribution(self) -> bool:
        """分析性别分布"""
        try:
            if '性别' not in self.data.columns:
                logger.error("数据中缺少'性别'列")
                return False
            
            gender_counts = self.data['性别'].value_counts()
            
            plt.figure(figsize=(8, 8))
            gender_counts.plot.pie(
                autopct='%1.1f%%',
                startangle=90,
                labels=gender_counts.index,
                legend=True
            )
            plt.title('性别分布')
            plt.ylabel('')
            
            output_file = self.output_dir / 'gender_pie_chart.png'
            plt.tight_layout()
            plt.savefig(output_file, dpi=100, bbox_inches='tight')
            plt.close()
            
            logger.info(f"性别分布分析完成，结果保存至: {output_file}")
            logger.info("性别分布:")
            for gender, count in gender_counts.items():
                logger.info(f"  {gender}: {count}人")
            
            return True
            
        except Exception as e:
            logger.error(f"性别分布分析失败: {e}")
            return False
    
    def analyze_level_likes_relationship(self) -> bool:
        """分析等级与点赞数关系"""
        try:
            required_cols = ['等级', '点赞']
            for col in required_cols:
                if col not in self.data.columns:
                    logger.error(f"数据中缺少'{col}'列")
                    return False
            
            valid_levels = [0, 1, 2, 3, 4, 5, 6]
            filtered_data = self.data[self.data['等级'].isin(valid_levels)]
            
            # 计算平均点赞数
            heatmap_data = filtered_data.groupby('等级')['点赞'].mean().reset_index()
            heatmap_pivot = heatmap_data.pivot_table(index='等级', values='点赞')
            
            plt.figure(figsize=(10, 8))
            sns.heatmap(
                heatmap_pivot,
                annot=True,
                fmt=".1f",
                cmap="YlGnBu",
                cbar_kws={'label': '平均点赞数'}
            )
            plt.title('等级与点赞数关系的热力图')
            plt.xlabel('平均点赞数')
            plt.ylabel('等级')
            
            output_file = self.output_dir / 'level_likes_heatmap.png'
            plt.tight_layout()
            plt.savefig(output_file, dpi=100, bbox_inches='tight')
            plt.close()
            
            logger.info(f"等级-点赞关系分析完成，结果保存至: {output_file}")
            logger.info("各等级平均点赞数:")
            for _, row in heatmap_data.iterrows():
                logger.info(f"  LV{int(row['等级'])}: {row['点赞']:.1f}")
            
            return True
            
        except Exception as e:
            logger.error(f"等级-点赞关系分析失败: {e}")
            return False
    
    def run_full_analysis(self) -> bool:
        """运行完整的数据分析"""
        try:
            logger.info("开始完整数据分析流程")
            
            # 1. 加载数据
            if not self.load_data():
                return False
            
            # 2. 清理数据
            if not self.clean_data():
                return False
            
            # 3. 运行各项分析
            analyses = [
                ("昵称频次分析", self.analyze_nickname_frequency),
                ("时间分布分析", self.analyze_time_distribution),
                ("IP属地分析", self.analyze_ip_location),
                ("等级分布分析", self.analyze_level_distribution),
                ("性别分布分析", self.analyze_gender_distribution),
                ("等级-点赞关系分析", self.analyze_level_likes_relationship),
            ]
            
            success_count = 0
            for name, func in analyses:
                try:
                    logger.info(f"执行{name}...")
                    if func():
                        success_count += 1
                        logger.info(f"{name}完成")
                    else:
                        logger.error(f"{name}失败")
                except Exception as e:
                    logger.error(f"{name}异常: {e}")
            
            logger.info(f"数据分析完成，成功 {success_count}/{len(analyses)} 项")
            logger.info(f"分析结果保存在: {self.output_dir}")
            
            return success_count == len(analyses)
            
        except Exception as e:
            logger.error(f"完整分析流程失败: {e}")
            return False