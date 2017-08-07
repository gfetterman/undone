# undo stacks

## General interface

An undo/redo stack must allow:

1. Logging actions taken
2. Restoring some state to before an action was taken
3. Re-performing an action that was previously undone

## Three possible implementations

There are three basic ways to implement an undo stack. Each has different
tradeoffs, and may be better suited to a given situation than the others.

### 1. Reversible operations

* define a class (or named tuple) for each operation, with a well-defined
  interface - something like "forward_op" and "reverse_op"
* hand instances of this class to the stack object
* doesn't require any handle on the object(s) being modified by the operations

### 2. Building from scratch

* (optionally) define a class for each operation, with a well-defined
  interface - something like "execute" or "forward_op", or perhaps just
  "__call__"
* hand instances of these classes to the stack object
* requires a handle on or snapshot of the initial state of the object(s) being
  modified by the operations; operations probably need to be handed this handle
  every time they're called

### 3. Snapshots

* requires handles on or snapshots of incremental states of the object(s) being
  modified by the operations. These snapshots are triggered explicitly by the
  user, and so can be used as frequently or as moderately as desired
* a more advanced feature involves providing a method to `diff` the snapshots,
  to allow more efficient storage of the snapshots
