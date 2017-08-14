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
        """Adds `op` to undo stack and applies it.
        
        As the redo stack is now invalid, also erases it.
        
        Arguments:
            op: operation object to apply; must have "do" and "redo" methods
        """
        self.done.append(op)
        self.undone = []
        return op.do()
    
    def undo(self):
        """Reverts the last undo stack operation and adds to redo stack.
        
        Does this by applying the "undo" method of the operation.
        
        Raises:
            IndexError: if the undo stack is empty.
        """
        op = self.done.pop()
        self.undone.append(op)
        return op.undo()
    
    def redo(self):
        """Applies top redo stack operation and adds to undo stack.
        
        Raises:
            IndexError: if the redo stack is empty.
        """
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
        """Creates a new RegeneratingUndoStack.
        
        Arguments:
            initial_state: objects to apply operations to
        """
        self.current_state = copy.deepcopy(initial_state)
        self.initial_state = copy.deepcopy(initial_state)
        self.done = []
        self.undone = []
    
    def do(self, op):
        """Adds `op` to undo stack and applies it.
        
        As the redo stack is now invalid, also erases it.
        
        Arguments:
            op (callable): operation to apply; must take 1 positional argument
        """
        self.done.append(op)
        self.undone = []
        op(self.current_state)
    
    def undo(self):
        """Reverts the last undo stack operation and adds to redo stack.
        
        Does this by re-applying all but the last undo stack operation to the
        initial state.
        
        Raises:
            IndexError: if the undo stack is empty.
        """
        self.undone.append(self.done.pop())
        self._regenerate()
    
    def redo(self):
        """Applies top redo stack operation and adds to undo stack.
        
        Raises:
            IndexError: if the redo stack is empty.
        """
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
        """Creates a new SnapshotUndoStack object.
        
        Arguments:
            objects: object or objects to take snapshots of
        """
        self.snapshots = []
        self.forward_snapshots = []
        self.current_state = copy.deepcopy(objects)
        self.initial_state = copy.deepcopy(objects)
    
    def do(self, new_state=None):
        """Take a snapshot of some objects and add it to the undo stack.
        
        If `new_state` is given, substitutes it for `current_state` and takes
        snapshot. Otherwise, the snapshot is of the existing `current_state`.
        
        Because the redo stack is now (conceptually) invalid, erases it.
        
        Arguments:
            new_state: if present, replaces `current_state`
        """
        if new_state is not None:
            self.current_state = new_state
        self.snapshots.append(copy.deepcopy(self.current_state))
        self.forward_snapshots = []
    
    def undo(self):
        """Adds the last snapshot to redo stack and reverts to the one before.
        
        If current_state contains changes not in the last snapshot, those are
        discarded too.
        
        Raises:
            IndexError: if the undo stack is empty
        """
        self.forward_snapshots.append(self.snapshots.pop())
        if self.snapshots:
            self.current_state = copy.deepcopy(self.snapshots[-1])
        else:
            self.current_state = copy.deepcopy(self.initial_state)
    
    def redo(self):
        """Adds the next snapshot to the undo stack and assumes its values.
        
        If current_state contains changes not in the last snapshot, they are
        lost.
        
        Raises:
            IndexError: if the redo stack is empty.
        """
        self.snapshots.append(self.forward_snapshots.pop())
        self.current_state = copy.deepcopy(self.snapshots[-1])
    
    @property
    def clean(self):
        """Checks whether `current_state` matches the last snapshot.
        
        Returns:
            bool: whether `current_state` matches the last snapshot.
        """
        if self.snapshots:
            return self.current_state == self.snapshots[-1]
        else:
            return self.current_state == self.initial_state
    
    def discard_changes(self):
        """Discards any unrecorded changes to `current_state`."""
        if not self.clean:
            if self.snapshots:
                self.current_state = copy.deepcopy(self.snapshots[-1])
            else:
                self.current_state = copy.deepcopy(self.initial_state)
