import collections
import functools
import pytest
import undone

INITIAL_STATE = [4]
SECOND_STATE = [4, 1]
THIRD_STATE = [4, 1, 1]
FOURTH_STATE = [4, 1, 2]
FIFTH_STATE = ['totally', 'new', 'list']
SIXTH_STATE = [4, 64, 256]

def common_tests(stack, resource, ops):
    stack.do(ops[0])
    assert resource() == SECOND_STATE
    stack.do(ops[1])
    assert resource() == THIRD_STATE
    stack.undo()
    assert resource() == SECOND_STATE
    stack.undo()
    assert resource() == INITIAL_STATE
    with pytest.raises(IndexError):
        stack.undo()
    stack.redo()
    assert resource() == SECOND_STATE
    stack.redo()
    assert resource() == THIRD_STATE
    with pytest.raises(IndexError):
        stack.redo()
    stack.undo()
    assert stack.undone == [ops[1]]
    stack.do(ops[2])
    assert resource() == FOURTH_STATE
    assert stack.undone == []

def test_reversible():
    resource = []
    resource.extend(INITIAL_STATE)
    def remove_one(r):
        try:
            r.pop()
        except IndexError:
            pass
    Revop = collections.namedtuple("Revop", ["do", "undo"])
    adding_one = Revop(functools.partial(lambda r: r.append(1), r=resource),
                       functools.partial(remove_one, r=resource))
    adding_two = Revop(functools.partial(lambda r: r.append(2), r=resource),
                       functools.partial(remove_one, r=resource))
    stack = undone.ReversibleUndoStack()
    common_tests(stack,
                 lambda: resource,
                 [adding_one, adding_one, adding_two])

def test_regenerating():
    def add_one(r):
        r.append(1)
    def add_two(r):
        r.append(2)
    stack = undone.RegeneratingUndoStack(initial_state=INITIAL_STATE)
    def resource(s):
        return s.current_state
    common_tests(stack,
                 functools.partial(resource, s=stack),
                 [add_one, add_one, add_two])

def test_snapshot():
    stack = undone.SnapshotUndoStack(INITIAL_STATE)
    assert stack.current_state == INITIAL_STATE
    assert not stack.snapshots
    assert not stack.forward_snapshots
    stack.current_state.append(1)
    assert stack.current_state == SECOND_STATE
    assert not stack.snapshots
    assert not stack.forward_snapshots
    stack.do()
    assert stack.current_state == SECOND_STATE
    assert stack.snapshots == [SECOND_STATE]
    stack.current_state = FIFTH_STATE
    stack.do()
    assert stack.current_state == FIFTH_STATE
    assert stack.snapshots[-1] == FIFTH_STATE
    stack.undo()
    assert stack.current_state == SECOND_STATE
    assert stack.snapshots == [SECOND_STATE]
    assert stack.forward_snapshots == [FIFTH_STATE]
    stack.undo()
    assert stack.current_state == INITIAL_STATE
    assert not stack.snapshots
    assert stack.forward_snapshots[-1] == SECOND_STATE
    with pytest.raises(IndexError):
        stack.undo()
    stack.redo()
    assert stack.current_state == SECOND_STATE
    assert stack.snapshots == [SECOND_STATE]
    assert stack.forward_snapshots == [FIFTH_STATE]
    stack.redo()
    assert stack.current_state == FIFTH_STATE
    assert stack.snapshots == [SECOND_STATE, FIFTH_STATE]
    assert not stack.forward_snapshots
    with pytest.raises(IndexError):
        stack.redo()
    stack.undo()
    assert stack.current_state == SECOND_STATE
    assert stack.snapshots == [SECOND_STATE]
    assert stack.forward_snapshots == [FIFTH_STATE]
    stack.current_state.extend([64, 256])
    del stack.current_state[1]
    stack.do()
    assert stack.current_state == SIXTH_STATE
    assert stack.snapshots == [SECOND_STATE, SIXTH_STATE]
    assert not stack.forward_snapshots
