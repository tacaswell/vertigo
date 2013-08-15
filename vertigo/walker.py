from collections import OrderedDict

class Walker(object):
    '''Class to do depth-first walks of Graphs.

    To use Walker directly, pass in two functions matching these signatures:

    def pre_children(value, path, **kwargs):
        pass

    def post_children(value, path, children, pre_result, **kwargs):
        pass

    Invoking Walker.walk(node) will traverse the graph in depth-first order,
    keeping track of the path from the root of the graph to the current point.

    For each node, pre_children(node.value, path, **kwargs) will be invoked.
    Then, the Walker will recursively visit every child of node. Finally,
    post_children(node.value, path, child_results, pre_result, **kwargs) will be
    returned, where pre_result is the result of calling pre_children on this
    node and child_results is a dictionary mapping each child's key to the value
    returned by recursing on that child.

    The 'kwargs' arguments to walk() will be passed in to fn as fn(...,
    **kwargs).

    Note that this function does NOT check for cycles. Walking a cyclic graph
    will recurse infinitely.

    You can also subclass Walker and override the visit_pre_children() and
    visit_post_children() methods, which by default are simply overridden by the
    two parameters.

    '''
    def __init__(self, pre_children=None, post_children=None):
        if pre_children:
            self.visit_pre_children = pre_children
        if post_children:
            self.visit_post_children = post_children

    def walk(self, node, path=(), kwargs=None):
        if kwargs is None:
            kwargs = {}
        if isinstance(path, basestring):
            path = (path,)
        return self._walk(node, path, kwargs)

    def _walk(self, node, path, kwargs):
        pre_result = self.visit_pre_children(node.value, path, **kwargs)
        children = OrderedDict()
        for key, child in node.edge_iter():
            children[key] = self._walk(child, path+(key,), kwargs)
        return self.visit_post_children(node.value, path, children, pre_result, **kwargs)

    def visit_post_children(self, value, path, children, pre_val, **kwargs):
        return pre_val

    def visit_pre_children(self, value, path, **kwargs):
        return None

    def __call__(self, graph, path=(), **kwargs):
        return self.walk(graph, path, kwargs)


def walk(node, pre_children, post_children, path=None, kwargs=None):
    '''Walk a GraphNode, calling a function on each node.

    See the docs for Walker.
    '''
    return Walker(pre_children, post_children).walk(node, path, kwargs)

def top_down(fn):
    '''Decorator that turns a function into a top-down walker.

    The function should have the pre_children signature described in the docs
    for Walker.
    '''
    return Walker(pre_children=fn)

def bottom_up(fn):
    '''Decorator that turns a function into a bottom-up walker.

    The function should have the post_children signature described in the docs
    for Walker.
    '''
    return Walker(post_children=fn)

def test_walk():
    from graph import PlainGraphNode
    from cStringIO import StringIO

    @top_down
    def td_pformat(value, path, out_stream, indent=1):
        if path:
            line = u"{}{}:{}".format(' '*indent*len(path), path[-1], value)
        else:
            line = u"{}".format(value)
        out_stream.write(line+"\n")

    @bottom_up
    def bu_pformat(value, path, children, _, indent=1):
        if path:
            line = u"{}{}:{}".format(' '*indent*len(path), path[-1], value)
        else:
            line = u"{}".format(value)
        lines = [line] + list(children.values())
        return '\n'.join(lines)

    d = OrderedDict
    tree = PlainGraphNode.build(d([
        ('foo', d([
            ('bar', 'hi'),
            ('baz', 'ho'),
        ])),
        ('spam', d([
            ('eggs', 'poached'),
            ('bacon', 'fried'),
            ('_self', 'baked'),
        ]))
    ]))
    s = StringIO()
    td_pformat(tree, out_stream=s, indent=2)
    s.reset()
    td = s.read().strip()
    bu = bu_pformat(tree, indent=2)
    import textwrap
    assert bu == textwrap.dedent('''
        None
          foo:None
            bar:hi
            baz:ho
          spam:baked
            eggs:poached
            bacon:fried
    ''').strip()
    assert td.strip() == bu

if __name__ == '__main__':
    test_walk()


'''
Things to do:

A loop-detecting walker that can wrap any other walker and stops it from being
called on the same node twice.

A breadth-first walker

A hook for walkers to short-circuit (so that e.g. a comparison walker can stop
as soon as it finds anything that doesn't match)

'''
