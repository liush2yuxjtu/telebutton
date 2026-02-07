# Telebutton 示例

## 示例 1: HPC 任务提交

```yaml
# hpc_submit.yaml
question: "🖥️ HPC 任务提交"
options:
  - text: "🚀 快速提交"
    callback: "quick"
    sub_menu:
      question: "选择队列："
      options:
        - text: "GPU A100"
          callback: "queue_a100"
        - text: "GPU 3090"
          callback: "queue_3090"
        - text: "CPU 集群"
          callback: "queue_cpu"
        - text: "🔙 返回"
          callback: "back"
  
  - text: "⚙️ 高级配置"
    callback: "advanced"
    sub_menu:
      question: "配置选项："
      options:
        - text: "设置 GPU 数"
          callback: "set_gpu"
        - text: "设置内存"
          callback: "set_memory"
        - text: "设置超时"
          callback: "set_timeout"
  
  - text: "📊 查看状态"
    callback: "status"
  
  - text: "❌ 取消"
    callback: "cancel"
```

使用代码：
```python
from telebutton import load_menu_from_file, show_menu, wait_selection

menu = load_menu_from_file("hpc_submit.yaml")
show_menu(menu)
result = wait_selection()

if result:
    if result['callback'] == 'queue_a100':
        print("提交到 A100 队列...")
    elif result['callback'] == 'status':
        print("查看任务状态...")
```

## 示例 2: 数据查询

```python
from telebutton import ButtonMenu, ButtonOption, show_menu, wait_selection

# 动态生成选项
datasets = ["MNIST", "CIFAR-10", "ImageNet", "Custom"]

menu = ButtonMenu(
    question="📊 选择要查看的数据集：",
    options=[
        ButtonOption(text=ds, callback=ds.lower().replace("-", "_"))
        for ds in datasets
    ],
    max_per_row=2
)

show_menu(menu)
result = wait_selection()

if result:
    print(f"用户选择了数据集: {result['text']}")
```

## 示例 3: 确认对话框

```python
from telebutton import show_confirm

# 简单确认
result = show_confirm("确定要删除这个文件吗？")
if result and result['callback'] == 'yes':
    delete_file()
else:
    print("操作已取消")

# 自定义按钮文字
result = show_confirm(
    "是否保存更改？",
    yes_text="💾 保存",
    no_text="🗑️ 放弃"
)
```

## 示例 4: 多级嵌套菜单

```python
from telebutton import ButtonMenu, ButtonOption, show_menu, wait_selection

# 三级嵌套菜单
menu = ButtonMenu(
    question="🏢 公司部门选择",
    options=[
        ButtonOption(
            text="👨‍💻 技术部",
            callback="tech",
            sub_menu=ButtonMenu(
                question="选择团队：",
                options=[
                    ButtonOption(
                        text="后端",
                        callback="backend",
                        sub_menu=ButtonMenu(
                            question="选择技术栈：",
                            options=[
                                ButtonOption(text="Python", callback="python"),
                                ButtonOption(text="Go", callback="go"),
                                ButtonOption(text="Java", callback="java")
                            ]
                        )
                    ),
                    ButtonOption(text="前端", callback="frontend"),
                    ButtonOption(text="运维", callback="devops")
                ]
            )
        ),
        ButtonOption(text="📈 产品部", callback="product"),
        ButtonOption(text="📢 市场部", callback="marketing")
    ]
)

show_menu(menu)
result = wait_selection()

# 处理多级路径
if result:
    print(f"选择路径: {' -> '.join(result['path'])}")
    # 输出示例: 选择路径: tech -> backend -> python
```

## 示例 5: 与 Agent 工作流集成

```python
from telebutton import ButtonMenu, ButtonOption, show_menu, wait_selection

def deploy_workflow():
    """部署工作流示例"""
    
    # 第一步：选择环境
    env_menu = ButtonMenu(
        question="🌍 选择部署环境：",
        options=[
            ButtonOption(text="🧪 测试环境", callback="staging"),
            ButtonOption(text="🚀 生产环境", callback="production")
        ]
    )
    
    show_menu(env_menu)
    env_result = wait_selection()
    
    if not env_result:
        print("⏱️ 选择超时")
        return
    
    env = env_result['callback']
    
    # 第二步：确认部署
    confirm = show_confirm(
        f"确定要部署到 **{env.upper()}** 环境吗？\n"
        f"此操作不可撤销！"
    )
    
    if confirm and confirm['callback'] == 'yes':
        print(f"🚀 开始部署到 {env}...")
        # 执行部署逻辑
    else:
        print("❌ 部署已取消")

# 运行
deploy_workflow()
```

## 示例 6: 错误处理和超时

```python
from telebutton import ButtonMenu, show_menu, wait_selection

def robust_selection():
    """健壮的选择处理"""
    
    menu = ButtonMenu(
        question="选择一个选项：",
        options=[
            {"text": "选项 A", "callback": "a"},
            {"text": "选项 B", "callback": "b"}
        ]
    )
    
    # 显示菜单
    msg_id = show_menu(menu)
    
    # 等待选择，60秒超时
    result = wait_selection(timeout=60)
    
    if result is None:
        print("⏱️ 用户未在规定时间内选择")
        # 可选：发送超时提醒
        return None
    
    print(f"✅ 用户选择了: {result['text']} ({result['callback']})")
    return result

# 带重试的选择
def select_with_retry(max_retries=3):
    for attempt in range(max_retries):
        result = robust_selection()
        if result:
            return result
        print(f"第 {attempt + 1} 次尝试失败，重试...")
    print("达到最大重试次数")
    return None
```

## 示例 7: 配置文件最佳实践

```yaml
# config/menus.yaml
# 将所有菜单配置集中管理

menus:
  hpc_submit:
    question: "🖥️ HPC 任务提交"
    max_per_row: 2
    options:
      - text: "快速提交"
        callback: "quick"
      - text: "高级配置"
        callback: "advanced"
  
  data_query:
    question: "📊 数据查询"
    max_per_row: 3
    options:
      - text: "今日数据"
        callback: "today"
      - text: "本周数据"
        callback: "week"
      - text: "自定义"
        callback: "custom"

# 加载使用
# menu = load_menu_from_file("config/menus.yaml")
```

---

## ❌ Bad Cases - 常见错误

### Bad Case 1: 应该使用按钮时却用文本回复

**场景**: 用户需要选择操作方式

**❌ 错误做法** - 纯文本列出选项：
```
用户: 把这个发布到 GitHub

Agent: 好的！两种方式：
方式 A（推荐）：给我你的 GitHub 用户名...
方式 B：手动创建...
选哪种？
```

**问题**:
- 用户需要手动输入选择（容易出错）
- 体验不够直观
- 无法处理复杂的多级选择

**✅ 正确做法** - 使用按钮：
```python
from telebutton import ButtonMenu, show_menu, wait_selection

menu = ButtonMenu(
    question="📤 发布到 GitHub",
    options=[
        {"text": "🚀 快速推送", "callback": "quick_push"},
        {"text": "🔧 手动配置", "callback": "manual"}
    ]
)

show_menu(menu)
result = wait_selection()

if result['callback'] == 'quick_push':
    # 执行快速推送
elif result['callback'] == 'manual':
    # 引导手动配置
```

**使用时机**: 当提供 2-6 个明确选项供用户选择时，优先使用按钮而非文本列举。

---

### Bad Case 2: 按钮选项过多导致界面混乱

**❌ 错误做法**:
```python
# 一行放太多按钮
menu = ButtonMenu(
    question="选择服务器：",
    options=[{"text": f"HPC-{i}", "callback": f"hpc_{i}"} for i in range(10)],
    max_per_row=5  # ❌ 一行5个，按钮太小难点击
)
```

**✅ 正确做法**:
```python
# 分组或使用分页
menu = ButtonMenu(
    question="选择服务器集群：",
    options=[
        {"text": "🖥️ GPU 集群", "callback": "gpu_cluster", "sub_menu": {
            "question": "选择 GPU 服务器：",
            "options": [...]  # GPU 服务器列表
        }},
        {"text": "💻 CPU 集群", "callback": "cpu_cluster", "sub_menu": {
            "question": "选择 CPU 服务器：",
            "options": [...]  # CPU 服务器列表
        }}
    ]
)
```

---

### Bad Case 3: 回调标识不唯一导致冲突

**❌ 错误做法**:
```python
menu = ButtonMenu(
    question="选择环境：",
    options=[
        {"text": "生产环境", "callback": "prod"},
        {"text": "测试环境", "callback": "test"}
    ]
)

# 另一个菜单
menu2 = ButtonMenu(
    question="选择数据库：",
    options=[
        {"text": "生产库", "callback": "prod"},  # ❌ 冲突！
        {"text": "测试库", "callback": "test"}   # ❌ 冲突！
    ]
)
```

**✅ 正确做法**:
```python
# 使用命名空间或前缀
menu = ButtonMenu(
    question="选择环境：",
    options=[
        {"text": "生产环境", "callback": "env_prod"},
        {"text": "测试环境", "callback": "env_test"}
    ]
)

menu2 = ButtonMenu(
    question="选择数据库：",
    options=[
        {"text": "生产库", "callback": "db_prod"},  # ✅ 唯一
        {"text": "测试库", "callback": "db_test"}   # ✅ 唯一
    ]
)
```

---

### Bad Case 4: 按钮缺少详细说明

**场景**: 用户需要选择 GitHub 发布方式

**❌ 错误做法** - 只有简短标题，没有解释：
```python
menu = ButtonMenu(
    question="📤 发布 Telebutton 到 GitHub\n\n请选择方式：",  # ❌ 太简单
    options=[
        {"text": "🚀 快速推送", "callback": "quick_push"},
        {"text": "🔧 手动配置", "callback": "manual"}
    ]
)
```

**问题**:
- 用户不知道"快速推送"具体是什么意思
- 不清楚两种方式的区别
- 不知道需要提供什么信息
- 容易选错后才发现不符合预期

**✅ 正确做法** - 详细说明每个选项：
```python
menu = ButtonMenu(
    question="""📤 发布 Telebutton 到 GitHub

请选择合适的发布方式：

🚀 快速推送
• 自动创建 GitHub 仓库
• 使用 gh CLI 一键推送
• 需要你的 GitHub 用户名
• 适合已有 gh 认证的用户

🔧 手动配置
• 引导你手动创建仓库
• 提供完整的 git 命令
• 适合首次使用或需要自定义配置""",
    options=[
        {"text": "🚀 快速推送", "callback": "quick_push"},
        {"text": "🔧 手动配置", "callback": "manual"}
    ]
)

show_menu(menu)
result = wait_selection()

if result['callback'] == 'quick_push':
    # 进一步询问必要信息
    ask_github_username()
elif result['callback'] == 'manual':
    # 提供详细的手动步骤
    show_manual_steps()
```

**使用时机**: 
- 当选项之间的区别不明显时
- 当选项需要用户额外提供信息时
- 当用户可能不熟悉选项含义时
- 当选择后会产生不可逆操作时

**设计原则**:
- 按钮文字简洁（不超过10字）
- 详细说明放在 question 中
- 每个选项说明其特点、要求和后果
- 必要时在选择后进一步确认

---

### Bad Case 5: 使用文本数字菜单而不是 Telegram 内联按钮

**场景**: 提供多个选项供用户选择

**❌ 错误做法** - 使用数字列表让用户回复数字：
```
📋 请选择操作：

1️⃣ 查看状态
2️⃣ 执行任务
3️⃣ 设置选项
4️⃣ 帮助信息

请回复数字 1-4 来选择
```

**问题**:
- 用户需要手动输入数字，容易输错
- 交互体验差，需要打字而不是点击
- 需要额外处理无效输入（用户回复非数字、超范围数字等）
- 不直观，用户需要记住数字对应的选项
- 在移动端尤其不便

**✅ 正确做法** - 使用 Telegram 内联按钮：
```python
from telebutton import ButtonMenu, show_menu, wait_selection

menu = ButtonMenu(
    question="📋 请选择操作：",
    options=[
        {"text": "📊 查看状态", "callback": "status"},
        {"text": "▶️ 执行任务", "callback": "execute"},
        {"text": "⚙️ 设置选项", "callback": "settings"},
        {"text": "❓ 帮助信息", "callback": "help"}
    ],
    max_per_row=2
)

show_menu(menu)
result = wait_selection()

# 处理选择
if result['callback'] == 'status':
    show_status()
elif result['callback'] == 'execute':
    run_task()
```

**使用原则**:
- **永远优先使用内联按钮**（InlineKeyboardButton）
- 文本数字菜单只作为万不得已的备选方案
- 内联按钮提供直观的一键选择体验
- 避免用户输入错误，提高交互效率

---

## ✅ Features - 进阶特性

### Feature 1: 分离介绍和按钮（多消息交互）

**场景**: 当选项说明较长，需要给用户充分阅读时间

**实现方式** - 分两条消息发送：
```python
# 第一步：发送详细介绍（纯文本）
send_message("""📤 发布 Telebutton Skill 到 GitHub

这个操作将把 telebutton 代码推送到 GitHub 公开仓库。

**可选方式：**

🚀 **快速推送**
• 自动创建 GitHub 仓库
• 一键完成初始化、提交、推送
• 需要 GitHub Token

🔧 **手动创建**
• 手动在网页创建仓库
• 复制命令执行
• 适合自定义配置""")

# 第二步：发送简洁的选择按钮
menu = ButtonMenu(
    question="请选择一个方式：",
    options=[
        {"text": "🚀 快速推送", "callback": "quick_push"},
        {"text": "🔧 手动创建", "callback": "manual"}
    ]
)

show_menu(menu)
```

**适用场景**:
- 选项说明较长（超过 3-4 行）
- 需要给用户阅读消化时间
- 移动端展示时避免按钮被推到屏幕外
- 复杂选项需要对比时

**优势**:
- 介绍文字和按钮分离，界面清晰
- 用户可以充分阅读后再做选择
- 按钮始终可见，无需滚动
- 更好的移动端体验
