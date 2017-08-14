# undone

Version: 0.2

## Three implementations

This module offers three undo stack implementations. Each has different
tradeoffs, and may be better suited to a given situation than the others.

### 1. `ReversibleUndoStack`: reversible operations

* define a class (or named tuple) for each operation, with "do" and "undo"
  methods
* hand instances of these classes to the stack object
* doesn't require any handle on the object(s) being modified by the operations
* up to the user to ensure reversibility, which in some cases can be quite
  difficult
* least memory and runtime overhead for operations

### 2. `RegeneratingUndoStack`: regenerating current state from scratch

* define a callable object for each operation
* hand instances of these objects to the stack object
* requires a handle on or snapshot of the initial state of the object(s) being
  modified by the operations; operations must accept this handle as a parameter when called
* higher overhead, especially for `undo` operation

### 3. `SnapshotUndoStack`: state-oriented

* requires handles on or snapshots of incremental states of the object(s) being
  modified. These snapshots are triggered explicitly by the user, and may be 
  taken as frequently or rarely as desired
* can involve significant memory overhead in the worst case

## Installation

`undone` works under Python 2.7 and Python 3.3+.

To install:
```
$ git clone http://github.com/gfetterman/undone.git
$ cd undone
$ pip install .

# to run the tests
$ pytest -v
```

## Usage

(Coming soon.)