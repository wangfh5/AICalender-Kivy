# AI Calendar Assistant

一个基于人工智能的日历助手，可以从自然语言描述中提取事件信息并生成标准的日历文件。

## 功能特点

- 支持中英文自然语言输入
- 智能识别事件时间、地点、参与者等信息
- 自动处理各种时间表达方式（如"明天"、"下周一"、"五一节前一天"等）
- 生成标准的 .ics 日历文件，可导入到各种日历软件
- 支持设置提醒时间
- 完善的错误处理和日志记录

## 项目结构

```
.
├── src/
│   ├── nlp/
│   │   └── text_parser.py    # 自然语言解析模块
│   └── calendar/
│       └── ics_generator.py  # 日历文件生成模块
├── tests/
│   └── test_parser.py        # 测试用例
├── examples/
│   └── basic_usage.py        # 基本使用示例
└── README.md
```

## 安装

1. 创建并激活虚拟环境：

```bash
conda create -n aicalendar python=3.8
conda activate aicalendar
```

2. 安装依赖：

```bash
pip install openai pytz icalendar
```

3. 准备 API Key：
   您需要准备一个 Deepseek API Key。程序运行时会提示您输入。

## 使用方法

### 命令行交互（推荐）

直接运行主程序：
```bash
python src/main.py
```

程序会引导您：
1. 输入 Deepseek API Key（输入时不会显示在屏幕上）
2. 输入日程安排，支持以下方式：
   - 每个日程可以包含多行文本
   - 使用 `---` 或 `===` 分隔不同的日程
   - 使用以下方式之一结束输入：
     - 输入 `done` 或 `exit`
     - 连续两次回车
     - Ctrl+C 或 Ctrl+D

示例输入：
```
明天下午2点开产品评审会
需要讨论新功能的设计方案
和产品部一起评估开发工作量
---
Prof. Smith's seminar on Quantum Computing
Abstract: This talk introduces recent developments in quantum error correction.
We will discuss the surface code and its implementation.
Join via Zoom: https://zoom.us/j/123456, Passcode: qc2024
---
下周一上午10点到11点半在3楼会议室开项目进展会
done
```

程序会处理每个日程并生成 `my_calendar.ics` 文件。

### 代码调用

如果需要在代码中调用，可以参考以下示例：
```python
from src.nlp.text_parser import TextParser
from src.calendar.ics_generator import ICSGenerator

# 初始化解析器和生成器
parser = TextParser(api_key="YOUR_API_KEY")
generator = ICSGenerator()

# 解析文本
text = "明天下午2点开产品评审会"
event = parser.parse_to_event_data(text)

# 添加到日历
generator.add_event(event)

# 保存日历文件
generator.save("my_calendar.ics")
```

### 支持的输入格式

1. 基本会议：
```
明天下午2点开产品评审会
```

2. 带地点和时间范围的会议：
```
下周一上午10点到11点半在3楼会议室开项目进展会
```

3. 带参与者和提醒的会议：
```
后天下午3点和张总(zhang@example.com)、李经理(li@example.com)开预算会议，提前30分钟提醒
```

4. 学术讲座：
```
Prof. Smith's seminar on Quantum Computing
Abstract: This talk introduces recent developments in quantum error correction.
We will discuss the surface code and its implementation.
Join via Zoom: https://zoom.us/j/123456, Passcode: qc2024
```

### 高级特性

1. 智能默认值：
- 如果未指定结束时间，默认会议时长为1小时
- 如果未指定提醒时间，默认提前15分钟提醒
- 对于重要会议（如面试、演讲），默认提前30分钟提醒

2. 错误处理：
- 输入验证和错误提示
- 自动重试机制
- 详细的日志记录

## 测试

运行测试套件：

```bash
python -m unittest tests/test_parser.py -v
```

## 注意事项

1. 时区设置：默认使用 Asia/Shanghai 时区
2. API 限制：请注意 API 的调用频率限制
3. 日历文件：生成的 .ics 文件可以导入到 Google Calendar、Apple Calendar 等主流日历软件

## 许可证

MIT License
