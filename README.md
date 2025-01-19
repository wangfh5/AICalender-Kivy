# AI Calendar Assistant

一个基于人工智能的日历助手，可以从自然语言描述中提取事件信息并生成标准的日历文件。

> 本项目在 [Cursor](https://cursor.com/) 和 [WindSurf](https://windsurfai.org/) 的强大AI助手支持下完成。

## 功能特点

- 支持中英文自然语言输入
- 智能识别事件时间、地点、参与者等信息
- 自动处理各种时间表达方式（如"明天"、"下周一"、"五一节前一天"等）
- 生成标准的 .ics 日历文件，可导入到各种日历软件
- 支持设置提醒时间
- 完善的错误处理和日志记录
- 提供命令行、GUI 和 API 三种使用方式

## 项目结构

```
.
├── main.py               # GUI 界面入口
├── src/
│   ├── main.py          # 命令行界面入口
│   ├── nlp/
│   │   └── text_parser.py    # 自然语言解析模块
│   └── calendar/
│       └── ics_generator.py  # 日历文件生成模块
├── tests/
│   └── test_parser.py        # 测试用例
├── examples/
│   └── basic_usage.py        # API 调用示例
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
# 基础依赖
pip install openai pytz icalendar

# GUI 界面依赖
pip install kivy
```

3. 准备 API Key：
   您需要准备一个 [DeepSeek](https://platform.deepseek.com/) API Key。可以通过以下方式提供：
   - GUI 界面：在设置界面填入
   - 命令行：运行时会提示输入
   - API 调用：作为参数传入

## 使用方法

本项目提供三种使用方式：

### 1. GUI 界面（最友好但还很粗糙）

运行主程序：
```bash
python main.py
```

GUI 界面提供：
- 直观的事件输入界面
- API Key 设置
- 日历文件自动导出
- 实时反馈

### 2. 命令行交互（最轻量）

运行命令行版本：
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

### 3. API 调用（最灵活）

如果需要在自己的代码中调用，可以参考 `examples/basic_usage.py`：

1. 首先在代码中填入你的 [DeepSeek](https://platform.deepseek.com/) API Key：
```python
API_KEY = "sk-..." # 替换为你的 API Key
```

2. 然后运行示例：
```bash
python examples/basic_usage.py
```

或者在自己的代码中这样调用：
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

## 注意事项

1. 确保使用正确的 Python 版本（3.8）和虚拟环境
2. 保护好你的 API Key，不要将其提交到代码仓库
3. 生成的日历文件可以导入到 Google Calendar、Apple Calendar 等主流日历软件
4. 可以自行尝试使用 Buildozer 生成 Android 版本的日历助手 （我并没有尝试成功过）
