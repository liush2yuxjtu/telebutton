# Telebutton API 详细文档

## 核心类

### ButtonMenu

按钮菜单配置类。

```python
@dataclass
class ButtonMenu:
    question: str                    # 显示的问题/标题
    options: List[ButtonOption]      # 选项列表
    max_per_row: int = 2             # 每行最多按钮数
    menu_id: str                     # 自动生成的唯一ID
```

#### 方法

**`to_dict() -> Dict`**
将菜单转换为字典格式，便于序列化。

**`from_dict(data: Dict) -> ButtonMenu`**
从字典创建菜单实例（类方法）。

**`find_option(callback: str) -> Optional[ButtonOption]`**
根据 callback 标识查找选项。

**`get_all_callbacks() -> List[str]`**
获取菜单中所有 callback 标识（包括嵌套子菜单）。

---

### ButtonOption

单个按钮选项。

```python
@dataclass
class ButtonOption:
    text: str                        # 按钮显示文字
    callback: str                    # 回调标识（唯一）
    sub_menu: Optional[ButtonMenu]   # 子菜单（可选）
```

---

## 核心函数

### show_menu

```python
def show_menu(
    menu: ButtonMenu,
    chat_id: Optional[str] = None,
    use_openclaw: bool = True
) -> Optional[str]
```

发送按钮菜单到 Telegram。

**参数：**
- `menu`: ButtonMenu 实例
- `chat_id`: 目标聊天 ID（默认当前会话）
- `use_openclaw`: 是否使用 OpenClaw 消息工具

**返回：**
- `message_id`: 发送的消息 ID
- `None`: 发送失败

**示例：**
```python
from telebutton import ButtonMenu, ButtonOption, show_menu

menu = ButtonMenu(
    question="请选择：",
    options=[
        ButtonOption(text="选项1", callback="opt1"),
        ButtonOption(text="选项2", callback="opt2")
    ]
)

msg_id = show_menu(menu)
```

---

### wait_selection

```python
def wait_selection(
    menu_id: Optional[str] = None,
    timeout: int = 300,
    delete_message: bool = True
) -> Optional[Dict]
```

等待用户选择。

**参数：**
- `menu_id`: 要监听的菜单 ID（None 表示监听任何菜单）
- `timeout`: 超时时间（秒），默认 300
- `delete_message`: 选择后是否删除原消息

**返回：**
```python
{
    "callback": str,       # 选中的回调标识
    "text": str,           # 选中的按钮文字
    "path": List[str],     # 选择路径（如 ["remote", "hpc_01"]）
    "menu_id": str,        # 菜单 ID
    "sub_menu": ButtonMenu # 子菜单（如果有）
}
```

或 `None`（超时或错误）。

**示例：**
```python
result = wait_selection(timeout=60)

if result:
    print(f"用户选择了: {result['text']}")
    print(f"回调标识: {result['callback']}")
else:
    print("选择超时")
```

---

### show_confirm / ask

```python
def show_confirm(
    question: str,
    yes_text: str = "✅ 是",
    no_text: str = "❌ 否",
    **kwargs
) -> Optional[Dict]
```

快速显示确认对话框。

**参数：**
- `question`: 确认问题文字
- `yes_text`: 确认按钮文字
- `no_text`: 取消按钮文字
- `**kwargs`: 传递给 `show_menu` 的其他参数

**返回：**
- `callback` 为 `"yes"` 或 `"no"`

**示例：**
```python
from telebutton import show_confirm, ask

# 两种方式等价
result = show_confirm("确定删除？")
result = ask("确定删除？")

if result and result['callback'] == 'yes':
    print("用户确认")
```

---

### load_menu_from_file

```python
def load_menu_from_file(filepath: str) -> ButtonMenu
```

从 YAML 或 JSON 文件加载菜单配置。

**支持格式：**
- `.yaml`, `.yml`: YAML 格式
- `.json`: JSON 格式

**示例：**
```python
# 从 YAML 加载
menu = load_menu_from_file("config/menu.yaml")

# 从 JSON 加载
menu = load_menu_from_file("config/menu.json")
```

---

### save_menu_to_file

```python
def save_menu_to_file(menu: ButtonMenu, filepath: str)
```

保存菜单配置到文件。

**示例：**
```python
menu = ButtonMenu(question="Test", options=[...])
save_menu_to_file(menu, "config/menu.yaml")
```

---

### handle_callback

```python
def handle_callback(callback_data: str) -> Optional[Dict]
```

处理 Telegram 回调数据。

**参数：**
- `callback_data`: Telegram callback_query data，格式为 `menu_id:callback`

**返回：**
解析后的选择信息，或 `None`（无效回调）

**示例：**
```python
# 在 webhook 处理器中使用
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    
    if 'callback_query' in data:
        callback_data = data['callback_query']['data']
        result = handle_callback(callback_data)
        
        if result:
            print(f"用户选择: {result['text']}")
```

---

## 配置函数

### clear_menu

```python
def clear_menu(menu_id: str)
```

清理指定菜单的注册信息。

---

### clear_all_menus

```python
def clear_all_menus()
```

清理所有菜单注册信息。

---

## 别名

以下别名可用：

| 别名 | 原函数 |
|------|--------|
| `ask` | `show_confirm` |
| `select` | `wait_selection` |

**示例：**
```python
from telebutton import ask, select

# 使用别名
if ask("确定？"):
    result = select()
```

---

## 错误处理

### 可能的异常

| 异常 | 描述 | 处理建议 |
|------|------|----------|
| `FileNotFoundError` | 配置文件不存在 | 检查文件路径 |
| `ValueError` | 缺少环境变量 | 设置 TELEGRAM_BOT_TOKEN |
| `TimeoutError` | 等待超时 | 增加 timeout 参数或处理超时 |
| `KeyError` | 无效回调数据 | 验证 callback 数据格式 |

**示例：**
```python
from telebutton import load_menu_from_file

try:
    menu = load_menu_from_file("config/menu.yaml")
except FileNotFoundError:
    print("配置文件不存在，使用默认配置")
    menu = create_default_menu()
```

---

## 高级配置

### 环境变量

| 变量名 | 说明 | 必需 |
|--------|------|------|
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token | 直接调用 API 时 |
| `TELEGRAM_CHAT_ID` | 默认聊天 ID | 可选 |

### 按钮限制

- 每行最多 8 个按钮（Telegram 限制）
- 建议每行 2-3 个按钮，便于点击
- 按钮文字建议不超过 20 个字符
- callback_data 长度不能超过 64 字节

---

## 回调数据结构

### Telegram CallbackQuery 格式

```json
{
  "update_id": 123456789,
  "callback_query": {
    "id": "1234567890123456789",
    "from": {
      "id": 123456789,
      "is_bot": false,
      "first_name": "User"
    },
    "message": {
      "message_id": 123,
      "chat": {
        "id": -1001234567890,
        "type": "supergroup"
      },
      "text": "请选择："
    },
    "data": "menu_id:callback_id"
  }
}
```

### handle_callback 返回格式

```python
{
    "callback": "callback_id",      # 回调标识
    "text": "显示文字",              # 按钮文字
    "menu_id": "menu_id",           # 菜单 ID
    "path": ["callback_id"],        # 选择路径
    "sub_menu": ButtonMenu          # 子菜单（如果有）
}
```
