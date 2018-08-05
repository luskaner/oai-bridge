from DublinCore import Element, Type


class ElementList:
    def __init__(self):
        self.elements = []

    def add(self, element: Element):
        self.elements.append(element)
        return element

    def remove(self, element: Element):
        self.elements.remove(element)
        return element

    def replace_first_value_of_type(self, typ: Type, search: str, replace: str, use_regex: bool = False):
        el: Element = self.get_first_of_type(typ)
        if el:
            el.replace_value(search, replace, use_regex)

    def replace_all_values_of_type(self, typ: Type, search: str, replace: str, use_regex: bool = False):
        for el in self.get_all_of_type(typ):
            el.replace_value(search, replace, use_regex)

    def set_first_value_of_type(self, typ: Type, value: str):
        el = self.get_first_of_type(typ)
        if el:
            el.value = value

    def set_all_values_of_type(self, typ: Type, value: str):
        for el in self.get_all_of_type(typ):
            el.value = value

    def get_first_of_type(self, typ: Type):
        for el in self.elements:
            if el.typ == typ:
                return el

    def get_all_of_type(self, typ: Type):
        for el in self.elements:
            if el.typ == typ:
                yield el

    def remove_all_of_type(self, typ: Type):
        self.elements = [el for el in self.elements if el.typ != typ]

    def rename_elements(self, search_type: Type, replace_type: Type):
        for el in self.elements:
            if el.typ == search_type:
                el.typ = replace_type
