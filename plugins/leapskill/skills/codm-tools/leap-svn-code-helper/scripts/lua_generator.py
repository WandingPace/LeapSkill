#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Lua 热修复代码生成器
将 C# 方法转换为 XLua hotfix 格式
"""

import re
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class ModifiedMethod:
    """修改的方法信息"""
    class_name: str
    namespace: str
    method_name: str
    method_signature: str
    method_body: str
    file_path: str
    line_start: int
    line_end: int


class CSharpToLuaConverter:
    """C# 到 Lua 转换器"""

    # C# 到 Lua 的类型映射
    TYPE_MAP = {
        'int': 'number',
        'float': 'number',
        'double': 'number',
        'bool': 'boolean',
        'string': 'string',
        'void': 'nil',
    }

    def __init__(self, reference_dir: str = None):
        """初始化转换器

        Args:
            reference_dir: 参考 Lua 代码目录
        """
        self.reference_dir = reference_dir
        self.reference_patterns: Dict[str, str] = {}

        if reference_dir and Path(reference_dir).exists():
            self._load_reference_patterns()

    def _load_reference_patterns(self):
        """加载参考代码中的转换模式"""
        ref_path = Path(self.reference_dir)
        for lua_file in ref_path.rglob("*.lua"):
            try:
                content = lua_file.read_text(encoding="utf-8")
                # 提取 xlua.hotfix 调用模式
                patterns = re.findall(
                    r"xlua\.hotfix\(CS\.([\w.]+),\s*'(\w+)'",
                    content
                )
                for full_class, method in patterns:
                    key = f"{full_class}.{method}"
                    # 提取完整的 hotfix 代码块
                    pattern = re.search(
                        rf"xlua\.hotfix\(CS\.{re.escape(full_class)},\s*'{method}'.*?end\)",
                        content,
                        re.DOTALL
                    )
                    if pattern:
                        self.reference_patterns[key] = pattern.group(0)
            except Exception as e:
                print(f"警告: 读取参考文件失败 {lua_file}: {e}", file=sys.stderr)

    def convert_method(self, method: ModifiedMethod) -> str:
        """将 C# 方法转换为 Lua hotfix 代码"""
        # 检查是否有参考代码
        full_name = f"{method.namespace}.{method.class_name}.{method.method_name}"
        if full_name in self.reference_patterns:
            return self._adapt_reference(self.reference_patterns[full_name], method)

        # 否则使用规则转换
        return self._convert_by_rules(method)

    def _adapt_reference(self, reference: str, method: ModifiedMethod) -> str:
        """根据参考代码适配新方法"""
        # TODO: 实现更智能的参考代码适配
        return reference

    def _convert_by_rules(self, method: ModifiedMethod) -> str:
        """使用规则转换 C# 方法"""
        # 解析方法签名
        params = self._parse_parameters(method.method_signature)

        # 构建 Lua 函数头
        full_class = f"{method.namespace}.{method.class_name}" if method.namespace else method.class_name

        # 参数列表（添加 self）
        lua_params = ["self"] + [p[1] for p in params]
        params_str = ", ".join(lua_params)

        # 转换方法体
        lua_body = self._convert_body(method.method_body)

        # 生成完整代码
        lua_code = f"""xlua.hotfix(CS.{full_class}, '{method.method_name}', function({params_str})
{lua_body}
end)"""

        return lua_code

    def _parse_parameters(self, signature: str) -> List[tuple]:
        """解析方法参数

        Returns:
            List of (type, name) tuples
        """
        params = []
        # 提取参数列表
        match = re.search(r"\(([^)]*)\)", signature)
        if match:
            params_str = match.group(1).strip()
            if params_str:
                for param in params_str.split(","):
                    param = param.strip()
                    parts = param.rsplit(None, 1)
                    if len(parts) == 2:
                        params.append((parts[0], parts[1]))
        return params

    def _convert_body(self, csharp_body: str) -> str:
        """转换方法体"""
        # 移除方法签名，只保留方法体
        lines = csharp_body.split("\n")

        # 找到第一个 { 和最后一个 }
        body_start = -1
        body_end = -1
        brace_count = 0

        for i, line in enumerate(lines):
            for char in line:
                if char == "{":
                    if brace_count == 0:
                        body_start = i
                    brace_count += 1
                elif char == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        body_end = i

        if body_start < 0 or body_end < 0:
            return "    -- TODO: 无法解析方法体，需要手动转换"

        # 提取方法体内容
        body_lines = lines[body_start + 1:body_end]

        # 转换每一行
        converted_lines = []
        for line in body_lines:
            converted = self._convert_line(line)
            converted_lines.append(converted)

        return "\n".join(converted_lines)

    def _convert_line(self, line: str) -> str:
        """转换单行代码"""
        original = line
        indent = len(line) - len(line.lstrip())
        line = line.strip()

        if not line or line.startswith("//"):
            # 保留空行和注释
            comment = line.replace("//", "--") if line.startswith("//") else ""
            return " " * indent + comment

        # 变量声明
        line = self._convert_variable_declaration(line)

        # 条件语句
        line = self._convert_if_statement(line)

        # 循环语句
        line = self._convert_loop(line)

        # 方法调用
        line = self._convert_method_call(line)

        # 运算符
        line = self._convert_operators(line)

        # 移除分号
        line = line.rstrip(";")

        return " " * indent + line

    def _convert_variable_declaration(self, line: str) -> str:
        """转换变量声明"""
        # var x = ...  或  Type x = ...
        match = re.match(r"(?:var|int|float|double|bool|string|[\w<>\[\]]+)\s+(\w+)\s*=\s*(.+)", line)
        if match:
            var_name = match.group(1)
            value = match.group(2)
            return f"local {var_name} = {value}"
        return line

    def _convert_if_statement(self, line: str) -> str:
        """转换条件语句"""
        # if (condition) {
        match = re.match(r"if\s*\((.+)\)\s*\{?\s*$", line)
        if match:
            condition = match.group(1)
            condition = self._convert_condition(condition)
            return f"if {condition} then"

        # else if / elif
        match = re.match(r"else\s+if\s*\((.+)\)\s*\{?\s*$", line)
        if match:
            condition = match.group(1)
            condition = self._convert_condition(condition)
            return f"elseif {condition} then"

        # else {
        if re.match(r"else\s*\{?\s*$", line):
            return "else"

        # }
        if line == "}":
            return "end"

        return line

    def _convert_condition(self, condition: str) -> str:
        """转换条件表达式"""
        # != -> ~=
        condition = condition.replace("!=", "~=")
        # && -> and
        condition = condition.replace("&&", " and ")
        # || -> or
        condition = condition.replace("||", " or ")
        # ! -> not (小心处理)
        condition = re.sub(r"!(\w)", r"not \1", condition)
        # null -> nil
        condition = condition.replace("null", "nil")
        return condition

    def _convert_loop(self, line: str) -> str:
        """转换循环语句"""
        # for (int i = 0; i < count; i++)
        match = re.match(r"for\s*\(\s*(?:int|var)\s+(\w+)\s*=\s*(\d+)\s*;\s*\w+\s*<\s*(\w+)\s*;", line)
        if match:
            var = match.group(1)
            start = match.group(2)
            end = match.group(3)
            return f"for {var} = {start}, {end} - 1 do"

        # foreach (var item in collection)
        match = re.match(r"foreach\s*\(\s*(?:var|[\w<>]+)\s+(\w+)\s+in\s+(\w+)\s*\)", line)
        if match:
            item = match.group(1)
            collection = match.group(2)
            return f"for _, {item} in pairs({collection}) do"

        # while (condition)
        match = re.match(r"while\s*\((.+)\)\s*\{?\s*$", line)
        if match:
            condition = self._convert_condition(match.group(1))
            return f"while {condition} do"

        return line

    def _convert_method_call(self, line: str) -> str:
        """转换方法调用"""
        # this.Method() -> self:Method()
        line = re.sub(r"this\.(\w+)\(", r"self:\1(", line)

        # obj.Method() -> obj:Method() (实例方法)
        # 注意：属性访问保持 obj.Property

        return line

    def _convert_operators(self, line: str) -> str:
        """转换运算符"""
        # string concatenation: + -> ..
        # 这需要更复杂的类型推断，暂时不处理

        # null check
        line = line.replace("null", "nil")

        return line


def generate_hotfix_lua(
    methods: List[ModifiedMethod],
    output_path: str,
    version_number: str,
    svn_revision: str,
    reference_dir: str = None
):
    """生成热修复 Lua 文件

    Args:
        methods: 修改的方法列表
        output_path: 输出文件路径
        version_number: 版本号（用户输入的数字）
        svn_revision: SVN 版本号
        reference_dir: 参考代码目录
    """
    converter = CSharpToLuaConverter(reference_dir)

    # 按类分组
    class_methods: Dict[str, List[ModifiedMethod]] = {}
    for method in methods:
        full_class = f"{method.namespace}.{method.class_name}" if method.namespace else method.class_name
        if full_class not in class_methods:
            class_methods[full_class] = []
        class_methods[full_class].append(method)

    # 生成 Lua 代码
    lua_parts = [
        f"-- 自动生成的热修复脚本",
        f"-- 版本号: #{version_number}",
        f"-- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"-- SVN 版本: r{svn_revision}",
        f"",
    ]

    for full_class, class_method_list in sorted(class_methods.items()):
        lua_parts.append(f"-- ============ {full_class} ============")
        for method in class_method_list:
            lua_code = converter.convert_method(method)
            lua_parts.append(lua_code)
            lua_parts.append("")

    # 确保输出目录存在
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # 写入文件
    content = "\n".join(lua_parts)
    output_file.write_text(content, encoding="utf-8")

    print(f"Lua 热修复脚本已生成: {output_path}")
    print(f"包含 {len(methods)} 个方法，来自 {len(class_methods)} 个类")

    return content


def find_latest_version_dir(automatic_dir: str) -> Optional[str]:
    """查找最新的版本目录 (CN??_WWL??)"""
    auto_path = Path(automatic_dir)
    if not auto_path.exists():
        return None

    # 查找所有符合格式的目录
    version_dirs = []
    pattern = re.compile(r"CN(\d+(?:\.\d+)?)[_-]WWL(\d+(?:\.\d+)?)", re.IGNORECASE)

    for d in auto_path.iterdir():
        if d.is_dir():
            match = pattern.search(d.name)
            if match:
                cn_ver = float(match.group(1))
                wwl_ver = float(match.group(2))
                version_dirs.append((cn_ver, wwl_ver, d.name))

    if not version_dirs:
        return None

    # 按版本号排序，取最新的
    version_dirs.sort(reverse=True)
    return version_dirs[0][2]


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="Lua 热修复代码生成器")
    parser.add_argument("client_path", help="Client 目录路径")
    parser.add_argument("version_number", help="版本号（如 101）")
    parser.add_argument("--reference", "-r", help="参考 Lua 代码目录")

    args = parser.parse_args()

    # 导入 SVN 解析器
    from svn_diff_parser import get_latest_svn_log, extract_modified_methods

    # 获取 SVN 日志
    log_entry = get_latest_svn_log(args.client_path)
    if not log_entry:
        print("错误: 无法获取 SVN 日志")
        return 1

    if not log_entry.changed_files:
        print("没有修改的 C# 文件")
        return 0

    # 提取修改的方法
    methods = extract_modified_methods(args.client_path, log_entry)
    if not methods:
        print("没有找到修改的方法")
        return 0

    # 确定输出路径
    automatic_dir = Path(args.client_path) / "Export" / "LuaHotFixArchive" / "Automatic"

    # 查找参考目录
    reference_dir = args.reference
    if not reference_dir and automatic_dir.exists():
        reference_dir = str(automatic_dir)

    # 查找最新版本目录
    version_dir = find_latest_version_dir(str(automatic_dir))
    if not version_dir:
        version_dir = "CN30.0_WWL36.0"  # 默认值

    output_path = automatic_dir / version_dir / f"#{args.version_number}" / "TestHotFix.lua"

    # 生成 Lua 代码
    generate_hotfix_lua(
        methods=methods,
        output_path=str(output_path),
        version_number=args.version_number,
        svn_revision=log_entry.revision,
        reference_dir=reference_dir
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
