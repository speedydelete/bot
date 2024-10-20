
'''defines a custom wrapper client on top of discord.py'''

from typing import Any, get_origin, get_args, Callable, Sequence
from types import UnionType, GenericAlias
from dataclasses import dataclass, MISSING, _MISSING_TYPE as MISSING_TYPE
from argparse import ArgumentParser
import discord


type type_ = type | UnionType | GenericAlias | None

def issubtype(value: Any, t: type_) -> bool:
    if t is None:
        return value is None
    elif isinstance(t, type | UnionType):
        return isinstance(value, t)
    else:
        if not isinstance(value, get_origin(t)):
            return False
        args = get_args(t)
        if len(args) == 1:
            for x in value:
                if not issubtype(x, args[0]):
                    return False
        else:
            if len(args) != len(value):
                return False
            return all(issubtype(x, u) for x, u in zip(value, args))
        return True

@dataclass
class Arg:
    '''argument for a command'''
    name: str | list[str] = ''
    action: str | MISSING_TYPE = MISSING
    n: int | MISSING_TYPE = MISSING
    val: Any = MISSING
    default: Any = MISSING
    t: type_ | MISSING_TYPE = MISSING
    choices: Sequence[Any] = []
    req: bool = True
    help: str | MISSING_TYPE = MISSING
    dest: str | MISSING_TYPE = MISSING
    deprecated: bool = False


@dataclass
class CmdSpec:
    '''spec for a command'''
    desc: str | None = None
    epilog: str | None = None
    help: bool = True
    abbr: bool = True
    prefix: str = '-'
    default: Any = None
    args: tuple[Arg] = tuple()

def get_type_checker(t: type_) -> Callable:
    def wrapper(value):
        return issubtype(value, t)
    return wrapper

def spec_to_parser(spec: CmdSpec) -> ArgumentParser:
    out = ArgumentParser()
    if spec.desc is not None:
        out.description = spec.desc
    if spec.epilog is not None:
        out.epilog = spec.epilog
    out.add_help = spec.help
    out.allow_abbrev = spec.abbr
    out.prefix_chars = spec.prefix
    out.argument_default = spec.default
    for arg in spec.args:
        kw = {}
        name = arg.name
        if isinstance(name, str):
            name = [name]
        if arg.action is not MISSING:
            kw['action'] = arg.action
        if arg.n is not MISSING:
            kw['nargs'] = arg.n
        if arg.val is not MISSING:
            kw['const'] = arg.val
        if arg.default is not MISSING:
            kw['default'] = arg.default
        if arg.t is not MISSING:
            kw['type'] = arg.t
        kw['req'] = arg.req
        if arg.help is not MISSING:
            kw['help'] = arg.help
        if arg.dest is not MISSING:
            kw['dest'] = arg.dest
        kw['deprecated'] = arg.deprecated
        out.add_argument(*arg.name, **kw)
    return out


class Client:

    '''custom version of discord.Client'''

    def __init__(self, client: discord.Client, prefix: str) -> None:
        self.client = client
        self.prefix = prefix
        self.commands: dict[str, ArgumentParser] = {}

    def add_command(self, name: str, parser_or_spec: ArgumentParser | CmdSpec):
        if isinstance(parser_or_spec, CmdSpec):
            parser = spec_to_parser(parser_or_spec)
        else:
            parser = parser_or_spec
        parser.prog = name
        self.commands[name] = parser
