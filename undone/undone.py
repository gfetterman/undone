import copy

class UndoStack:
    """Abstract parent class for undo stacks."""
    pass

class ReversibleUndoStack(UndoStack):
    """Undo stack for reversible operations.
    
    Operations pushed to this stack must be objects with, at minimum, methods
    named "do" and "undo". These methods should be perfect inverses of each
    other - i.e., every change made to objects by the "do()" method should be
    reversed by the "undo()" method. If the methods are not perfect inverses,
    program behavior is undefined.
    
    These methods must be callable objects which accept no required arguments.
    Use functools.partial or default-argument-value lambdas to create them
    as necessary. Be aware of the implications the use of complete closures has
    for parallel applications.
    
    This undo stack passes any return values from the application of "do" or
    "undo" methods through to the caller, if that's a feature you want.
    
    Unlike the Regenerating or Snapshot undo stacks, this stack does not
    require a reference to the objects being changed. Thus, existing references
    to the objects are not rendered stale by undo stack operations.
    
    If it is impossible or inconvenient to express the operations you need in a
    reversible form, use another type of undo stack.
    """
    def __init__(self):
        self.done = []
        self.undone = []
    
    def do(self, op):
        self.done.append(op)
        self.undone = []
        return op.do()
    
    def undo(self):
        op = self.done.pop()
        self.undone.append(op)
        return op.undo()
    
    def redo(self):
        op = self.undone.pop()
        self.done.append(op)
        return op.do()

class RegeneratingUndoStack(UndoStack):
    """Undo stack for general operations.
    
    Operations pushed to this stack should be callable objects which accept one
    positional argument - the object (or list of objects) to act on. Use
    functools.partial or default-argument-value lambdas to create a closure
    which satisfies this requirement from a function with more arguments.
    
    Note that this undo stack may run operations multiple times in the course
    of use (as it rebuilds the current state from the initial state and
    operation stack for each undo). Thus, you must be conscious of any side-
    effects your operations may have. Ideally, you would be pushing operations
    with zero side-effects.
    
    Return values from the operations pushed to the undo stack are discarded.
    
    This undo stack must hold references to the object or objects its
    operations are modifying. Exterior references to these objects may become
    stale during use, so all access to these objects should be carried out
    through this undo stack object, via its `current_state` variable.
    """
    def __init__(self, initial_state):
        self.current_state = copy.deepcopy(initial_state)
        self.initial_state = copy.deepcopy(initial_state)
        self.done = []
        self.undone = []
    
    def do(self, op):
        self.done.append(op)
        self.undone = []
        op(self.current_state)
    
    def undo(self):
        self.undone.append(self.done.pop())
        self._regenerate()
    
    def redo(self):
        op = self.undone.pop()
        self.done.append(op)
        op(self.current_state)
    
    def _regenerate(self):
        self.current_state = copy.deepcopy(self.initial_state)
        [op(self.current_state) for op in self.done]

class SnapshotUndoStack(UndoStack):
    """Undo stack which is state-focused rather than operation-focused.
    
    Rather than containing operations to apply, this stack contains snapshots
    of the state of an object or list of objects at a sequence of points in
    time.
    
    Snapshots are only taken when the user chooses to. The user may decide how
    often to take them.
    
    This undo stack must hold references to the object or objects of which it
    is taking snapshots. Exterior references to these objects may become
    stale during use, so all access to these objects should be carried out
    through this undo stack object, via its `current_state` variable.
    """
    def __init__(self, objects):
        self.snapshots = []
        self.forward_snapshots = []
        self.current_state = copy.deepcopy(objects)
        self.initial_state = copy.deepcopy(objects)
    
    def do(self, new_state=None):
        if new_state is not None:
            self.current_state = new_state
        self.snapshots.append(copy.deepcopy(self.current_state))
        self.forward_snapshots = []
    
    def undo(self):
        self.forward_snapshots.append(self.snapshots.pop())
        if self.snapshots:
            self.current_state = copy.deepcopy(self.snapshots[-1])
        else:
            self.current_state = copy.deepcopy(self.initial_state)
    
    def redo(self):
        self.snapshots.append(self.forward_snapshots.pop())
        self.current_state = copy.deepcopy(self.snapshots[-1])
