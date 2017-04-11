import sys
from tree import Tree


class Reorderer:
    def __init__(self):
        pass

    def reorder(self, tree):
        pass


class RecursiveReorderer(Reorderer):
    def reorder(self, tree):
        return self.reorder_recursively(tree.root, [])

    def reorder_recursively(self, head, ordering):
        # 1. Append leaf nodes to ordering.
        if not head.children:
            ordering.append(head)
            return ordering

        # 2. Call 'reorder_head_and_children' to reorder immediate subtree.
        # 3. Call this method recursively on children, adding head when reached.
        for node in self.reorder_head_and_children(head):
            if node == head:
                ordering.append(node)
            else:
                ordering = self.reorder_recursively(node, ordering)

        return ordering

    def reorder_head_and_children(self, head):
        # Reorder the head and children in the desired order.
        assert False, "TODO: implement me in a subclass."


class DoNothingReorderer(RecursiveReorderer):
    # Just orders head and child nodes according to their original index.
    def reorder_head_and_children(self, head):
        all_nodes = (
            [(child.index, child) for child in head.children] + [(head.index, head)])
        return [node for index, node in sorted(all_nodes)]


class ReverseReorderer(RecursiveReorderer):
    # Reverse orders head and child nodes according original index
    def reorder_head_and_children(self, head):
        all_nodes = (
            [(-child.index, child) for child in head.children] + [(head.index, head)])
        return [node for index, node in sorted(all_nodes)]

class HeadFinalReorderer(RecursiveReorderer):
    def reorder_head_and_children(self, head):
        children = [node for index, node in sorted([(child.index, child) for child in head.children])]
        return children + [head]


class MyReorderer(RecursiveReorderer):
    def reorder_head_and_children(self, head):
        children = [node for index, node in sorted([(child.index, child) for child in head.children])]

        aux_indices = []
        auxs = []
        for idx, node in enumerate(children):
            if node.label.startswith("aux"):  # aux or auxpass
                aux_indices.append(idx)
                auxs.append(node)
        for i, aux_idx in enumerate(aux_indices):
            del children[aux_idx - i]

        first_prep_after_head_idx = None
        for idx, node in enumerate(children):
            if node.word in "().,;!?" and node.index > head.index:
                first_prep_after_head_idx = idx
                break

        if first_prep_after_head_idx is None:
            return children + [head] + auxs
        else:
            ordering = children[:first_prep_after_head_idx] + [head] + auxs + children[first_prep_after_head_idx:]
            return ordering

if __name__ == "__main__":
    if not len(sys.argv) == 3:
        print "python reorderers.py ReordererClass parses"
        sys.exit(0)
    # Instantiates the reorderer of this class name.
    reorderer = eval(sys.argv[1])()

    # Reorders each input parse tree and prints words to std out.
    for line in open(sys.argv[2]):
        t = Tree(line)
        assert t.root
        reordering = reorderer.reorder(t)
        print ' '.join([node.word for node in reordering if node != t.root])
