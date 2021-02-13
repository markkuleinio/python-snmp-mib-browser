import re
import sys

class Node:
    def __init__(self, name, oid, mib_name=None):
        self.name = name
        if not mib_name:
            mib_name = "(unknown MIB)"
        self.mib_name = mib_name
        self.oid = oid
        self.subnodes = []

    def add_subnode(self, name, number, mib_name=None):
        subnode = Node(name, self.oid + "." + number, mib_name)
        self.subnodes.append(subnode)
        self.subnodes.sort(key=oid_sort_func)
        return subnode


def oid_sort_func(node):
    """Returns the last number in node's OID for sorting the subnodes"""
    try:
        return int(node.oid.split(".")[-1])
    except:
        return 0


def find_node(node, name):
    """Finds a node based on its name, returns Node"""
    if node.name == name:
        return node
    for subnode in node.subnodes:
        found_node = find_node(subnode, name)
        if found_node:
            return found_node
    return None


def print_list(node):
    print("{} = {}::{}".format(node.oid, node.mib_name, node.name))
    for subnode in node.subnodes:
        print_list(subnode)


mibtree = Node("iso", ".1", "(root)")

name_waiting = None
mib_name = None
prev_line = None
more_needed = False
imported_items = []
parsing_imports = False

imports = {}

for line in sys.stdin:
    line = line.strip()
    cols = line.split()
    if name_waiting:
        if "::=" not in line:
            continue
        name = name_waiting
        name_waiting = None
        match = re.search(r"::=\s*\{\s*([\w-]+)\s+([0-9]+)\s*\}", line)
        parent = match[1]
        number = match[2]
        # Added to the tree later below
    elif parsing_imports:
        words = re.split(r"[, ]+", line)
        i = 0
        while i < len(words):
            if words[i] != "FROM":
                if words[i]:
                    imported_items.append(words[i])
            else:
                imported_from = words[i+1]
                i += 1
                if imported_from.endswith(";"):
                    parsing_imports = False
                    imported_from = imported_from[:-1]
                for item in imported_items:
                    imports[item] = imported_from
                imported_items = []
            i += 1
        continue
    elif line == "" or line.startswith("--") or line.find(",") >= 0 or cols[0] == "SYNTAX":
        continue
    elif (
        len(cols) == 2 and cols[1] in [
            "OBJECT-IDENTITY",
            "OBJECT-TYPE",
            "MODULE-IDENTITY",
            "NOTIFICATION-TYPE",
        ]) or (
        len(cols) == 3 and cols[1] == "OBJECT" and cols[2] == "IDENTIFIER"
    ):
        # Save the name and keep looping
        name_waiting = cols[0]
        continue
    elif "DEFINITIONS" in cols and "::=" in cols and "BEGIN" in cols:
        # "mibname DEFINITIONS ::= BEGIN"
        mib_name = cols[0]
        continue
    elif more_needed:
        line = prev_line + " " + line
        more_needed = False
    elif line.find("OBJECT IDENTIFIER") >= 0:
        if line == "OBJECT IDENTIFIER":
            continue
        elif line.find(")") >= 0:
            continue
        elif line.find("::=") == -1:
            # We need to read more to find the assignment
            more_needed = True
            prev_line = line
            continue
        elif line.startswith("OBJECT IDENTIFIER"):
            # Let's take the previous line as well
            line = prev_line + " " + line
        match = re.search(r"([\w-]+)\s*OBJECT IDENTIFIER\s*::=\s*\{\s*([\w-]+)\s*([0-9]+)\s*\}", line)
        name = match[1]
        parent = match[2]
        number = match[3]
    elif line.startswith("IMPORTS"):
        imported_items = []
        parsing_imports = True
        words = re.split(r"[, ]+", line)
        if len(words) == 1:
            continue
        i = 1   # Skip the first word "IMPORTS"
        while i < len(words):
            if words[i] != "FROM":
                imported_items.append(words[i])
            else:
                imported_from = words[i+1]
                i += 1
                if imported_from.endswith(";"):
                    parsing_imports = False
                    imported_from = imported_from[:-1]
                for item in imported_items:
                    imports[item] = imported_from
                imported_items = []
            i += 1
        continue
    else:
        prev_line = line
        continue
    #print("{} = {{ {} {} }}".format(name, parent, number))
    if find_node(mibtree, name) or parent == "0":
        continue
    node = find_node(mibtree, parent)
    if node is None:
        if parent in imports:
            print("Missing input: MIB file for {} is needed for resolving \"{} = {{ {} {} }}\"".format(imports[parent], name, parent, number))
        else:
            print("Missing input: parent {0} was not found for \"{1} = {{ {0} {2} }}\"".format(parent, name, number))
    else:
        node.add_subnode(name, number, mib_name)

print_list(mibtree)
