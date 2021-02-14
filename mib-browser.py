import argparse
import re
from pathlib import Path
from typing import List, Optional


class RawMibItem:

    def __init__(self, name: str, parent: str, index: int):
        self.name: str = name
        self.parent: str = parent
        self.index: int = index


class RawMib:

    def __init__(self, mibname: str):
        self.name: str = mibname
        self.items: List[RawMibItem] = []

    def add_item(self, name: str, parent: str, index: int):
        self.items.append(RawMibItem(name, parent, index))


class Node:
    def __init__(self, name, oid, mib_name=None):
        self.name = name
        if not mib_name:
            mib_name = "(unknown MIB)"
        self.mib_name = mib_name
        self.oid = oid
        self.subnodes = []

    def add_subnode(self, name, number, mib_name=None):
        subnode = Node(name, self.oid + "." + str(number), mib_name)
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


all_mibs: List[RawMib] = []
all_mib_files: dict = {}
missing_imports = {}
missed_mibs = []


def load_mib_by_name(mib_name: str):
    if mib_name not in all_mib_files:
        global missed_mibs
        if mib_name not in missed_mibs:
            print(f"MIB '{mib_name}' not found")
            missed_mibs.append(mib_name)
        return False
    mib = None
    name_waiting = None
    prev_line = None
    more_needed = False
    imported_items = []
    parsing_imports = False
    global all_mibs
    imports = {}

    with open(all_mib_files[mib_name]) as input_file:
        for line in input_file:
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
                if mib:
                    all_mibs.append(mib)
                mib = RawMib(mib_name)
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
            mib.add_item(name, parent, int(number))
    if mib:
        global missing_imports
        for item, mib_name in imports.items():
            if not load_mib_by_name(mib_name):
                missing_imports[item] = mib_name
        all_mibs.append(mib)
    return True


def get_mib_name_from_file(path: Path) -> Optional[str]:
    """Returns the MIB name from the MIB file."""
    with open(path) as f:
        try:
            for line in f:
                line = line.strip()
                match = re.search(r"^([\w-]+)\s+DEFINITIONS\s*::=\s*BEGIN", line)
                if match:
                    return match[1]
        except UnicodeDecodeError:
            return None
    return None


def get_all_mibs(path: Path):
    """Returns all MIB names with their file names."""
    mib_files: dict = {}
    for p in path.glob("*"):
        if p.is_file():
            mib_name = get_mib_name_from_file(p)
            if mib_name:
                mib_files[mib_name] = p
        elif p.is_dir():
            mib_files.update(get_all_mibs(p))
    return mib_files


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mib_name",
        metavar="mibname",
        help="The name of the MIB to be shown",
    )
    parser.add_argument(
        "-a", "--add",
        metavar="path(s)",
        help="Add given path(s) (comma-separated) to MIB search list",
        dest="add_paths",
        required=False,
    )
    parser.add_argument(
        "-n", "--no-default",
        help="Do not use the default MIB search path",
        required=False,
        action="store_true",
    )
    args = parser.parse_args()
    searchpath = [] if args.no_default else ["/var/lib/snmp/mibs"]
    if args.add_paths:
        searchpath += args.add_paths.split(",")
    global all_mib_files
    for path in searchpath:
        all_mib_files.update(get_all_mibs(Path(path)))

    load_mib_by_name(args.mib_name)

    mibtree = Node("iso", ".1", "(root)")
    missing_items = set()
    for mib in all_mibs:
        for item in mib.items:
            if find_node(mibtree, item.name) or item.parent == "0":
                continue
            node = find_node(mibtree, item.parent)
            if node is None:
                if item.parent in missing_items:
                    missing_items.add(item.name)
                elif item.parent in missing_imports:
                    print("Missing input: MIB file for {} is needed for resolving \"{} = {{ {} {} }}\" (and others in the same tree)".format(
                        missing_imports[item.parent], item.name, item.parent, item.index,
                    ))
                    missing_items.add(item.name)
                else:
                    print("Missing input: parent {0} was not found for \"{1} = {{ {0} {2} }}\"".format(
                        item.parent, item.name, item.index,
                    ))
            else:
                node.add_subnode(item.name, item.index, mib.name)

    print_list(mibtree)


if __name__ == "__main__":
    main()
