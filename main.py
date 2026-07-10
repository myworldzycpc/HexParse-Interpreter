import math
import re
from abc import ABC, abstractmethod
from typing import Callable, Collection


class Accident(Exception): pass


class IndexAccident(Accident): pass


class TypeAccident(Accident): pass


class NameAccident(Accident): pass


class IntrospectAccident(Accident): pass


class EvalAccident(Accident): pass


class MindStack:
    def __init__(self, caster: Entity):
        self.stack = []
        self.caster = caster
        self.local = None
        self.introspect = []
        self.introspect_level = 0

    def push(self, *item):
        if len(self.stack) > 20:
            print(f"[...({len(self.stack) - 20} more), {"".join(f"{i}, " for i in self.stack[-20:])}*{", ".join(str(i) for i in item)}]")
        else:
            print(f"[{"".join(f"{i}, " for i in self.stack)}*{", ".join(str(i) for i in item)}]")
        self.stack.extend(item)

    def pop(self, *args):
        count = len(args)
        if len(self.stack) >= count:
            removed = self.stack[-count:]
            del self.stack[-count:]
            for i, (val, type) in enumerate(zip(removed, args)):
                if not isinstance(val, type):
                    raise TypeAccident(count - 1 - i, type, val)
            print(f"~ {removed}")
            return removed
        raise IndexAccident(count)

    def set_local(self, local):
        self.local = local
        print(f"local: {self.local}")

    def run_command(self, command):
        try:
            if self.introspect_level > 0 and command not in '()':
                self.introspect.append(command)
            else:
                match command:
                    case '/stack':
                        print(self.stack)
                    case '/clear':
                        self.stack.clear()
                        print("已清空栈")
                    case '/local':
                        print(f"local: {self.local}")
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
                    case 'swap':
                        a, b = self.pop(object, object)
                        self.push(b, a)
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
                            self.push(self.introspect)
                            self.introspect = []
                            self.introspect_level -= 1
                        else:
                            self.introspect.append(command)
                            self.introspect_level -= 1
                    case 'eval':
                        to_eval = self.pop(str | list)[0]
                        if isinstance(to_eval, str):
                            l = [to_eval]
                        elif isinstance(to_eval, list):
                            l = to_eval
                        for i in l:
                            print(f"{" " * 4 * self.introspect_level}eval> {i}")
                            if not self.run_command(i):
                                raise EvalAccident
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
            return False
        except TypeAccident as e:
            print(f"[Accident] {command}本应在栈下标为{e.args[0]}处接受一个{e.args[1].__name__}，而实际接受了{e.args[2]}")
        except NameAccident as e:
            print(f"[Accident] 未知符号：{command}")
        except IntrospectAccident as e:
            print("[Accident] 在绘制反思前未先绘制内省")
        except EvalAccident as e:
            pass  # 错误发生在元运行方式运行命令期间，直接传播
        else:
            return True
        return False

    def run_program(self, text):
        for cmd in split_command(text):
            print(f"{" " * 4 * self.introspect_level}run_program> {cmd}")
            if not self.run_command(cmd):
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

    def __str__(self):
        return self.name

    __repr__ = __str__


class Vector:
    def __init__(self, x, y, z):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __str__(self):
        return f"({self.x:.2f}, {self.y:.2f}, {self.z:.2f})"

    __repr__ = __str__


def start_repl(mind_stack: MindStack):
    while True:
        text = input(f"{" " * 4 * m.introspect_level}> ")
        m.run_program(text)


def run_file(mind_stack: MindStack, file_name: str):
    with open(file_name, encoding="utf-8") as f:
        text = f.read()
    mind_stack.run_program(text)


def split_command(text):
    pattern = r'[^\s,()]+|\(|\)'
    return re.findall(pattern, text)


if __name__ == '__main__':
    # start_repl()

    caster = Entity("caster", Vector(0, 0, 0), 1.8)
    m = MindStack(caster=caster)
    run_file(m, "画圆.hexparse")
    start_repl(m)

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
