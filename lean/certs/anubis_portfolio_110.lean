/-
  Machine-checkable certificate for a Shortest Linear Straight-Line Program.

  Instance    : anubis
  Fingerprint : e91a060b2ec0d36f
  Inputs      : 32 variables over GF(2)
  Outputs     : 32 linear forms
  Gate count  : 110 XOR gates
  Produced by : portfolio_k10_mode0
  Source run  : portfolio

  WHAT THIS FILE PROVES

    SLP.valid n targets prog = true

  which unfolds to two conjuncts:

    (1) wellFormed  -- every gate reads only earlier signals, and no gate is a
                       self-XOR (x XOR x = 0, which would be a way to cheat).
    (2) computes    -- every one of the 32 target linear forms appears among the
                       signals the program actually produces.

  Signals are coefficient vectors over GF(2), so signal equality IS equality of
  linear forms. There is no abstraction gap to argue about.

  HOW TO CHECK IT

    lean lean/certs/anubis_portfolio_110.lean

  No Mathlib, no lake, no imports. If it compiles with no errors, the circuit is
  correct. The final `#print axioms` line reports the trust base; an empty axiom
  list means the Lean kernel checked everything itself.

  This file is generated. Do not edit by hand.
-/

set_option maxRecDepth 1000000

namespace SLP

/-- A linear form over GF(2), as its coefficient vector. -/
abbrev Vec := List Bool

/-- Addition in GF(2)^n. -/
def xorVec (u v : Vec) : Vec := List.zipWith Bool.xor u v

/-- The i-th standard basis vector in GF(2)^n, i.e. the input variable x_i. -/
def basisRow (n i : Nat) : Vec := (List.range n).map (fun j => Nat.beq i j)

/-- The n input variables. -/
def basis (n : Nat) : List Vec := (List.range n).map (basisRow n)

/-- Append one gate: a new signal equal to the XOR of two existing ones. -/
def stepOne (sigs : List Vec) (op : Nat × Nat) : List Vec :=
  sigs ++ [xorVec (sigs.getD op.1 []) (sigs.getD op.2 [])]

/-- Run the whole program, returning every signal it computes. -/
def signals (n : Nat) (prog : List (Nat × Nat)) : List Vec :=
  prog.foldl stepOne (basis n)

/-- Gate k may only read signals with index < n + k, and may not read the same
    signal twice (which would compute the zero vector). -/
def wellFormedAux (n : Nat) : Nat -> List (Nat × Nat) -> Bool
  | _, [] => true
  | k, (a, b) :: rest =>
      Nat.blt a (n + k) && Nat.blt b (n + k) && (! Nat.beq a b) &&
        wellFormedAux n (k + 1) rest

def wellFormed (n : Nat) (prog : List (Nat × Nat)) : Bool := wellFormedAux n 0 prog

/-- Every target linear form is realised by some signal. -/
def computesWith (sigs : List Vec) (targets : List Vec) : Bool :=
  targets.all (fun t => sigs.any (fun v => v == t))

def valid (n : Nat) (targets : List Vec) (prog : List (Nat × Nat)) : Bool :=
  wellFormed n prog && computesWith (signals n prog) targets

end SLP


namespace CertAnubis

def n : Nat := 32

/-- The target matrix: one coefficient vector per output row. -/
def targets : List SLP.Vec :=
  [
  [true, false, false, false, false, false, false, false, false, false, false, false, false, false, false, true, false, false, false, false, false, false, true, false, false, false, false, false, false, false, true, true],
  [false, true, false, false, false, false, false, false, true, false, false, false, false, false, false, false, false, false, false, false, false, false, false, true, true, false, false, false, false, false, false, true],
  [false, false, true, false, false, false, false, false, false, true, false, false, false, false, false, true, true, false, false, false, false, false, true, false, true, true, false, false, false, false, true, true],
  [false, false, false, true, false, false, false, false, false, false, true, false, false, false, false, true, false, true, false, false, false, false, true, true, false, true, true, false, false, false, true, false],
  [false, false, false, false, true, false, false, false, false, false, false, true, false, false, false, true, false, false, true, false, false, false, true, true, false, false, true, true, false, false, true, false],
  [false, false, false, false, false, true, false, false, false, false, false, false, true, false, false, false, false, false, false, true, false, false, false, true, false, false, false, true, true, false, false, true],
  [false, false, false, false, false, false, true, false, false, false, false, false, false, true, false, false, false, false, false, false, true, false, false, false, false, false, false, false, true, true, false, false],
  [false, false, false, false, false, false, false, true, false, false, false, false, false, false, true, false, false, false, false, false, false, true, false, false, false, false, false, false, false, true, true, false],
  [false, false, false, false, false, false, false, true, true, false, false, false, false, false, false, false, false, false, false, false, false, false, true, true, false, false, false, false, false, false, true, false],
  [true, false, false, false, false, false, false, false, false, true, false, false, false, false, false, false, true, false, false, false, false, false, false, true, false, false, false, false, false, false, false, true],
  [false, true, false, false, false, false, false, true, false, false, true, false, false, false, false, false, true, true, false, false, false, false, true, true, true, false, false, false, false, false, true, false],
  [false, false, true, false, false, false, false, true, false, false, false, true, false, false, false, false, false, true, true, false, false, false, true, false, false, true, false, false, false, false, true, true],
  [false, false, false, true, false, false, false, true, false, false, false, false, true, false, false, false, false, false, true, true, false, false, true, false, false, false, true, false, false, false, true, true],
  [false, false, false, false, true, false, false, false, false, false, false, false, false, true, false, false, false, false, false, true, true, false, false, true, false, false, false, true, false, false, false, true],
  [false, false, false, false, false, true, false, false, false, false, false, false, false, false, true, false, false, false, false, false, true, true, false, false, false, false, false, false, true, false, false, false],
  [false, false, false, false, false, false, true, false, false, false, false, false, false, false, false, true, false, false, false, false, false, true, true, false, false, false, false, false, false, true, false, false],
  [false, false, false, false, false, false, true, false, false, false, false, false, false, false, true, true, true, false, false, false, false, false, false, false, false, false, false, false, false, false, false, true],
  [false, false, false, false, false, false, false, true, true, false, false, false, false, false, false, true, false, true, false, false, false, false, false, false, true, false, false, false, false, false, false, false],
  [true, false, false, false, false, false, true, false, true, true, false, false, false, false, true, true, false, false, true, false, false, false, false, false, false, true, false, false, false, false, false, true],
  [false, true, false, false, false, false, true, true, false, true, true, false, false, false, true, false, false, false, false, true, false, false, false, false, false, false, true, false, false, false, false, true],
  [false, false, true, false, false, false, true, true, false, false, true, true, false, false, true, false, false, false, false, false, true, false, false, false, false, false, false, true, false, false, false, true],
  [false, false, false, true, false, false, false, true, false, false, false, true, true, false, false, true, false, false, false, false, false, true, false, false, false, false, false, false, true, false, false, false],
  [false, false, false, false, true, false, false, false, false, false, false, false, true, true, false, false, false, false, false, false, false, false, true, false, false, false, false, false, false, true, false, false],
  [false, false, false, false, false, true, false, false, false, false, false, false, false, true, true, false, false, false, false, false, false, false, false, true, false, false, false, false, false, false, true, false],
  [false, false, false, false, false, false, true, true, false, false, false, false, false, false, true, false, false, false, false, false, false, false, false, true, true, false, false, false, false, false, false, false],
  [true, false, false, false, false, false, false, true, false, false, false, false, false, false, false, true, true, false, false, false, false, false, false, false, false, true, false, false, false, false, false, false],
  [true, true, false, false, false, false, true, true, true, false, false, false, false, false, true, false, false, true, false, false, false, false, false, true, false, false, true, false, false, false, false, false],
  [false, true, true, false, false, false, true, false, false, true, false, false, false, false, true, true, false, false, true, false, false, false, false, true, false, false, false, true, false, false, false, false],
  [false, false, true, true, false, false, true, false, false, false, true, false, false, false, true, true, false, false, false, true, false, false, false, true, false, false, false, false, true, false, false, false],
  [false, false, false, true, true, false, false, true, false, false, false, true, false, false, false, true, false, false, false, false, true, false, false, false, false, false, false, false, false, true, false, false],
  [false, false, false, false, true, true, false, false, false, false, false, false, true, false, false, false, false, false, false, false, false, true, false, false, false, false, false, false, false, false, true, false],
  [false, false, false, false, false, true, true, false, false, false, false, false, false, true, false, false, false, false, false, false, false, false, true, false, false, false, false, false, false, false, false, true]
  ]

/-- The circuit: gate k computes signal (n+k) = signal a XOR signal b. -/
def prog : List (Nat × Nat) :=
  [(6, 14), (22, 30), (7, 15), (23, 31), (7, 32), (7, 33), (23, 36), (23, 37), (3, 34), 
   (19, 35), (6, 29), (4, 12), (5, 13), (0, 34), (16, 35), (1, 38), (17, 39), (21, 42), 
   (5, 21), (9, 46), (10, 48), (11, 40), (16, 45), (25, 54), (24, 34), (26, 47), (27, 41), 
   (4, 53), (20, 58), (0, 51), (8, 39), (24, 38), (4, 60), (13, 64), (8, 56), (17, 66), 
   (15, 49), (22, 68), (20, 59), (29, 70), (36, 49), (30, 72), (37, 45), (31, 74), (43, 50), 
   (30, 76), (0, 57), (8, 78), (17, 79), (1, 35), (24, 81), (8, 82), (5, 58), (12, 84), 
   (28, 85), (6, 44), (22, 87), (31, 88), (12, 53), (21, 90), (28, 91), (13, 42), (20, 93), 
   (28, 94), (14, 50), (20, 96), (2, 9), (18, 27), (3, 26), (39, 99), (100, 101), (2, 10), 
   (19, 38), (103, 104), (25, 52), (28, 97), (59, 102), (5, 85), (102, 109), (11, 60), 
   (105, 111), (26, 40), (106, 113), (28, 40), (105, 115), (34, 38), (46, 117), (36, 39), 
   (88, 119), (46, 52), (82, 121), (49, 76), (88, 123), (1, 98), (99, 117), (125, 126), 
   (9, 10), (41, 57), (128, 129), (55, 56), (75, 98), (131, 132), (8, 18), (38, 51), (55, 134), 
   (135, 136), (11, 18), (35, 103), (106, 138), (139, 140)]

/-- The circuit uses exactly 110 XOR gates. -/
theorem gate_count : prog.length = 110 := by rfl

/-- MAIN RESULT: the circuit is well formed and computes every target. -/
theorem cert : SLP.valid n targets prog = true := by decide

-- Trust base. An empty axiom list means the kernel checked everything.
#print axioms cert
#print axioms gate_count

end CertAnubis