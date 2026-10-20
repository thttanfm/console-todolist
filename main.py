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

# ----------------------------------------------------------------------
# 配置区
# ----------------------------------------------------------------------

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")

# 待办事项的字段定义：(字段名, 显示名称, 是否必填)
# 想要新增字段时，只需在这里添加一行，展示 / 添加 / 修改逻辑会自动生效。
ITEM_FIELDS = [
    ("name", "名称", True),
    ("due_date", "截止日期", True),
]


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
        print("警告：data.json 读取失败，将以空列表开始。")
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
        print(f"无效选项，请输入 {'/'.join(keys)} 之一。")


def prompt_index(count):
    """让用户输入 1..count 的条目编号。"""
    while True:
        raw = input(f"请输入条目编号 (1-{count}) > ").strip()
        if raw.isdigit() and 1 <= int(raw) <= count:
            return int(raw)
        print("无效编号，请重新输入。")


def format_item(index, item):
    """把一条待办事项格式化为一行文本。"""
    parts = [f"{label}：{item.get(field, '')}" for field, label, _ in ITEM_FIELDS]
    return f"[{index}] " + " | ".join(parts)


# ----------------------------------------------------------------------
# 具体操作
# ----------------------------------------------------------------------

def view_todos(todos):
    """查看所有待办事项，任意键返回。"""
    print("\n=== 待办事项列表 ===")
    if not todos:
        print("（暂无待办事项）")
    else:
        for i, item in enumerate(todos, 1):
            print(format_item(i, item))
    input("\n按回车键返回主菜单...")


def add_todo(todos):
    """添加一条待办事项。"""
    print("\n--- 添加待办事项 ---")
    item = {}
    for field, label, required in ITEM_FIELDS:
        while True:
            value = input(f"请输入{label}：").strip()
            if value or not required:
                item[field] = value
                break
            print(f"{label}不能为空。")
    todos.append(item)
    save_data(todos)
    print("已添加。")


def delete_todo(todos):
    """删除一条待办事项。"""
    print("\n--- 删除待办事项 ---")
    if not todos:
        print("（暂无待办事项）")
        return
    for i, item in enumerate(todos, 1):
        print(format_item(i, item))
    idx = prompt_index(len(todos))
    removed = todos.pop(idx - 1)
    save_data(todos)
    print(f"已删除：{removed.get('name', '')}")


def modify_todo(todos):
    """更改一条待办事项的字段内容。"""
    print("\n--- 更改待办事项 ---")
    if not todos:
        print("（暂无待办事项）")
        return
    for i, item in enumerate(todos, 1):
        print(format_item(i, item))
    idx = prompt_index(len(todos))
    item = todos[idx - 1]

    for field, label, required in ITEM_FIELDS:
        current = item.get(field, "")
        while True:
            value = input(f"新的{label}（当前：{current}，直接回车保留原值）：").strip()
            if not value:
                break
            item[field] = value
            break
    save_data(todos)
    print("已更新。")


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
        print("\n=== 修改待办事项 ===")
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
        print("\n=== 待办事项 ===")
        show_menu(options)
        choice = prompt_choice(options)
        if choice == "a":
            view_todos(todos)
        elif choice == "b":
            modify_menu(todos)
        elif choice == "c":
            print("再见！")
            return


def main():
    todos = load_data()
    main_menu(todos)


if __name__ == "__main__":
    main()