#!/usr/bin/env python3
"""
重构后的BV/AV号转换工具
提供命令行和编程接口
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib.utils.video_utils import av2bv, bv2av, validate_av_format, validate_bv_format
from lib.utils.file_utils import setup_logger

logger = setup_logger(__name__)


def main():
    """主函数"""
    try:
        logger.info("=" * 50)
        logger.info("Bilibili BV/AV号转换工具")
        logger.info("=" * 50)
        
        while True:
            print("\n请选择操作:")
            print("1. AV号转BV号")
            print("2. BV号转AV号")
            print("3. 批量转换 (从文件)")
            print("4. 退出")
            
            choice = input("请输入选项 (1-4): ").strip()
            
            if choice == '1':
                handle_av_to_bv()
            elif choice == '2':
                handle_bv_to_av()
            elif choice == '3':
                handle_batch_convert()
            elif choice == '4':
                logger.info("程序退出")
                break
            else:
                print("无效选项，请重新输入")
    
    except KeyboardInterrupt:
        logger.info("用户中断程序")
    except Exception as e:
        logger.error(f"程序运行时发生异常: {e}")
    finally:
        logger.info("程序结束")


def handle_av_to_bv():
    """处理AV号转BV号"""
    try:
        av_input = input("请输入AV号 (可以带av前缀): ").strip()
        
        # 清理输入
        if av_input.lower().startswith('av'):
            av_input = av_input[2:]
        
        if not validate_av_format(av_input):
            print("AV号格式不正确，请输入正整数")
            return
        
        aid = int(av_input)
        bvid = av2bv(aid)
        
        print(f"转换结果:")
        print(f"  AV号: av{aid}")
        print(f"  BV号: {bvid}")
        
        logger.info(f"AV转BV: av{aid} -> {bvid}")
        
    except ValueError as e:
        print(f"转换失败: {e}")
    except Exception as e:
        logger.error(f"AV转BV失败: {e}")


def handle_bv_to_av():
    """处理BV号转AV号"""
    bv_input = input("请输入BV号: ").strip()
    if not validate_bv_format(bv_input):
        print("BV号格式不正确")
        return
    try:
        aid = bv2av(bv_input)
    except ValueError as e:
        print(f"转换失败: {e}")
    except Exception as e:
        logger.error(f"BV转AV失败: {e}")

        print(f"转换结果:")
        print(f"  BV号: {bv_input}")
        print(f"  AV号: av{aid}")

        logger.info(f"BV转AV: {bv_input} -> av{aid}")

def handle_batch_convert():
    """处理批量转换"""
    try:
        file_path = input("请输入包含视频ID的文件路径: ").strip()
        
        if not os.path.exists(file_path):
            print("文件不存在")
            return
        
        output_file = input("请输入输出文件路径 (回车使用默认): ").strip()
        if not output_file:
            output_file = "converted_ids.txt"
        
        print("正在处理...")
        
        success_count = 0
        total_count = 0
        
        with open(file_path, 'r', encoding='utf-8') as f:
            with open(output_file, 'w', encoding='utf-8') as out_f:
                out_f.write("原ID\t转换后ID\t类型\n")
                
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    total_count += 1
                    
                    try:
                        if line.lower().startswith('av'):
                            # AV转BV
                            av_num = line[2:]
                            if validate_av_format(av_num):
                                bvid = av2bv(int(av_num))
                                out_f.write(f"{line}\t{bvid}\tAV->BV\n")
                                success_count += 1
                            else:
                                out_f.write(f"{line}\t转换失败\t格式错误\n")
                        
                        elif line.upper().startswith('BV'):
                            # BV转AV
                            if validate_bv_format(line):
                                aid = bv2av(line)
                                out_f.write(f"{line}\tav{aid}\tBV->AV\n")
                                success_count += 1
                            else:
                                out_f.write(f"{line}\t转换失败\t格式错误\n")
                        
                        else:
                            # 尝试判断是否为纯数字（AV号）
                            if validate_av_format(line):
                                bvid = av2bv(int(line))
                                out_f.write(f"av{line}\t{bvid}\tAV->BV\n")
                                success_count += 1
                            else:
                                out_f.write(f"{line}\t转换失败\t未知格式\n")
                                
                    except Exception as e:
                        out_f.write(f"{line}\t转换失败\t{str(e)}\n")
        
        print(f"批量转换完成!")
        print(f"  处理总数: {total_count}")
        print(f"  成功转换: {success_count}")
        print(f"  结果保存至: {output_file}")
        
        logger.info(f"批量转换: {success_count}/{total_count} 成功")
        
    except Exception as e:
        logger.error(f"批量转换失败: {e}")


if __name__ == '__main__':
    main()