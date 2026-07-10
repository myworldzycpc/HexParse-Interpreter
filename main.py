import re
from abc import ABC, abstractmethod
from typing import Callable, Collection


class Accident(Exception): pass


class IndexAccident(Accident): pass


class TypeAccident(Accident): pass


class NameAccident(Accident): pass


class MindStack:
    def __init__(self, caster: Entity):
        self.stack = []
        self.caster = caster

    def push(self, *item, from_=None):
        if from_ is not None:
            print(f"~ {from_}")

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
            return removed
        raise IndexAccident(count)

    def run_command(self, command):
        try:
            match command:
                case '/stack':
                    print(self.stack)
                case 'print':
                    value = self.pop(object)
                    print(f"[print] {value}")
                    self.push(value)
                case 'get_caster':
                    self.push(self.caster)
                case 'entity_pos/eye':
                    entity: Entity = self.pop(Entity)[0]
                    self.push(entity.pos + Vector(0, entity.eye_height, 0), from_=entity)
                case 'entity_pos/foot':
                    entity: Entity = self.pop(Entity)[0]
                    self.push(entity.pos, from_=entity)
                case 'const/true':
                    self.push(True)
                case 'const/false':
                    self.push(False)
                case 'if':
                    condition, then, else_ = self.pop(bool, object, object)
                    if condition:
                        self.push(then, from_=(condition, then, else_))
                    else:
                        self.push(else_, from_=(condition, then, else_))
                case _ if re.match("num_.*", command):
                    self.push(float(command.lstrip("num_")))
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
            print(f"")
        else:
            return True


class Entity:
    def __init__(self, name, pos: Vector, eye_height: float):
        self.name = name
        self.pos = pos
        self.eye_height = eye_height

    def ray_cast_entity(self):
        return None

    def __str__(self):
        return self.name


class Vector:
    def __init__(self, x, y, z):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __str__(self):
        return f"({self.x:.2f}, {self.y:.2f}, {self.z:.2f})"


def start_repl():
    caster = Entity("caster", Vector(0, 0, 0), 1.8)
    m = MindStack(caster=caster)
    while True:
        text = input("> ")
        for cmd in split_command(text):
            m.run_command(cmd)


def split_command(text):
    result = list(filter(bool, re.split(r'[, \t\n]+', text)))
    return result


if __name__ == '__main__':
    start_repl()
