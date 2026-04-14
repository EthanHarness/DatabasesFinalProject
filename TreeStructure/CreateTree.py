from __future__ import annotations
from enum import Enum
from typing import Any, List

class NodeType(Enum):
    OBJECT = 1
    ARRAY = 2
    KEY = 3
    LITERAL = 4

class Node:
    def __init__(self, label: str, type: NodeType):
        self.label = label
        self.type = type
        self.children = []

    def addChild(self, child: Node) -> Node:
        self.children.append(child)
        return child

    @staticmethod
    def recursivelyCreateNodeFromObjectLevel(key: str, label: dict|list|Any) -> Node:
        rt = Node(key, NodeType.KEY)
        
        if isinstance(label, dict):
            child = rt.addChild(Node(None, NodeType.OBJECT))
            for key in label:
                child.addChild(Node.recursivelyCreateNodeFromObjectLevel(key, label[key]))
            return rt
        
        if isinstance(label, list):
            child = rt.addChild(Node(None, NodeType.ARRAY))
            for val in label:
                child.addChild(Node.recursivelyCreateNodeFromArrayLevel(val))
            return rt
        
        child = rt.addChild(Node(label, NodeType.LITERAL))
        return rt

    @staticmethod
    def recursivelyCreateNodeFromArrayLevel(data: dict|list|Any) -> Node:
        if isinstance(data, dict):
            rt = Node(None, NodeType.OBJECT)
            for key in data:
                rt.addChild(Node.recursivelyCreateNodeFromObjectLevel(key, data[key]))
            return rt
        
        if isinstance(data, list):
            rt = Node(None, NodeType.ARRAY)
            for val in data:
                rt.addChild(Node.recursivelyCreateNodeFromArrayLevel(val))
            return rt
        
        return Node(data, NodeType.LITERAL)

class JsonTree:
    def __init__(self, docRoot: dict):
        self.root = Node(None, NodeType.OBJECT)

        for key in docRoot:
            self.root.addChild(Node.recursivelyCreateNodeFromObjectLevel(key, docRoot[key]))

    