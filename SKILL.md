---
name: telebutton
description: |
  Telegram 选择按钮交互 Skill。用于在 Telegram 对话中向用户展示选择按钮（InlineKeyboard），获取用户反馈。
  
  使用场景：
  - 需要用户从多个选项中选择
  - 多轮嵌套菜单（选择后显示子菜单）
  - 简单的确认/取消交互
  - 工作流分支选择（如 HPC 任务提交方式选择）
  
  核心特点：
  - 配置驱动：通过 YAML/JSON 定义按钮结构，无需修改代码
  - 支持嵌套：多级菜单，选择后自动展开子选项
  - 临时状态：无需持久化存储，适合快速交互
  - 通用接口：与具体执行逻辑解耦，Agent 自行处理选择结果
---

# Telebutton - Telegram 选择按钮 Skill

## 快速开始

### 1. 基础用法

```python
from telebutton import ButtonMenu, show_menu, wait_selection

# 定义菜单
menu = ButtonMenu(
    question="选择执行方式：",
    options=[
        {"text": "本地运行", "callback": "local"},
        {"text": "远程服务器", "callback": "remote", "sub_menu": {
            "question": "选择服务器：",
            "options": [
                {"text": "HPC-01", "callback": "hpc_01"},
                {"text": "HPC-02", "callback": "hpc_02"}
            ]
        }}
    ]
)

# 发送按钮
message_id = show_menu(menu)

# 等待用户选择（阻塞式）
result = wait_selection(timeout=300)  # 5分钟超时

print(f"用户选择了: {result['callback']}")
# 输出: 用户选择了: hpc_01
```

### 2. 配置文件方式

```python
from telebutton import load_menu_from_file, show_menu, wait_selection

# 从 YAML 加载
menu = load_menu_from_file("config/hpc_menu.yaml")
show_menu(menu)
result = wait_selection()
```

**config/hpc_menu.yaml:**
```yaml
question: "选择执行方式："
options:
  - text: "本地运行"
    callback: "local"
  - text: "远程服务器"
    callback: "remote"
    sub_menu:
      question: "选择服务器："
      options:
        - text: "HPC-01"
          callback: "hpc_01"
        - text: "HPC-02"
          callback: "hpc_02"
        - text: "返回"
          callback: "back"
```

## API 参考

### ButtonMenu 类

主菜单配置类。

```python
ButtonMenu(
    question: str,                    # 显示的问题/标题
    options: List[ButtonOption],       # 选项列表
    max_per_row: int = 2               # 每行最多按钮数
)
```

### ButtonOption 结构

```python
{
    "text": str,                      # 按钮显示文字
    "callback": str,                  # 回调标识（唯一）
    "sub_menu": Optional[ButtonMenu]  # 子菜单（可选）
}
```

### 核心函数

#### show_menu(menu, chat_id=None)
发送按钮菜单到 Telegram。

- `menu`: ButtonMenu 实例
- `chat_id`: 目标聊天 ID（默认当前会话）
- 返回: message_id

#### wait_selection(timeout=300, delete_message=True)
等待用户选择。

- `timeout`: 超时时间（秒）
- `delete_message`: 选择后是否删除原消息
- 返回: `{"callback": str, "text": str, "path": List[str]}`
  - `callback`: 选中的回调标识
  - `text`: 选中的按钮文字
  - `path`: 选择路径（如 `["remote", "hpc_01"]`）

#### show_confirm(question, yes_text="是", no_text="否")
快速显示确认对话框。

```python
from telebutton import show_confirm

result = show_confirm("确定要删除吗？")
if result['callback'] == 'yes':
    print("用户确认")
```

## 高级用法

### 动态生成选项

```python
from telebutton import ButtonMenu, show_menu, wait_selection

# 从外部数据动态生成
servers = ["hpc-01", "hpc-02", "hpc-03"]

menu = ButtonMenu(
    question="选择服务器：",
    options=[
        {"text": s.upper(), "callback": s} 
        for s in servers
    ],
    max_per_row=3
)

show_menu(menu)
result = wait_selection()
```

### 处理多级选择

```python
result = wait_selection()

# 根据选择路径判断
if result['path'] == ['remote', 'hpc_01']:
    # 用户选择了：远程服务器 -> HPC-01
    execute_on_hpc_01()
elif result['callback'] == 'local':
    # 用户选择了：本地运行
    execute_locally()
```

### 自定义按钮样式

```python
from telebutton import ButtonOption

options = [
    ButtonOption(text="✅ 确认", callback="confirm"),
    ButtonOption(text="❌ 取消", callback="cancel"),
    ButtonOption(text="🔙 返回", callback="back"),
]
```

## 完整示例

### HPC 任务提交

```python
from telebutton import ButtonMenu, show_menu, wait_selection

def submit_hpc_job():
    # 主菜单
    main_menu = ButtonMenu(
        question="🖥️ HPC 任务提交",
        options=[
            {
                "text": "🚀 快速提交",
                "callback": "quick",
                "sub_menu": {
                    "question": "选择队列：",
                    "options": [
                        {"text": "GPU (A100)", "callback": "gpu_a100"},
                        {"text": "GPU (3090)", "callback": "gpu_3090"},
                        {"text": "CPU", "callback": "cpu"}
                    ]
                }
            },
            {
                "text": "⚙️ 高级配置",
                "callback": "advanced"
            },
            {
                "text": "📊 查看状态",
                "callback": "status"
            }
        ]
    )
    
    show_menu(main_menu)
    result = wait_selection()
    
    # 处理选择
    if result['callback'] == 'gpu_a100':
        print("提交到 A100 队列...")
    elif result['callback'] == 'advanced':
        print("打开高级配置...")
    # ...
```

## 注意事项

1. **超时处理**: `wait_selection()` 默认 5 分钟超时，超时后返回 `None`
2. **并发**: 同一聊天中同时只能有一个活跃的选择等待
3. **回调唯一性**: 同一菜单层级中，callback 标识必须唯一
4. **嵌套深度**: 建议不超过 3 层嵌套，避免用户迷失

## 依赖

- Python >= 3.8
- OpenClaw 消息工具（用于发送按钮和接收回调）

## 参考

- 更多示例: [references/examples.md](references/examples.md)
- API 详细文档: [references/api.md](references/api.md)
