import unittest

from BPlusTree.BplusTreeInMemory import bplustreeinmemory

class MyTestCase(unittest.TestCase):
    def test_insertandquery(self):
        order = 4
        tree = bplustreeinmemory(order)
        for i in range(1000):
            tree.insert(i, i)
            self.assertEqual(tree.get(i) == i, True)
            self.assertEqual(self.traverse(tree.root, order, tree.root), True)
        print ("hello")


    def traverse(self, node, order, root):
        min_degree = (order + 1)/2
        if not node or node == root:
            return True
        if node.is_leaf:
            return node.length >= min_degree
        if node.length < min_degree:
            return False
        for i in range(node.length + 1):
            if self.traverse(node.childs[i], order, root) == False:
                return False

        return True


    def test_delete(self):
        order = 4
        tree = bplustreeinmemory(order)

        num = 1000
        res = [i for i in range(num)]
        for i in range(num):
            tree.insert(i, i)
            self.assertEqual(tree.get(i) == i, True)
        print("insert finisth")

        for i in range(num):
            tree.delete(i)
            res.remove(i)
            vals = tree.values()
            correct = all([vals[k] == res[k] for k in range(len(vals))])
            self.assertEqual(correct, True)
            self.assertEqual(tree.get(i) == None, True)
            self.assertEqual(self.traverse(tree.root, order, tree.root), True)

        print("here")



if __name__ == '__main__':
    unittest.main()
