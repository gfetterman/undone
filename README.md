# undo stacks

Version: 0.1.1

## Three implementations

There are three basic ways to implement an undo stack. Each has different
tradeoffs, and may be better suited to a given situation than the others.

### 1. Reversible operations

* define a class (or named tuple) for each operation, with a well-defined
  interface - something like `do` and `undo`
* hand instances of this class to the stack object
* doesn't require any handle on the object(s) being modified by the operations
* but not all operations are easily reversible
* and it's up to the user to ensure reversibility

### 2. Regenerating current state from scratch

* define a function or callable class for each operation
* hand instances of these objects to the stack object
* requires a handle on or snapshot of the initial state of the object(s) being
  modified by the operations; operations must accept this handle as a parameter when called

### 3. Snapshots

* requires handles on or snapshots of incremental states of the object(s) being
  modified by the operations. These snapshots are triggered explicitly by the
  user, and so can be used as frequently or rarely as desired
* a more advanced feature involves providing a method to `diff` the snapshots,
  to allow more efficient storage of the snapshots (not implemented yet)
