from bisect import bisect_right
## todo check the code, optimize the code ,and then test the code tomorrow
class node:
    def __init__(self, order, is_leaf):
        self.keys = [None] * (order)
        self.is_leaf = is_leaf
        if not self.is_leaf:
            ## we preserve extra one slot for programming simply
            self.childs = [None] * (order + 1)
        else:
            self.childs = None

        self.length = 0

        self.values = None
        if self.is_leaf:
            self.values = [None] * (order + 1)

        self.next = None


class bplustreeinmemory:
    def __init__(self, order):
        self.root = None
        self.order = order
        self.min_key_nums = (self.order + 1) / 2 - 1
        self.max_key_nums = self.order - 1
        self.leaf_head = None

    def __init_root(self, order):
        if self.root:
            return self.root

        return self.create_leaf_node(order)


    def create_internal_node(self, order):
        return node(order, False)

    def create_leaf_node(self, order):
        return node(order, True)


    def insert(self, key, val):
        if not self.root:
            self.root = self.__init_root(self.order)
            self.root.keys[0] = key
            self.root.values[0] = val
            self.root.length += 1
            self.leaf_head = self.root
        else:
            self.__insert(key, val, self.root, None)
            if self.root.length >= self.order:
                new_root = self.create_internal_node(self.order)
                new_root.childs[0] = self.root
                self.root = new_root

                self.__split_node(self.root, 0)


    def __insert_into_leaf(self, key, val, node, parent):
        inserted_idx = self.__get_inserted_index(key, node)
        self.__shift_keys_values_right(node, inserted_idx)
        node.keys[inserted_idx] = key
        node.values[inserted_idx] = val
        node.length += 1


    ## need to split node
    def __insert(self, key, val, node, parent):
        if node.is_leaf:
            self.__insert_into_leaf(key, val, node, parent)
        else:
            inserted_idx = self.__get_inserted_index(key, node)
            child = node.childs[inserted_idx]
            self.__insert(key, val, child, node)

            if child.length >= self.order:
                self.__split_node(node, inserted_idx)

    def __split_node(self, parentnode, inserted_idx):
        child = parentnode.childs[inserted_idx]
        right_node = self.__create_right_node(parentnode, inserted_idx)

        mid = (self.order + 1) / 2
        child.length = mid
        ## buble the middle one up to the parent
        self.__shift_keys_values_right(parentnode, inserted_idx)
        self.__shift_childs_right(parentnode, inserted_idx + 1)

        parentnode.keys[inserted_idx] = child.keys[mid]
        parentnode.length += 1
        parentnode.childs[inserted_idx + 1] = right_node

        ## link
        if child.is_leaf:
            child_next = child.next
            child.next = right_node
            right_node.next = child_next


    def __shift_keys_values_right(self, node, idx):
        for i in range(node.length - 1, idx - 1, -1):
            node.keys[i + 1] = node.keys[i]

        if node.is_leaf:
            for i in range(node.length - 1, idx - 1, -1):
                node.values[i + 1] = node.values[i]

    def __shift_childs_right(self, node, idx):
        for i in range(node.length, idx - 1, -1):
            node.childs[i + 1] = node.childs[i]


    def __create_right_node(self,  parentnode, inserted_idx):
        mid = (self.order + 1) / 2
        child = parentnode.childs[inserted_idx]

        right_node = node(self.order, child.is_leaf)
        l = 0
        for i in range(mid, child.length):
            right_node.keys[l] = child.keys[i]
            if right_node.is_leaf:
                right_node.values[l] = child.keys[i]
            right_node.length += 1
            l += 1

        if not right_node.is_leaf:
            l = 1
            for i in range(mid + 1, child.length + 1):
                right_node.childs[l] = child.childs[i]
                l += 1

        return right_node


    def delete(self, key):
        deleted_idx = self.__find_delete_idx(key, self.root)

        self.__delete(key, self.root, None,  deleted_idx)
        if self.root.length == 0:
            self.root = None if self.root.is_leaf else self.root.childs[0]
        return


    def __delete(self, key, node, parent, idx):
        if node.is_leaf:
            if node.length <= self.min_key_nums and parent != None:
                self.__borrow_or_merge(node, parent, idx)

            self.__delete_from_leaf_node(key, node)
        else:
            delete_idx = self.__find_delete_idx(key, node)
            idx =delete_idx ## todo looks strange here
            child = node.childs[delete_idx]
            self.__delete(key, child, node, delete_idx)

            if node.length < self.min_key_nums and parent != None :
                self.__borrow_or_merge(node, parent, idx)
                ## if the root has been deleted, change the root

    def __borrow_or_merge(self, node, parent, idx):
        if idx - 1 >= 0 and parent.childs[idx - 1].length >= self.min_key_nums + 1:
            ## borrow from the left
            self.__borrow_from_left(node, parent, idx)
        elif idx + 1 <= parent.length and parent.childs[idx + 1].length >= self.min_key_nums + 1:
            ## borrow from the right
            self.__borrow_from_right(node, parent, idx)
        else:
            ##merge
            if idx - 1 >= 0:
                self.__merge(parent, idx)
            else:
                self.__merge(parent, idx + 1)

    def __borrow_from_left(self, node, parent, idx):
        lchild = parent.childs[idx - 1]

        borrow_key, borrow_val, borrow_child = lchild.keys[lchild.length - 1], lchild.values[lchild.length - 1], lchild.childs[lchild.length]
        lchild.length -= 1

        self.__shift_keys_values_right(node, 0)
        self.__shift_childs_right(node, 0)
        node.keys[0] = borrow_key
        if node.is_leaf:
            node.values[0] = borrow_val
        node.childs[0] = borrow_child

        node.length += 1

        parent.keys[idx - 1] = borrow_key

    def values(self):
        val = []

        node = self.leaf_head
        while node:
            val.extend([node.values[i] for i in range(node.length)])
            node = node.next

        return val

    def __borrow_from_right(self, node, parent, idx):
        rchild = parent.childs[idx + 1]
        borrow_key, borrow_val, borrow_child= rchild.keys[0], None if not rchild.values else rchild.values[0], None if rchild.is_leaf else rchild.childs[1]

        self.__shift_keys_values_left(rchild, 1)
        self.__shift_child_left(rchild, 2)
        rchild.length -= 1

        node.keys[node.length] =borrow_key
        if node.is_leaf:
            node.values[node.length] = borrow_val
        node.length += 1
        if not node.is_leaf:
            node.childs[node.length] = borrow_child

        parent.keys[idx] = rchild.keys[0]


    def __merge(self, parent, idx):
        lchild = parent.childs[idx - 1]
        rchild = parent.childs[idx]

        self.__shift_keys_values_left(parent, idx)
        self.__shift_child_left(parent, idx + 1)
        parent.length -= 1
        self.__append(lchild, rchild)
        if lchild.is_leaf:
            lchild.next = rchild.next

    def __append(self, node, appendnode):
        l = node.length

        for i in range(appendnode.length):
            node.keys[l] = appendnode.keys[i]
            if node.is_leaf:
                node.values[l] = appendnode.values[i]
            if not node.is_leaf:
                node.childs[l + 1] = appendnode.childs[i + 1]
            l += 1

        node.length = l

    def __shift_keys_values_left(self, node, idx):
        for i in range(idx, node.length):
            node.keys[i - 1] = node.keys[i]
            if node.is_leaf:
                node.values[i - 1] = node.values[i]

    def __shift_child_left(self, node, idx):
        if node.is_leaf:
            return
        for i in range(idx, node.length + 1):
            node.childs[i - 1] = node.childs[i]

    def __delete_from_leaf_node(self, key, node):
        deleted_idx = self.__find_delete_idx(key, node)
        self.__shift_keys_values_left(node, deleted_idx)
        node.length -= 1


    def __find_delete_idx(self, key, node):
        return bisect_right(node.keys, key, 0, node.length)

    def get(self, key):
        return self.__get(key, self.root)

    def __get(self, key, node):
        if not node:
            return None

        if node.is_leaf:
            return self.__get_from_leaf(key, node)

        idx = bisect_right(node.keys,key, 0, node.length)

        return self.__get(key, node.childs[idx])

    def __get_inserted_index(self, key, node):
        return bisect_right(node.keys, key, 0, node.length)

    def __get_from_leaf(self, key, node):
        idx = bisect_right(node.keys, key, 0, node.length)
        if 0 <= idx - 1 < node.length:
            return node.values[idx - 1]

        return None