import copy

class UndoStack:
    pass

# 1. reversible operations

class ReversibleUndoStack(UndoStack):
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

# 2. built from scratch

class RegeneratingUndoStack(UndoStack):
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
        self.done.append(self.undone.pop())
        self._regenerate()
    
    def _regenerate(self):
        self.current_state = copy.deepcopy(self.initial_state)
        [op(self.current_state) for op in self.done]

# 3. snapshots

class SnapshotUndoStack(UndoStack):
    def __init__(self, objects):
        self.snapshots = []
        self.forward_snapshots = []
        self.current_state = copy.deepcopy(objects)
        self.initial_state = copy.deepcopy(objects)
    
    def do(self):
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
