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


#mibtree = Node("enterprises", ".1.3.6.1.4.1")

mibtree = Node("iso", ".1")
mibtree.add_subnode("org", "3").add_subnode("dod", "6").add_subnode("internet", "1").\
        add_subnode("private", "4").add_subnode("enterprises", "1")

name_waiting = None
mib_name = None
prev_line = None
more_needed = False

for line in sys.stdin:
    line = line.strip()
    if line == "" or line.startswith("--") or line.find(",") >= 0:
        continue
    if "DEFINITIONS" in line.split() and "BEGIN" in line.split():
        # "mibname DEFINITIONS ::= BEGIN"
        mib_name = line.split()[0]
        continue
    if line.find("MODULE-IDENTITY") > 0 or line.find("OBJECT-TYPE") > 0 or \
            line.find("NOTIFICATION-TYPE") > 0:
        # Looks for lines like "eventInformMsg OBJECT-TYPE"
        # Save the name and keep looping
        name_waiting = line.split()[0]
        continue
    if more_needed:
        line = prev_line + " " + line
        more_needed = False
    if line.find("OBJECT IDENTIFIER") >= 0:
        if line == "OBJECT IDENTIFIER":
            continue
        elif line.find(")") >= 0:
            continue
        elif line.find("::=") == -1:
            # We need to read more to find the assignment
            more_needed = True
            prev_line = line
            continue
        cols = line.split()
        name = cols[0]
        parent = cols[5]
        number = cols[6]
    elif name_waiting:
        if line.find("::=") == -1:
            continue
        name = name_waiting
        name_waiting = None
        cols = line.split()
        parent = cols[2]
        number = cols[3]
    else:
        continue
    #print("{} = {{ {} {} }}".format(name, parent, number))
    if find_node(mibtree, name):
        continue
    node = find_node(mibtree, parent)
    if node is None:
        print("Data error: parent {0} was not found for \"{1} = {{ {0} {2} }}\"".format(parent, name, number))
    else:
        node.add_subnode(name, number, mib_name)

print_list(mibtree)
