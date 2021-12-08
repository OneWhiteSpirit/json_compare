from __future__ import annotations

from argparse import ArgumentParser
from enum import Enum
from json import load as json_load
from pathlib import Path


class NodeChangeType(Enum):
    Unchanged = 1,
    Inserted = 2,
    Deleted = 3,
    Updated = 4


class TreeNode:
    def __init__(self, data: object) -> None:
        self.data = data
        self.children = dict()
        self.node_type = NodeChangeType.Unchanged

    def add_child(self, obj: TreeNode) -> None:
        if isinstance(obj.data, list):
            for k in obj.data:
                self.children[k] = obj
        else:
            self.children[obj.data] = obj

    @property
    def is_root(self) -> bool:
        if str(self.data).lower() == 'root':
            return True
        else:
            return False

    def __str__(self, level: int = 0) -> str:
        ret = ''
        if self.node_type != NodeChangeType.Unchanged:
            ret = '\t' * level + repr(self.data) + \
                ' - (' + self.node_type.name + ')' + '\n\n'
        for data, child in self.children.items():
            ret += child.__str__(level + 1)
        return ret

    def __repr__(self) -> str:
        return self.__str__()


def change_node_type(type: NodeChangeType, node: TreeNode) -> None:
    node.node_type = type
    for data, child in node.children.items():
        change_node_type(type, child)


def make_inserted(node: TreeNode) -> None:
    change_node_type(NodeChangeType.Inserted, node)


def make_deleted(node: TreeNode) -> None:
    change_node_type(NodeChangeType.Deleted, node)


def make_updated(node: TreeNode) -> None:
    change_node_type(NodeChangeType.Updated, node)


def diff(oldNode: TreeNode, newNode: TreeNode) -> TreeNode:
    if not oldNode or not newNode:
        raise ValueError('Must have at least one node to compare.')

    old_ndata = oldNode.children.keys()
    new_ndata = newNode.children.keys()
    left_diff = old_ndata - new_ndata
    right_diff = new_ndata - old_ndata
    intersection = old_ndata & new_ndata

    if left_diff:
        for k in left_diff:
            make_deleted(oldNode.children[k])
        if not oldNode.is_root and not oldNode.children:
            return oldNode
    if right_diff:
        for k in right_diff:
            oldNode.children[k] = newNode.children[k]
            make_inserted(oldNode.children[k])
        if not oldNode.is_root and not oldNode.children:
            return oldNode
    if intersection:
        for node1, node2 in [(oldNode.children[k], newNode.children[k]) for k in intersection]:
            oldNode.children[node1.data] = diff(node1, node2)

    return oldNode


def make_tree(json: dict, parent: TreeNode) -> None:
    for key in json:
        if isinstance(json[key], dict):
            node = TreeNode(key)
            make_tree(json[key], node)
        elif isinstance(json[key], list):
            node = TreeNode(key)
            for item in json[key]:
                if isinstance(item, dict):
                    make_tree(item, node)
                elif isinstance(item, list):
                    for k in item:
                        make_tree(k, node)
        else:
            node = TreeNode(key)
            node.add_child(TreeNode(json[key]))
        parent.add_child(node)


def create_tree_from_JSON(json: dict) -> TreeNode:
    tree = TreeNode("root")
    make_tree(json, tree)
    return tree


def main(args: list) -> TreeNode:
    parser = ArgumentParser(description='Two JSON comparer')
    parser.add_argument('json_first', type=str,
                        help='A required JSON path of the first file argument')
    parser.add_argument('json_second', type=str,
                        help='A required JSON path of the second file argument')

    if not args:
        raise RuntimeError("Two arguments with JSON paths are expected")

    args = parser.parse_args(args)

    tree1: TreeNode = None
    tree2: TreeNode = None
    if Path(args.json_first).exists() or Path(args.json_second).exists():
        jfile1 = open(args.json_first, 'r')
        jfile2 = open(args.json_second, 'r')
        data1 = json_load(jfile1)
        data2 = json_load(jfile2)
        if data1 and data2:
            tree1 = create_tree_from_JSON(data1)
            tree2 = create_tree_from_JSON(data2)
    else:
        raise FileNotFoundError("Not valid paths to the JSONs")

    if tree1 and tree2:
        diffs = diff(tree1, tree2)
        print(diffs)
        return diffs
    else:
        return None


if __name__ == '__main__':
    from sys import argv
    main(argv[1:])
