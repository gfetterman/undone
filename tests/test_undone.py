import collections
import functools
import pytest
import undone

def test_reversible():
    resource = [4]
    def add_one(r):
        r.append(1)
    def remove_one(r):
        try:
            r.pop()
        except IndexError:
            pass
    Revop = collections.namedtuple("Revop", ["do", "undo"])
    adding_one = Revop(functools.partial(add_one, r=resource),
                       functools.partial(remove_one, r=resource))
    stack = undone.ReversibleUndoStack()
    stack.do(adding_one)
    assert resource == [4 ,1]
    stack.do(adding_one)
    assert resource == [4, 1, 1]
    stack.undo()
    assert resource == [4, 1]
    stack.undo()
    assert resource == [4]
    with pytest.raises(IndexError):
        stack.undo()
    stack.redo()
    assert resource == [4, 1]
    stack.redo()
    assert resource == [4, 1, 1]
    with pytest.raises(IndexError):
        stack.redo()
    stack.undo()
    assert resource == [4, 1]
    assert stack.done == [adding_one]
    assert stack.undone == [adding_one]
    adding_two = Revop(functools.partial(lambda r: r.append(2), r=resource),
                       functools.partial(remove_one, r=resource))
    stack.do(adding_two)
    assert resource == [4, 1, 2]
    assert stack.done == [adding_one, adding_two]
    assert stack.undone == []

def test_regenerating():
    resource = [4]
    def add_one(r):
        r.append(1)
    stack = undone.RegeneratingUndoStack(initial_state=resource)
    stack.do(add_one)
    assert stack.current_state == [4 ,1]
    # if resource is a mutable object, resource and current_state become
    # decoupled
    assert resource == [4]
    stack.do(add_one)
    assert stack.current_state == [4, 1, 1]
    stack.undo()
    assert stack.current_state == [4, 1]
    stack.undo()
    assert stack.current_state == [4]
    with pytest.raises(IndexError):
        stack.undo()
    stack.redo()
    assert stack.current_state == [4, 1]
    stack.redo()
    assert stack.current_state == [4, 1, 1]
    with pytest.raises(IndexError):
        stack.redo()
    stack.undo()
    assert stack.current_state == [4, 1]
    assert stack.done == [add_one]
    assert stack.undone == [add_one]
    def add_two(r):
        r.append(2)
    stack.do(add_two)
    assert stack.current_state == [4, 1, 2]
    assert stack.done == [add_one, add_two]
    assert stack.undone == []

def test_snapshot():
    resource = [4]
    stack = undone.SnapshotUndoStack(resource)
    assert stack.initial_state == [4]
    assert stack.current_state == [4]
    assert not stack.snapshots
    assert not stack.forward_snapshots
    stack.current_state.append(16)
    assert stack.initial_state == [4]
    assert stack.current_state == [4, 16]
    assert not stack.snapshots
    assert not stack.forward_snapshots
    stack.do()
    assert stack.initial_state == [4]
    assert stack.current_state == [4, 16]
    assert stack.snapshots == [[4, 16]]
    assert not stack.forward_snapshots
    stack.current_state = ['totally', 'new', 'list']
    stack.do()
    assert stack.initial_state == [4]
    assert stack.current_state == ['totally', 'new', 'list']
    assert stack.snapshots[-1] == ['totally', 'new', 'list']
    assert not stack.forward_snapshots
    stack.undo()
    assert stack.current_state == [4, 16]
    assert stack.snapshots == [[4, 16]]
    assert stack.forward_snapshots == [['totally', 'new', 'list']]
    stack.undo()
    assert stack.current_state == [4]
    assert not stack.snapshots
    assert stack.forward_snapshots[-1] == [4, 16]
    with pytest.raises(IndexError):
        stack.undo()
    stack.redo()
    assert stack.current_state == [4, 16]
    assert stack.snapshots == [[4, 16]]
    assert stack.forward_snapshots == [['totally', 'new', 'list']]
    stack.redo()
    assert stack.current_state == ['totally', 'new', 'list']
    assert stack.snapshots == [[4, 16], ['totally', 'new', 'list']]
    assert not stack.forward_snapshots
    with pytest.raises(IndexError):
        stack.redo()
    stack.undo()
    assert stack.current_state == [4, 16]
    assert stack.snapshots == [[4, 16]]
    assert stack.forward_snapshots == [['totally', 'new', 'list']]
    stack.current_state.append(64)
    stack.do()
    assert stack.current_state == [4, 16, 64]
    assert stack.snapshots == [[4, 16], [4, 16, 64]]
    assert stack.forward_snapshots == []
