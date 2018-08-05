import re

from DublinCore import Type


class Element:
    def __init__(self, typ: Type, value=""):
        self.typ = typ
        self.value = value

    def replace_value(self, search: str, replace: str, use_regex: bool = False):
        if use_regex:
            self.value = re.sub(search, replace, self.value)
        else:
            self.value = self.value.replace(search, replace)
