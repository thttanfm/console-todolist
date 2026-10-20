#!/usr/bin/env python3
# todo.py
"""一个简单的命令行待办事项管理程序。

数据保存在脚本所在目录的 data.json 中，格式为字典列表：
[
    {"name": "...", "due_date": "..."},
    ...
]
如需扩展字段，只需修改 ITEM_FIELDS（以及必要时的输入校验）即可。
"""

import json
import os
import re
from termcolor import colored
from datetime import datetime, date

# ----------------------------------------------------------------------
# 配置区
# ----------------------------------------------------------------------

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")

# 待办事项的字段定义：(字段名, 显示名称, 字段类型, 是否必填)
# 类型 "text" 为普通文本，类型 "date" 为日期（存储为 {"year", "month", "day"}）
# 想要新增字段时，只需在这里添加一行，展示 / 添加 / 修改逻辑会自动生效。
ITEM_FIELDS = [
    ("name", "名称", "text", True),
    ("due_date", "截止日期", "date", True),
]

def out_error(msg, end='\n'):
    print(colored(msg, 'red'), end=end)

def out_warn(msg, end='\n'):
    print(colored(msg, 'yellow'), end=end)

def out_info(msg, end='\n'):
    print(colored(msg, 'green'), end=end)


# ----------------------------------------------------------------------
# 数据读写
# ----------------------------------------------------------------------

def load_data():
    """从 data.json 读取待办事项，文件不存在或损坏时返回空列表。"""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        out_warn("警告：data.json 读取失败，将以空列表开始。")
        return []


def save_data(todos):
    """把待办事项写回 data.json。"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(todos, f, ensure_ascii=False, indent=2)


# ----------------------------------------------------------------------
# 通用交互工具
# ----------------------------------------------------------------------

def show_menu(options):
    """按 “a. xxx” 的格式打印菜单。options: [(字母, 描述), ...]"""
    for key, desc in options:
        print(f"{key}. {desc}")


def prompt_choice(options):
    """让用户输入字母选择，返回选中的字母。"""
    keys = [k for k, _ in options]
    while True:
        raw = input("请选择 > ").strip().lower()
        if raw in keys:
            return raw
        out_error(f"无效选项，请输入 {'/'.join(keys)} 之一。")


def prompt_index(count):
    """让用户输入 1..count 的条目编号。"""
    while True:
        raw = input(f"请输入条目编号 (1-{count}) > ").strip()
        if raw.isdigit() and 1 <= int(raw) <= count:
            return int(raw)
        out_error("无效编号，请重新输入。")


def format_date(d):
    """把存储的日期（字典）格式化为 yyyy-mm-dd 字符串；兼容旧格式的字符串。"""
    if isinstance(d, dict):
        return f"{d.get('year', 0):04d}-{d.get('month', 0):02d}-{d.get('day', 0):02d}"
    return str(d) if d else ""

def prompt_date(label="截止日期", current=None):
    """交互式读取日期，严格校验 yyyy-mm-dd，并对过去日期发出警告。

    current 为已有日期（修改时传入），直接回车可保留原值。
    返回 {"year": int, "month": int, "day": int}。
    """
    # 兼容旧数据（字符串格式）——无法回显则视为无当前值
    if current is not None and not isinstance(current, dict):
        current = None

    while True:
        prompt = f"请输入{label}（格式 yyyy-mm-dd）"
        if current:
            prompt += f"，当前：{format_date(current)}，直接回车保留原值"
        value = input(prompt + "：").strip()

        if not value and current:
            return current

        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            out_info("格式错误，请严格按 yyyy-mm-dd 输入，例如 2025-10-20。")
            continue

        try:
            dt = datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            out_info("日期无效（月份或日期超出范围），请重新输入。")
            continue

        if dt < date.today():
            out_warn(f"警告：{value} 已经过去，确定要提交吗？(y/n) > ", end='')
            ans = input().strip().lower()
            if ans not in ("y", "yes"):
                continue

        return {"year": dt.year, "month": dt.month, "day": dt.day}


def format_item(index, item):
    """把一条待办事项格式化为一行文本。"""
    parts = []
    for field, label, ftype, _ in ITEM_FIELDS:
        if ftype == "date":
            parts.append(f"{label}：{format_date(item.get(field))}")
        else:
            parts.append(f"{label}：{item.get(field, '')}")
    return f"[{index}] " + " | ".join(parts)

# ----------------------------------------------------------------------
# 具体操作
# ----------------------------------------------------------------------

def view_todos(todos):
    """查看所有待办事项，任意键返回。"""
    out_info("\n=== 待办事项列表 ===")
    if not todos:
        out_warn("（暂无待办事项）")
    else:
        for i, item in enumerate(todos, 1):
            print(format_item(i, item))
    out_info("\n按回车键返回主菜单...", end='')
    input()


def add_todo(todos):
    """添加一条待办事项。"""
    out_info("\n--- 添加待办事项 ---")
    item = {}
    for field, label, ftype, required in ITEM_FIELDS:
        if ftype == "date":
            item[field] = prompt_date(label=label)
        else:
            while True:
                value = input(f"请输入{label}：").strip()
                if value or not required:
                    item[field] = value
                    break
                out_warn(f"{label}不能为空。")
    todos.append(item)
    save_data(todos)
    out_info("已添加。")


def delete_todo(todos):
    """删除一条待办事项。"""
    out_info("\n--- 删除待办事项 ---")
    if not todos:
        out_warn("（暂无待办事项）")
        return
    for i, item in enumerate(todos, 1):
        print(format_item(i, item))
    idx = prompt_index(len(todos))
    removed = todos.pop(idx - 1)
    save_data(todos)
    out_info(f"已删除：{removed.get('name', '')}")


def modify_todo(todos):
    """更改一条待办事项的字段内容。"""
    out_info("\n--- 更改待办事项 ---")
    if not todos:
        out_warn("（暂无待办事项）")
        return
    for i, item in enumerate(todos, 1):
        print(format_item(i, item))
    idx = prompt_index(len(todos))
    item = todos[idx - 1]

    for field, label, ftype, required in ITEM_FIELDS:
        if ftype == "date":
            item[field] = prompt_date(label=label, current=item.get(field))
        else:
            current = item.get(field, "")
            while True:
                out_info(f"新的{label}（当前：{current}，直接回车保留原值）：", end='')
                value = input().strip()
                if not value:
                    break
                item[field] = value
                break
    save_data(todos)
    out_info("已更新。")


# ----------------------------------------------------------------------
# 菜单流程
# ----------------------------------------------------------------------

def modify_menu(todos):
    """修改待办事项子菜单。"""
    options = [
        ("a", "添加"),
        ("b", "删除"),
        ("c", "更改"),
        ("d", "返回主菜单"),
    ]
    while True:
        out_info("\n=== 修改待办事项 ===")
        show_menu(options)
        choice = prompt_choice(options)
        if choice == "a":
            add_todo(todos)
        elif choice == "b":
            delete_todo(todos)
        elif choice == "c":
            modify_todo(todos)
        elif choice == "d":
            return


def main_menu(todos):
    """主菜单。"""
    options = [
        ("a", "查看待办事项"),
        ("b", "修改待办事项"),
        ("c", "退出"),
    ]
    while True:
        out_info("\n=== 待办事项 ===")
        show_menu(options)
        choice = prompt_choice(options)
        if choice == "a":
            view_todos(todos)
        elif choice == "b":
            modify_menu(todos)
        elif choice == "c":
            out_info("再见！")
            return


def main():
    todos = load_data()
    main_menu(todos)


if __name__ == "__main__":
    main()