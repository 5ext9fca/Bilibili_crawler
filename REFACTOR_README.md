# Bilibili爬虫重构版 - 架构文档

## 📁 项目结构

重构后的项目采用模块化设计，提高了代码的可读性和可维护性：

```
Bilibili_crawler-main/
├── core/                              # 核心业务逻辑
│   ├── __init__.py
│   ├── config_manager.py              # 配置管理器
│   ├── api_client.py                  # B站API客户端
│   └── crawler.py                     # 爬虫核心类
├── utils/                             # 工具函数
│   ├── __init__.py
│   ├── video_utils.py                 # 视频相关工具（BV/AV转换等）
│   ├── time_utils.py                  # 时间处理工具
│   └── file_utils.py                  # 文件操作工具
├── models/                            # 数据模型
│   ├── __init__.py
│   └── data_models.py                 # 数据模型定义
├── analyzers/                         # 数据分析模块
│   ├── __init__.py
│   └── comment_analyzer.py            # 评论数据分析器
├── Bilibili_crawler_refactored.py     # 重构后的批量爬虫
├── simple_bili_crawler_refactored.py  # 重构后的单目标爬虫
├── bili_user_space_refactored.py      # 重构后的用户空间爬虫
├── common_func_refactored.py          # 重构后的数据分析脚本
├── bv2oid_refactored.py              # 重构后的BV/AV转换工具
├── config.json                        # 配置文件
├── comments/                          # 评论数据输出目录
├── user/                             # 用户动态列表目录
└── analysis_output/                   # 数据分析结果目录
```

## 🎯 重构亮点

### 1. 面向对象设计

- **职责分离**：每个类都有明确的职责
- **配置管理**：`ConfigManager`统一管理所有配置
- **API客户端**：`BilibiliApiClient`封装所有API调用
- **爬虫核心**：`BilibiliCrawler`处理业务逻辑

### 2. 模块化架构

- **utils模块**：通用工具函数，提高代码复用
- **models模块**：数据模型定义，类型安全
- **core模块**：核心业务逻辑，功能集中
- **analyzers模块**：数据分析功能，独立模块

### 3. 错误处理与日志

- **统一日志**：所有模块使用统一的日志系统
- **异常处理**：完善的错误处理和恢复机制
- **进度跟踪**：详细的爬取进度记录

### 4. 配置验证

- **参数校验**：配置文件参数自动验证
- **错误提示**：清晰的配置错误提示
- **默认值**：合理的默认配置

## 🚀 使用方法

### 环境准备

1. 安装依赖：

```bash
pip install -r requirements.txt
```

2. 配置文件：编辑 `config.json`

```json
{
  "cookies_str": "你的cookies",
  "bili_jct": "你的bili_jct",
  "ps": "20",
  "start": 1,
  "end": 99999
}
```

### 脚本使用

#### 1. 批量爬取评论

```bash
python Bilibili_crawler.py
```

- 读取 `user/` 目录下的CSV任务文件
- 批量爬取所有任务的评论
- 输出到 `comments/` 目录

#### 2. 单个目标爬取

```bash
python simple_crawler.py
```

需要在 `config.json` 中配置：

```json
{
  "oid": "目标ID",
  "type": 1,
  "down": 1,
  "up": 100
}
```

#### 3. 用户空间动态获取

```bash
python bili_user_space.py
```

- 交互式输入用户UID
- 获取该用户所有动态列表
- 保存到 `user/{uid}.csv`

#### 4. 数据分析

```bash
python common_func.py
```

- 支持多种分析类型
- 结果保存到 `analysis_output/` 目录
- 包含图表和统计数据

#### 5. BV/AV号转换

```bash
python bv2oid.py
```

- 支持单个转换和批量转换
- 支持双向转换（AV↔BV）
- 格式验证和错误处理

## 🔧 核心类介绍

### ConfigManager

```python
# 配置管理器
config_manager = ConfigManager()
config_manager.load_config()
crawl_config = config_manager.crawl_config
```

### BilibiliApiClient

```python
# API客户端
api_client = BilibiliApiClient(config)
data = api_client.get_main_comments(oid, comment_type, page)
```

### BilibiliCrawler

```python
# 爬虫核心
crawler = BilibiliCrawler(config_manager)
success = crawler.crawl_single_target(oid, comment_type)
```

### CommentDataAnalyzer

```python
# 数据分析器
analyzer = CommentDataAnalyzer('data.csv')
analyzer.run_full_analysis()
```

## 📊 数据模型

### CommentData

评论数据模型，包含：

- 基础信息：昵称、性别、时间、点赞、内容
- 用户信息：等级、UID、IP属地
- 结构信息：回复ID、父评论ID、是否置顶

### CrawlTask

爬取任务模型：

- 目标ID（oid）
- 评论类型（视频/动态）
- 可选标题

### CrawlConfig

爬取配置模型：

- Cookie和认证信息
- 分页参数
- 延迟和重试设置

## 🛡️ 错误处理

1. **网络错误**：自动重试机制
2. **配置错误**：详细的验证和提示
3. **数据错误**：格式验证和清理
4. **文件错误**：目录自动创建和权限检查

## 📈 性能优化

1. **请求优化**：会话复用、连接池
2. **内存优化**：流式处理、及时清理
3. **并发控制**：合理延迟、避免封禁
4. **缓存机制**：配置缓存、重复请求避免

## 🆚 与原版对比

| 特性   | 原版           | 重构版       |
|------|--------------|-----------|
| 代码组织 | 面向过程，重复代码多   | 面向对象，模块化  |
| 错误处理 | 基础的try-catch | 完善的异常处理体系 |
| 配置管理 | 硬编码，分散       | 统一配置管理    |
| 日志记录 | print输出      | 结构化日志系统   |
| 数据验证 | 缺少验证         | 完整的数据验证   |
| 可扩展性 | 难以扩展         | 高度可扩展     |
| 代码复用 | 复制粘贴         | 工具函数复用    |
| 测试友好 | 难以测试         | 模块化便于测试   |

## 🔮 后续扩展

重构后的架构支持轻松扩展：

1. 新增其他B站数据类型的爬取
2. 支持更多数据分析算法
3. 添加数据库存储支持
4. 实现Web界面
5. 支持分布式爬取

## 📝 最佳实践

1. **使用重构版脚本**：功能更稳定，错误处理更完善
2. **配置验证**：启动前检查配置文件的完整性
3. **日志监控**：关注日志输出，及时发现问题
4. **数据备份**：定期备份爬取的数据
5. **遵守协议**：合理设置延迟，避免过度请求