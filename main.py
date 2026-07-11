import math
import re
from abc import ABC, abstractmethod
from argparse import Namespace
from copy import copy
from typing import Callable, Collection

import numpy


class Accident(Exception): pass


class IndexAccident(Accident): pass


class TypeAccident(Accident): pass


class NameAccident(Accident): pass


class IntrospectAccident(Accident): pass


class EvalAccident(Accident): pass


class DivisionAccident(Accident): pass


class NotAllowedOperationAccident(Accident): pass


class BlockPlacementAccident(NotAllowedOperationAccident):
    def __init__(self, pos: tuple[int, int, int], block: Block):
        self.pos = pos
        self.block = block

    def __str__(self):
        return f"本应在{self.pos}处接受一个可放置方块的地方，而实际接受了{self.block}"


class RunTypeAccident(NotAllowedOperationAccident):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f"本应运行一个命令，而实际接受了{self.value}"


class Block:
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return self.name


class World:
    def __init__(self):
        self.blocks: dict[tuple[int, int, int], Block] = {}

    def add_block(self, pos: tuple[int, int, int], block: Block):
        if pos in self.blocks:
            raise BlockPlacementAccident(pos, self.blocks[pos])
        self.blocks[pos] = block
        print(f"place_block: 已在位置{pos}处放置方块{block}")

    def remove_block(self, pos: tuple[int, int, int]):
        if pos in self.blocks:
            del self.blocks[pos]
            print(f"break_block: 已移除位置{pos}处的方块")
        else:
            print(f"break_block: 位置{pos}处没有方块")

    def clear(self):
        self.blocks.clear()


class MindStack:
    def __init__(self, caster: Entity, world: World, verbose: bool = True):
        self.stack = []
        self.caster = caster
        self.world = world
        self.local = None
        self.introspect = []
        self.introspect_level = 0
        self.verbose = verbose

    def copy_stack(self):
        new_stack = MindStack(self.caster, self.world, self.verbose)
        new_stack.stack = self.stack.copy()
        return new_stack

    def push(self, *item):
        if self.verbose:
            if len(self.stack) > 20:
                display_str = f"[...({len(self.stack) - 20} more), {"".join(f"{i}, " for i in self.stack[-20:])}*{", ".join(str(i) for i in item)}]"
            else:
                display_str = f"[{"".join(f"{i}, " for i in self.stack)}*{", ".join(str(i) for i in item)}]"
            if len(display_str) > 100:
                display_str = display_str[:50] + "..." + display_str[-50:]
            print(display_str)
        self.stack.extend(item)

    def pop(self, *args):
        count = len(args)
        if len(self.stack) >= count:
            removed = tuple(self.stack[-count:])
            del self.stack[-count:]
            for i, (val, type) in enumerate(zip(removed, args)):
                if not isinstance(val, type):
                    raise TypeAccident(count - 1 - i, type, val)
            if self.verbose:
                print(f"~ {removed}")
            return removed
        raise IndexAccident(count)

    def set_local(self, local):
        self.local = local
        print(f"local: {self.local}")

    def run_command(self, command):
        try:
            if not isinstance(command, str):
                raise RunTypeAccident(command)
            if self.introspect_level > 0 and command not in '()':
                self.introspect.append(command)
            else:
                match command:
                    case '/stack':
                        print(self.stack)
                    case '/clear':
                        self.stack.clear()
                        print("已清空栈")
                    case '/clear_world':
                        self.world.clear()
                        print("世界已清空")
                    case '/local':
                        print(f"local: {self.local}")
                    case '/verbose':
                        self.verbose = True
                        print("详细模式已开启")
                    case '/quiet':
                        self.verbose = False
                        print("安静模式已开启")
                    case '/get_block':
                        pos = input("请输入要获取的方块位置：")
                        pos: tuple[int, int, int] = tuple(map(int, pos.split()))
                        if pos not in self.world.blocks:
                            print(f"位置{pos}处没有方块")
                        print(f"位置{pos}处的方块是{self.world.blocks[pos]}")
                    case '/get_blocks':
                        for i in self.world.blocks:
                            print(f"  {str(i):10}: {self.world.blocks[i]}")
                    case 'print':
                        value = self.pop(object)
                        print(f"[print] {value}")
                        self.push(value)
                    case 'get_caster':
                        self.push(self.caster)
                    case 'entity_pos/eye':
                        entity: Entity = self.pop(Entity)[0]
                        self.push(entity.pos + Vector(0, entity.eye_height, 0))
                    case 'entity_pos/foot':
                        entity: Entity = self.pop(Entity)[0]
                        self.push(entity.pos)
                    case 'const/true':
                        self.push(True)
                    case 'const/false':
                        self.push(False)
                    case 'const/double/tau':
                        self.push(math.tau)
                    case 'const/double/pi':
                        self.push(math.pi)
                    case 'read/local':
                        self.push(self.local)
                    case 'write/local':
                        self.set_local(self.pop(object)[0])
                    case 'duplicate':
                        self.push(*(self.pop(object) * 2))
                    case '2dup':
                        self.push(*(self.pop(object, object) * 2))
                    case 'over':
                        a, b = self.pop(object, object)
                        self.push(a, b, a)
                    case 'swap':
                        a, b = self.pop(object, object)
                        self.push(b, a)
                    case 'stack_len':
                        self.push(len(self.stack))
                    case 'construct_vec':
                        x, y, z = self.pop(float, float, float)
                        self.push(Vector(x, y, z))
                    case 'div_cross':
                        a, b = self.pop(float | Vector, float | Vector)
                        if b == 0 or isinstance(b, Vector):
                            raise DivisionAccident(a, b)
                        match a, b:
                            case (float(), float()) | (Vector(), float()):
                                self.push(a / b)
                            case Vector(), Vector():
                                self.push(a.cross(b))
                    case 'mul_dot':
                        a, b = self.pop(float | Vector, float | Vector)
                        match a, b:
                            case (float(), float()) | (Vector(), float()) | (float(), Vector()):
                                self.push(a * b)
                            case Vector(), Vector():
                                self.push(a.dot(b))
                    case 'sub':
                        a, b = self.pop(float | Vector, float | Vector)
                        match a, b:
                            case float(), float():
                                self.push(a - b)
                            case Vector(), float():
                                self.push(a - Vector(b, b, b))
                            case float(), Vector():
                                self.push(Vector(a, a, a) - b)
                            case Vector(), Vector():
                                self.push(a - b)
                    case 'add':
                        a, b = self.pop(float | Vector, float | Vector)
                        match a, b:
                            case float(), float():
                                self.push(a + b)
                            case Vector(), float():
                                self.push(a + Vector(b, b, b))
                            case float(), Vector():
                                self.push(Vector(a, a, a) + b)
                            case Vector(), Vector():
                                self.push(a + b)
                    case 'less':
                        a, b = self.pop(float, float)
                        self.push(a < b)
                    case 'greater':
                        a, b = self.pop(float, float)
                        self.push(a > b)
                    case 'cos':
                        self.push(math.cos(self.pop(float)[0]))
                    case 'sin':
                        self.push(math.sin(self.pop(float)[0]))
                    case 'tan':
                        self.push(math.tan(self.pop(float)[0]))
                    case 'break_block':
                        pos = self.pop(Vector)[0]
                        self.world.remove_block(pos.to_int_tuple())
                    case 'place_block':
                        pos = self.pop(Vector)[0]
                        block = self.caster.get_block()
                        self.world.add_block(pos.to_int_tuple(), block)
                    case 'if':
                        condition, then, else_ = self.pop(bool, object, object)
                        if condition:
                            self.push(then)
                        else:
                            self.push(else_)
                    case '(':
                        if self.introspect_level > 0:
                            self.introspect.append(command)
                        self.introspect_level += 1
                    case ')':
                        if self.introspect_level == 0:
                            raise IntrospectAccident
                        elif self.introspect_level == 1:
                            self.push(tuple(self.introspect))
                            self.introspect = []
                            self.introspect_level -= 1
                        else:
                            self.introspect.append(command)
                            self.introspect_level -= 1
                    case 'eval':
                        to_eval = self.pop(str | tuple)[0]
                        l = ()
                        if isinstance(to_eval, str):
                            l = (to_eval,)
                        elif isinstance(to_eval, tuple):
                            l = to_eval
                        for i in l:
                            if self.verbose:
                                print(f"{" " * 4 * self.introspect_level}eval> {i}")
                            run_result = self.run_command(i)
                            if not run_result == 'success':
                                if run_result == 'accident':
                                    raise EvalAccident
                    case 'for_each':
                        commands, iterable = self.pop(tuple, tuple)
                        result = []
                        for i in iterable:
                            new_stack = self.copy_stack()
                            new_stack.push(i)
                            for c in commands:
                                if self.verbose:
                                    print(f"{" " * 4 * (self.introspect_level + new_stack.introspect_level)}for_each> {c}")
                                run_result = new_stack.run_command(c)
                                if not run_result == 'success':
                                    if run_result == 'accident':
                                        raise EvalAccident
                            result.extend(new_stack.stack)
                        self.push(tuple(result))
                    case 'last_n_list':
                        count = int(self.pop(float)[0])
                        items = self.pop(*([object] * count))
                        self.push(tuple(items))
                    case 'splat':
                        l = self.pop(tuple)[0]
                        self.push(*l)
                    case 'index':
                        l, n = self.pop(tuple, float)
                        n = int(n)
                        try:
                            self.push(l[n])
                        except IndexError:
                            self.push(None)
                    case 'slice':
                        l, start, end = self.pop(tuple, float, float)
                        start = int(start)
                        end = int(end)
                        if start > end:
                            start, end = end, start
                        self.push(tuple(l[start:end]))
                    case 'append':
                        l, item = self.pop(tuple, object)
                        self.push(l + (item,))
                    case 'concat':
                        l1, l2 = self.pop(tuple, tuple)
                        self.push(l1 + l2)
                    case 'empty_list':
                        self.push(())
                    case 'singleton':
                        self.push((self.pop(object)[0],))
                    case 'list_size':
                        self.push(len(self.pop(tuple)[0]))
                    case 'reverse_list':
                        self.push(tuple(reversed(self.pop(tuple)[0])))
                    case 'index_of':
                        l, item = self.pop(tuple, object)
                        try:
                            self.push(l.index(item))
                        except ValueError:
                            self.push(-1)
                    case 'list_remove':
                        l, n = self.pop(tuple, float)
                        n = int(n)
                        self.push(l[:n] + l[n + 1:])
                    case 'modify_in_place':
                        l, n, item = self.pop(tuple, float, object)
                        n = int(n)
                        if 0 <= n < len(l):
                            self.push(l[:n] + (item,) + l[n + 1:])
                    case 'construct':
                        l, item = self.pop(tuple, object)
                        self.push(tuple((item,) + l))
                    case 'deconstruct':
                        l = self.pop(tuple)[0]
                        if len(l) == 0:
                            self.push((), None)
                        else:
                            self.push(tuple(l[1:]), l[0])
                    case 'halt':
                        return 'halt'
                    case _ if re.match("num_.*", command):
                        self.push(float(command.lstrip("num_")))
                    case _ if re.match("mask_.*", command):
                        mask_str = command.lstrip("mask_")
                        if not set(mask_str).issubset({'v', '-'}):
                            raise NameAccident
                        elements = self.pop(*([object] * len(mask_str)))
                        result = []
                        for i, c in enumerate(mask_str):
                            if c == '-':
                                result.append(elements[i])
                        self.push(*result)
                    case _:
                        raise NameAccident
        except IndexAccident as e:
            if len(self.stack) == 0:
                print(f"[Accident] {command}本应接受大于等于{e}个参数，而实际为空栈")
            else:
                print(f"[Accident] {command}本应接受大于等于{e}个参数，而实际栈中元素数为{len(self.stack)}")
        except TypeAccident as e:
            print(f"[Accident] {command}本应在栈下标为{e.args[0]}处接受一个{e.args[1].__name__}，而实际接受了{e.args[2]}")
        except NameAccident as e:
            print(f"[Accident] 未知符号：{command}")
        except IntrospectAccident as e:
            print("[Accident] 在绘制反思前未先绘制内省")
        except DivisionAccident as e:
            print(f"[Accident] 试图用{e.args[1]}除{e.args[0]}")
        except EvalAccident as e:
            pass  # 错误发生在元运行方式运行命令期间，直接传播
        except NotAllowedOperationAccident as e:
            print(f"[Accident] {e}")
        else:
            return 'success'
        return 'accident'

    def run_program(self, text):
        for cmd in split_command(text):
            if self.verbose:
                print(f"{" " * 4 * self.introspect_level}run_program> {cmd}")
            if not self.run_command(cmd) == 'success':
                break


class Item:
    def __init__(self, data=None):
        self.data = data


class Entity:
    def __init__(self, name, pos: Vector, eye_height: float):
        self.name = name
        self.pos = pos
        self.eye_height = eye_height
        self.selected_item = None
        self.inventory = []

    def ray_cast_entity(self):
        return None

    def get_block(self):
        return STONE

    def __str__(self):
        return self.name

    __repr__ = __str__


class Vector:
    def __init__(self, x, y, z):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def to_int_tuple(self):
        return int(self.x), int(self.y), int(self.z)

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __str__(self):
        return f"({self.x:.2f}, {self.y:.2f}, {self.z:.2f})"

    def __iter__(self):
        return iter([self.x, self.y, self.z])

    def __truediv__(self, other: float):
        return Vector(self.x / other, self.y / other, self.z / other)

    def __mul__(self, other: float):
        return Vector(self.x * other, self.y * other, self.z * other)

    def __rmul__(self, other: float):
        return self * other

    def __sub__(self, other: Vector):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __neg__(self):
        return Vector(-self.x, -self.y, -self.z)

    def cross(self, other):
        return Vector(*numpy.cross(self, other))

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __hash__(self):
        return hash((self.x, self.y, self.z))

    __repr__ = __str__


def start_repl(mind_stack: MindStack):
    while True:
        text = input(f"{" " * 4 * mind_stack.introspect_level}> ")
        mind_stack.run_program(text)


def run_file(mind_stack: MindStack, file_name: str):
    with open(file_name, encoding="utf-8") as f:
        text = f.read()
    mind_stack.run_program(text)


def split_command(text):
    # 移除多行注释 /* ... */
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    # 移除单行注释 // ...
    text = re.sub(r'//[^\n]*', '', text)
    pattern = r'[^\s,()]+|\(|\)'
    return re.findall(pattern, text)


STONE = Block("stone")


def main(args=None):
    if args is None:
        import argparse
        parser = argparse.ArgumentParser(
            prog='hexparse',
            description='HexParse 解释器 - 基于栈的编程语言',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog='''
示例:
    python main.py              启动 REPL
    python main.py script.hex   运行脚本文件
    python main.py a.hex b.hex  依次运行多个文件（共享栈）
    python main.py -c "num_1 num_2 add"  执行命令
    python main.py -i script.hex   运行文件后进入 REPL
    python main.py -q script.hex  安静模式（仅显示错误和 print）
            '''
        )
        parser.add_argument('files', nargs='*', help='要运行的脚本文件')
        parser.add_argument('-c', '--command', help='直接执行命令字符串')
        parser.add_argument('-i', '--interactive', action='store_true', help='运行后进入交互模式 (REPL)')
        parser.add_argument('-q', '--quiet', action='store_true', help='安静模式，隐藏执行提示')

        args = parser.parse_args()

    verbose = not args.quiet

    caster = Entity("caster", Vector(0, 0, 0), 1.8)
    m = MindStack(caster=caster, world=World(), verbose=verbose)

    # 运行文件
    for file_name in args.files:
        try:
            run_file(m, file_name)
        except FileNotFoundError:
            print(f"[错误] 文件不存在: {file_name}")
            return 1

    # 执行 -c 命令
    if args.command:
        m.run_program(args.command)

    # 进入 REPL
    if args.interactive or (not args.files and not args.command):
        start_repl(m)

    return 0


if __name__ == '__main__':
    args = Namespace()
    args.files = ["example/for_each.hexparse"]
    args.quiet = False
    args.command = None
    args.interactive = True
    exit(main(args))

    # exit(main())

"""
运行示例：
> const/true
[*True]
> (
    > const/true
    > num_1
    > num_2
    > if
    > )
[True, *['const/true', 'num_1', 'num_2', 'if']]
> ()
[True, ['const/true', 'num_1', 'num_2', 'if'], *[]]
> if
~ [True, ['const/true', 'num_1', 'num_2', 'if'], []]
[*['const/true', 'num_1', 'num_2', 'if']]
> eval
~ [['const/true', 'num_1', 'num_2', 'if']]
eval> const/true
[*True]
eval> num_1
[True, *1.0]
eval> num_2
[True, 1.0, *2.0]
eval> if
~ [True, 1.0, 2.0]
[*1.0]
> 
"""
