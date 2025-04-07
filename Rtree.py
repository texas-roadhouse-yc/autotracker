import matplotlib.pyplot as plt
import matplotlib.patches as patches

class Rectangle:
    def __init__(self, x_min, y_min, x_max, y_max, data=None, heading=0.0, coor=(0.0, 0.0)):
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max
        self.data = data  # Extra information stored in a dictionary
        self.heading = heading  # Newly added float attribute
        self.coor = coor  # Coordinate attribute

    def __repr__(self):
        return (f"Rectangle(({self.x_min}, {self.y_min}), ({self.x_max}, {self.y_max}), "
                f"data={self.data}, heading={self.heading}, coor={self.coor})")

    def intersects(self, other):
        return not (self.x_max < other.x_min or self.x_min > other.x_max or
                    self.y_max < other.y_min or self.y_min > other.y_max)

    def contains(self, other):
        return (self.x_min <= other.x_min and self.x_max >= other.x_max and
                self.y_min <= other.y_min and self.y_max >= other.y_max)

    def enlarge(self, other):
        self.x_min = min(self.x_min, other.x_min)
        self.y_min = min(self.y_min, other.y_min)
        self.x_max = max(self.x_max, other.x_max)
        self.y_max = max(self.y_max, other.y_max)


class Node:
    def __init__(self, is_leaf=True):
        self.is_leaf = is_leaf
        self.children = []
        self.bounding_box = None
        self.data_dict = {}  # Dictionary to store data in leaf nodes

    def __repr__(self):
        if self.is_leaf:
            return f"LeafNode(children={self.children}, data_dict={self.data_dict})"
        return f"InnerNode(bounding_box={self.bounding_box}, children={self.children})"


class RTree:
    def __init__(self, max_entries=4):
        self.root = Node()
        self.max_entries = max_entries

    def insert(self, rectangle, data=None, heading=0.0, coor=(0.0, 0.0)):
        leaf = self._choose_leaf(self.root, rectangle)
        rectangle.data = data
        rectangle.heading = heading  # Set heading attribute
        rectangle.coor = coor        # Set coor attribute
        leaf.children.append(rectangle)
        if data or heading or coor:
            # Store heading and data in the dictionary
            leaf.data_dict[repr(rectangle)] = {"data": data, "heading": heading, "coor": coor}
        if len(leaf.children) > self.max_entries:
            self._split_node(leaf)
        self._update_bounding_boxes(self.root)

    def search(self, search_rect):
        results = []
        self._search_helper(self.root, search_rect, results)
        return results

    def delete(self, rectangle):
        deleted = self._delete_helper(self.root, rectangle)
        if deleted:
            self._update_bounding_boxes(self.root)
        return deleted

    def _choose_leaf(self, node, rectangle):
        if node.is_leaf:
            return node
        best_choice = None
        min_enlargement = float('inf')
        for child in node.children:
            enlargement = self._get_enlargement(child.bounding_box, rectangle)
            if enlargement < min_enlargement:
                min_enlargement = enlargement
                best_choice = child
        return self._choose_leaf(best_choice, rectangle)

    def _get_enlargement(self, bbox, rectangle):
        enlarged_bbox = Rectangle(bbox.x_min, bbox.y_min, bbox.x_max, bbox.y_max)
        enlarged_bbox.enlarge(rectangle)
        original_area = (bbox.x_max - bbox.x_min) * (bbox.y_max - bbox.y_min)
        enlarged_area = (enlarged_bbox.x_max - enlarged_bbox.x_min) * (enlarged_bbox.y_max - enlarged_bbox.y_min)
        return enlarged_area - original_area

    def _split_node(self, node):
        node.is_leaf = False
        mid = len(node.children) // 2
        node1 = Node(is_leaf=True)
        node2 = Node(is_leaf=True)
        node1.children = node.children[:mid]
        node2.children = node.children[mid:]
        node.children = [node1, node2]

    def _update_bounding_boxes(self, node):
        if node.is_leaf:
            node.bounding_box = self._get_bounding_box(node.children)
        else:
            for child in node.children:
                self._update_bounding_boxes(child)
            node.bounding_box = self._get_bounding_box([child.bounding_box for child in node.children])

    def _get_bounding_box(self, rectangles):
        if not rectangles:
            return None
        x_min = min(rect.x_min for rect in rectangles)
        y_min = min(rect.y_min for rect in rectangles)
        x_max = max(rect.x_max for rect in rectangles)
        y_max = max(rect.y_max for rect in rectangles)
        return Rectangle(x_min, y_min, x_max, y_max)

    def _search_helper(self, node, search_rect, results):
        if node.is_leaf:
            for child in node.children:
                if search_rect.intersects(child):
                    results.append(child)
        else:
            for child in node.children:
                if search_rect.intersects(child.bounding_box):
                    self._search_helper(child, search_rect, results)

    def _delete_helper(self, node, rectangle):
        if node.is_leaf:
            if rectangle in node.children:
                node.children.remove(rectangle)
                node.data_dict.pop(repr(rectangle), None)  # Remove corresponding dictionary entry
                return True
            return False
        for child in node.children:
            if self._delete_helper(child, rectangle):
                if not child.children:  # Clean up empty nodes
                    node.children.remove(child)
                return True
        return False

    def visualize(self):
        fig, ax = plt.subplots(figsize=(20, 10))
        self._visualize_node(self.root, ax)
        plt.axis('equal')
        plt.show()

    def _visualize_node(self, node, ax, color="blue"):
        if node.bounding_box:
            rect = node.bounding_box
            ax.add_patch(
                patches.Rectangle(
                    (rect.x_min, rect.y_min),
                    rect.x_max - rect.x_min,
                    rect.y_max - rect.y_min,
                    linewidth=1,
                    edgecolor=color,
                    facecolor='none'
                )
            )
        if node.is_leaf:
            for child in node.children:
                rect = child
                ax.add_patch(
                    patches.Rectangle(
                        (rect.x_min, rect.y_min),
                        rect.x_max - rect.x_min,
                        rect.y_max - rect.y_min,
                        linewidth=1,
                        edgecolor="green",
                        facecolor='none'
                    )
                )
        else:
            for child in node.children:
                self._visualize_node(child, ax, color="red")
