import copy

# 1. reversible operations

class ReversibleUndoStack:
    def __init__(self):
        self.done = []
        self.undone = []
    
    def do(self, op):
        self.done.append(op)
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

class RegeneratingUndoStack:
    def __init__(self, initial_state):
        self.current_state = initial_state
        self.initial_state = copy.deepcopy(initial_state)
        self.done = []
        self.undone = []
    
    def do(self, op):
        self.done.append(op)
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

class SnapshotUndoStack:
    def __init__(self, objects):
        self.snapshots = []
        self.forward_snapshots = []
        self.current_state = objects
        self.initial_state = self.snap()
    
    def do(self):
        self.snapshots.append(copy.deepcopy(self.objects))
    
    def undo(self):
        state = self.snapshots.pop()
        self.forward_snapshots.append(state)
        self.current_state = copy.deepcopy(state)
    
    def redo(self):
        state = self.forward_snapshots.pop()
        self.snapshots.append(state)
        self.current_state = copy.deepcopy(state)