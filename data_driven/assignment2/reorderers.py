from tree import Tree
import sys

class Reorderer:
    def reorder(self, root):
        assert False, "Not implemented."

class RecursiveReorderer(Reorderer):
    def reorder(self, tree):
        return self.reorder_recursively(tree.root, [])

    def reorder_recursively(self, head, ordering):
        assert False, "TODO: implement this."
        # 1. Append leaf nodes to ordering.
        # 2. Call 'reorder_head_and_children' to reorder immediate subtree.
        # 3. Call this method recursively on children, adding head when reached.

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
        pass


class HeadFinalReorderer(RecursiveReorderer):
    def reorder_head_and_children(self, head):
        assert False, "Implement me to place head node last."


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
