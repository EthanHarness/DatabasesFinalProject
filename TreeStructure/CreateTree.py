from __future__ import annotations
from enum import Enum
from typing import Any
from collections import deque

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
        
        self.offset = None

    def addChild(self, child: Node) -> Node:
        self.children.append(child)
        return child
    
    def nodeToString(self) -> str:
        return f"Label: {self.label} ------ Type: {self.type}"
    
    def setOffset(self, offset: int) -> None:
        self.offset = offset

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
        self.size = 0
        self.degree = 0
        self.height = 0


        for key in docRoot:
            self.root.addChild(Node.recursivelyCreateNodeFromObjectLevel(key, docRoot[key]))
        
        self.computeStats()

    def computeStats(self):
        self.computeStatsBFS()
        self.height = self.computeStatsDFS(self.root)

    def computeStatsBFS(self):
        queue = deque([self.root])
        count = 0
        maxDegree = 0

        while queue:
            currentNode = queue.popleft()
            currentNode.setOffset(count)
            count += 1
            maxDegree = max(len(currentNode.children), maxDegree)

            if len(currentNode.children) != 0:

                for child in currentNode.children:
                    queue.append(child)

        self.degree = maxDegree
        self.size = count

    def computeStatsDFS(self, root: Node):
        if len(root.children) == 0: return 1

        maxHeight = 1
        for child in root.children:
            temp = self.computeStatsDFS(child)
            maxHeight = max(maxHeight, temp)

        return maxHeight + 1
    
    def printTreeBFS(self):
        queue = deque([self.root])

        while queue:
            currentNode = queue.popleft()
            print(currentNode.nodeToString())

            if len(currentNode.children) != 0:
                for child in currentNode.children:
                    queue.append(child)

    @staticmethod
    def findIthChild(childNumber: int, root: Node) -> Node:
        if len(root.offset) == childNumber: return root
        if len(root.children) == 0: return root

        for child in root.children:
            potential = JsonTree.findIthChild(childNumber, child)
            if potential.offset == childNumber: return potential

        return root
    