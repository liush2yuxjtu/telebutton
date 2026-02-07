#!/usr/bin/env python3
"""
Telebutton - Telegram 选择按钮交互库

提供简单的 API 在 Telegram 中展示选择按钮并获取用户反馈。
"""

import json
import time
import uuid
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable
from pathlib import Path

# 全局状态存储（临时内存存储）
_pending_selections: Dict[str, Any] = {}
_menu_registry: Dict[str, 'ButtonMenu'] = {}


@dataclass
class ButtonOption:
    """单个按钮选项"""
    text: str
    callback: str
    sub_menu: Optional['ButtonMenu'] = None
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        result = {
            "text": self.text,
            "callback": self.callback
        }
        if self.sub_menu:
            result["sub_menu"] = self.sub_menu.to_dict()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ButtonOption':
        """从字典创建"""
        sub_menu = None
        if "sub_menu" in data:
            sub_menu = ButtonMenu.from_dict(data["sub_menu"])
        return cls(
            text=data["text"],
            callback=data["callback"],
            sub_menu=sub_menu
        )


@dataclass
class ButtonMenu:
    """按钮菜单配置"""
    question: str
    options: List[ButtonOption]
    max_per_row: int = 2
    menu_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "question": self.question,
            "options": [opt.to_dict() for opt in self.options],
            "max_per_row": self.max_per_row,
            "menu_id": self.menu_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ButtonMenu':
        """从字典创建"""
        options = [ButtonOption.from_dict(opt) for opt in data.get("options", [])]
        menu = cls(
            question=data["question"],
            options=options,
            max_per_row=data.get("max_per_row", 2)
        )
        if "menu_id" in data:
            menu.menu_id = data["menu_id"]
        return menu
    
    def find_option(self, callback: str) -> Optional[ButtonOption]:
        """查找选项"""
        for opt in self.options:
            if opt.callback == callback:
                return opt
        return None
    
    def get_all_callbacks(self) -> List[str]:
        """获取所有回调标识（包括子菜单）"""
        callbacks = []
        for opt in self.options:
            callbacks.append(opt.callback)
            if opt.sub_menu:
                callbacks.extend(opt.sub_menu.get_all_callbacks())
        return callbacks


def load_menu_from_file(filepath: str) -> ButtonMenu:
    """
    从 YAML 或 JSON 文件加载菜单配置
    
    Args:
        filepath: 配置文件路径 (.yaml, .yml, 或 .json)
    
    Returns:
        ButtonMenu 实例
    """
    import yaml
    
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"配置文件不存在: {filepath}")
    
    with open(path, 'r', encoding='utf-8') as f:
        if path.suffix in ['.yaml', '.yml']:
            data = yaml.safe_load(f)
        else:
            data = json.load(f)
    
    return ButtonMenu.from_dict(data)


def save_menu_to_file(menu: ButtonMenu, filepath: str):
    """
    保存菜单配置到文件
    
    Args:
        menu: ButtonMenu 实例
        filepath: 目标文件路径
    """
    import yaml
    
    path = Path(filepath)
    with open(path, 'w', encoding='utf-8') as f:
        if path.suffix in ['.yaml', '.yml']:
            yaml.dump(menu.to_dict(), f, allow_unicode=True, default_flow_style=False)
        else:
            json.dump(menu.to_dict(), f, ensure_ascii=False, indent=2)


def _generate_inline_keyboard(menu: ButtonMenu) -> List[List[Dict]]:
    """
    生成 Telegram InlineKeyboard 格式
    
    Args:
        menu: 菜单配置
    
    Returns:
        Telegram InlineKeyboardMarkup 格式
    """
    keyboard = []
    row = []
    
    for i, option in enumerate(menu.options):
        # 注册回调
        callback_data = f"{menu.menu_id}:{option.callback}"
        
        row.append({
            "text": option.text,
            "callback_data": callback_data
        })
        
        # 按 max_per_row 换行
        if (i + 1) % menu.max_per_row == 0:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    return keyboard


def show_menu(menu: ButtonMenu, chat_id: Optional[str] = None, 
              use_openclaw: bool = True) -> Optional[str]:
    """
    发送按钮菜单到 Telegram
    
    Args:
        menu: ButtonMenu 实例
        chat_id: 目标聊天 ID（None 表示使用当前会话）
        use_openclaw: 是否使用 OpenClaw 消息工具发送
    
    Returns:
        message_id 或 None
    """
    # 注册菜单
    _menu_registry[menu.menu_id] = menu
    
    # 生成键盘
    keyboard = _generate_inline_keyboard(menu)
    
    if use_openclaw:
        # 使用 OpenClaw 消息工具发送
        return _send_via_openclaw(menu.question, keyboard, chat_id)
    else:
        # 直接调用 Telegram API
        return _send_via_telegram_api(menu.question, keyboard, chat_id)


def _send_via_openclaw(text: str, keyboard: List[List[Dict]], 
                       chat_id: Optional[str] = None) -> Optional[str]:
    """通过 OpenClaw 发送消息"""
    # 实际实现会通过 OpenClaw 的 message 工具发送
    # 这里返回模拟的 message_id
    message_id = f"msg_{int(time.time())}"
    
    # 构建按钮显示文本（用于调试）
    buttons_text = []
    for row in keyboard:
        row_text = " | ".join([btn["text"] for btn in row])
        buttons_text.append(f"[{row_text}]")
    
    print(f"\n[Telegram] Telegram 按钮消息:\n")
    print(f"[Text] {text}")
    print("\n".join(buttons_text))
    print()
    
    return message_id


def _send_via_telegram_api(text: str, keyboard: List[List[Dict]],
                           chat_id: Optional[str] = None) -> Optional[str]:
    """直接调用 Telegram Bot API 发送"""
    import os
    import requests
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        raise ValueError("未设置 TELEGRAM_BOT_TOKEN 环境变量")
    
    api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    payload = {
        "chat_id": chat_id or os.getenv("TELEGRAM_CHAT_ID"),
        "text": text,
        "reply_markup": {
            "inline_keyboard": keyboard
        }
    }
    
    try:
        response = requests.post(api_url, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return str(result["result"]["message_id"])
    except Exception as e:
        print(f"发送消息失败: {e}")
        return None


def wait_selection(menu_id: Optional[str] = None, timeout: int = 300,
                   delete_message: bool = True) -> Optional[Dict]:
    """
    等待用户选择
    
    Args:
        menu_id: 菜单 ID（None 表示等待任何菜单）
        timeout: 超时时间（秒）
        delete_message: 选择后是否删除原消息
    
    Returns:
        {
            "callback": str,       # 回调标识
            "text": str,           # 按钮文字
            "path": List[str],     # 选择路径
            "menu_id": str         # 菜单 ID
        }
        或 None（超时）
    """
    # 实际实现需要监听 Telegram 回调
    # 这里提供模拟实现
    
    wait_key = menu_id or "any"
    start_time = time.time()
    
    print(f"[...] 等待用户选择... (超时: {timeout}秒)")
    print("提示: 在真实环境中，这里会阻塞等待 Telegram 回调")
    
    # 模拟：在测试环境下返回第一个选项
    # 实际使用时，这应该从 Telegram webhook 或轮询获取
    
    # TODO: 实现真实的回调监听
    # 需要与 OpenClaw 的消息系统集成
    
    return None


def handle_callback(callback_data: str) -> Optional[Dict]:
    """
    处理 Telegram 回调数据
    
    Args:
        callback_data: Telegram callback_query data (格式: menu_id:callback)
    
    Returns:
        解析后的选择信息，或 None（无效回调）
    """
    try:
        parts = callback_data.split(":", 1)
        if len(parts) != 2:
            return None
        
        menu_id, callback = parts
        
        # 查找菜单
        menu = _menu_registry.get(menu_id)
        if not menu:
            return None
        
        # 查找选项
        option = menu.find_option(callback)
        if not option:
            return None
        
        result = {
            "callback": callback,
            "text": option.text,
            "menu_id": menu_id,
            "path": [callback]
        }
        
        # 如果有子菜单，返回子菜单供后续展示
        if option.sub_menu:
            result["sub_menu"] = option.sub_menu
        
        return result
        
    except Exception as e:
        print(f"处理回调失败: {e}")
        return None


def show_confirm(question: str, yes_text: str = "[OK] 是", 
                 no_text: str = "[X] 否", **kwargs) -> Optional[Dict]:
    """
    快速显示确认对话框
    
    Args:
        question: 确认问题
        yes_text: 确认按钮文字
        no_text: 取消按钮文字
        **kwargs: 传递给 show_menu 的其他参数
    
    Returns:
        选择结果，callback 为 "yes" 或 "no"
    """
    menu = ButtonMenu(
        question=question,
        options=[
            ButtonOption(text=yes_text, callback="yes"),
            ButtonOption(text=no_text, callback="no")
        ],
        max_per_row=2
    )
    
    show_menu(menu, **kwargs)
    return wait_selection(menu.menu_id)


def clear_menu(menu_id: str):
    """清理菜单注册信息"""
    if menu_id in _menu_registry:
        del _menu_registry[menu_id]


def clear_all_menus():
    """清理所有菜单"""
    _menu_registry.clear()
    _pending_selections.clear()


# 便捷函数
ask = show_confirm  # 别名
select = wait_selection  # 别名


if __name__ == "__main__":
    # 测试示例
    print("🧪 Telebutton 测试\n")
    
    # 创建示例菜单
    menu = ButtonMenu(
        question="🖥️ 选择执行环境：",
        options=[
            ButtonOption(text="💻 本地", callback="local"),
            ButtonOption(
                text="☁️ 远程",
                callback="remote",
                sub_menu=ButtonMenu(
                    question="选择服务器：",
                    options=[
                        ButtonOption(text="HPC-01", callback="hpc01"),
                        ButtonOption(text="HPC-02", callback="hpc02")
                    ],
                    max_per_row=2
                )
            )
        ]
    )
    
    # 显示菜单
    msg_id = show_menu(menu, use_openclaw=False)
    print(f"\n消息 ID: {msg_id}")
    
    # 测试确认框
    print("\n" + "="*40)
    result = show_confirm("确定要删除这个文件吗？", use_openclaw=False)
    print(f"确认结果: {result}")
