/-
  Machine-checkable certificate for a Shortest Linear Straight-Line Program.

  Instance    : clefia_m1
  Fingerprint : 60591a0ce16495fa
  Inputs      : 32 variables over GF(2)
  Outputs     : 32 linear forms
  Gate count  : 110 XOR gates
  Produced by : portfolio k=200 mode=1 seed=762144912
  Source run  : portfolio_overnight

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

    lean lean/certs/clefia_m1_best_110.lean

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


namespace CertClefiam1

def n : Nat := 32

/-- The target matrix: one coefficient vector per output row. -/
def targets : List SLP.Vec :=
  [
  [true, false, false, false, false, false, false, false, false, false, false, false, false, true, false, false, false, false, false, false, false, false, false, true, false, false, false, false, false, true, false, true],
  [false, true, false, false, false, false, false, false, false, false, false, false, false, false, true, false, true, false, false, false, false, false, false, false, true, false, false, false, false, false, true, false],
  [false, false, true, false, false, false, false, false, false, false, false, false, false, true, false, true, false, true, false, false, false, false, false, true, false, true, false, false, false, true, false, false],
  [false, false, false, true, false, false, false, false, true, false, false, false, false, true, true, false, false, false, true, false, false, false, false, true, true, false, true, false, false, true, true, true],
  [false, false, false, false, true, false, false, false, false, true, false, false, false, true, true, true, false, false, false, true, false, false, false, true, false, true, false, true, false, true, true, false],
  [false, false, false, false, false, true, false, false, false, false, true, false, false, false, true, true, false, false, false, false, true, false, false, false, false, false, true, false, true, false, true, true],
  [false, false, false, false, false, false, true, false, false, false, false, true, false, false, false, true, false, false, false, false, false, true, false, false, false, false, false, true, false, true, false, true],
  [false, false, false, false, false, false, false, true, false, false, false, false, true, false, false, false, false, false, false, false, false, false, true, false, false, false, false, false, true, false, true, false],
  [false, false, false, false, false, true, false, false, true, false, false, false, false, false, false, false, false, false, false, false, false, true, false, true, false, false, false, false, false, false, false, true],
  [false, false, false, false, false, false, true, false, false, true, false, false, false, false, false, false, true, false, false, false, false, false, true, false, true, false, false, false, false, false, false, false],
  [false, false, false, false, false, true, false, true, false, false, true, false, false, false, false, false, false, true, false, false, false, true, false, false, false, true, false, false, false, false, false, true],
  [true, false, false, false, false, true, true, false, false, false, false, true, false, false, false, false, true, false, true, false, false, true, true, true, false, false, true, false, false, false, false, true],
  [false, true, false, false, false, true, true, true, false, false, false, false, true, false, false, false, false, true, false, true, false, true, true, false, false, false, false, true, false, false, false, true],
  [false, false, true, false, false, false, true, true, false, false, false, false, false, true, false, false, false, false, true, false, true, false, true, true, false, false, false, false, true, false, false, false],
  [false, false, false, true, false, false, false, true, false, false, false, false, false, false, true, false, false, false, false, true, false, true, false, true, false, false, false, false, false, true, false, false],
  [false, false, false, false, true, false, false, false, false, false, false, false, false, false, false, true, false, false, false, false, true, false, true, false, false, false, false, false, false, false, true, false],
  [false, false, false, false, false, false, false, true, false, false, false, false, false, true, false, true, true, false, false, false, false, false, false, false, false, false, false, false, false, true, false, false],
  [true, false, false, false, false, false, false, false, true, false, false, false, false, false, true, false, false, true, false, false, false, false, false, false, false, false, false, false, false, false, true, false],
  [false, true, false, false, false, false, false, true, false, true, false, false, false, true, false, false, false, false, true, false, false, false, false, false, false, false, false, false, false, true, false, true],
  [false, false, true, false, false, false, false, true, true, false, true, false, false, true, true, true, false, false, false, true, false, false, false, false, true, false, false, false, false, true, true, false],
  [false, false, false, true, false, false, false, true, false, true, false, true, false, true, true, false, false, false, false, false, true, false, false, false, false, true, false, false, false, true, true, true],
  [false, false, false, false, true, false, false, false, false, false, true, false, true, false, true, true, false, false, false, false, false, true, false, false, false, false, true, false, false, false, true, true],
  [false, false, false, false, false, true, false, false, false, false, false, true, false, true, false, true, false, false, false, false, false, false, true, false, false, false, false, true, false, false, false, true],
  [false, false, false, false, false, false, true, false, false, false, false, false, true, false, true, false, false, false, false, false, false, false, false, true, false, false, false, false, true, false, false, false],
  [false, false, false, false, false, true, false, true, false, false, false, false, false, false, false, true, false, false, false, false, false, true, false, false, true, false, false, false, false, false, false, false],
  [true, false, false, false, false, false, true, false, true, false, false, false, false, false, false, false, false, false, false, false, false, false, true, false, false, true, false, false, false, false, false, false],
  [false, true, false, false, false, true, false, false, false, true, false, false, false, false, false, true, false, false, false, false, false, true, false, true, false, false, true, false, false, false, false, false],
  [true, false, true, false, false, true, true, true, false, false, true, false, false, false, false, true, true, false, false, false, false, true, true, false, false, false, false, true, false, false, false, false],
  [false, true, false, true, false, true, true, false, false, false, false, true, false, false, false, true, false, true, false, false, false, true, true, true, false, false, false, false, true, false, false, false],
  [false, false, true, false, true, false, true, true, false, false, false, false, true, false, false, false, false, false, true, false, false, false, true, true, false, false, false, false, false, true, false, false],
  [false, false, false, true, false, true, false, true, false, false, false, false, false, true, false, false, false, false, false, true, false, false, false, true, false, false, false, false, false, false, true, false],
  [false, false, false, false, true, false, true, false, false, false, false, false, false, false, true, false, false, false, false, false, true, false, false, false, false, false, false, false, false, false, false, true]
  ]

/-- The circuit: gate k computes signal (n+k) = signal a XOR signal b. -/
def prog : List (Nat × Nat) :=
  [(5, 21), (13, 29), (14, 30), (6, 22), (23, 31), (7, 15), (7, 23), (32, 36), (15, 31), 
   (33, 36), (0, 35), (8, 34), (18, 38), (26, 40), (27, 40), (32, 37), (3, 38), (9, 41), 
   (17, 47), (16, 24), (25, 40), (33, 37), (19, 48), (21, 29), (5, 13), (11, 46), (6, 14), 
   (4, 20), (12, 28), (22, 30), (1, 50), (35, 62), (11, 48), (19, 46), (25, 49), (34, 66), 
   (44, 45), (43, 53), (24, 69), (2, 10), (16, 47), (42, 72), (10, 45), (34, 74), (4, 12), 
   (20, 28), (35, 44), (2, 78), (0, 41), (8, 39), (24, 47), (16, 53), (68, 73), (11, 84), 
   (6, 57), (55, 86), (31, 58), (59, 88), (77, 79), (13, 90), (64, 67), (20, 92), (12, 65), 
   (63, 94), (4, 67), (65, 96), (22, 57), (56, 98), (63, 64), (28, 100), (19, 71), (70, 102), 
   (15, 61), (59, 104), (23, 58), (60, 106), (25, 42), (8, 108), (37, 104), (60, 110), (5, 77), 
   (75, 112), (0, 43), (17, 114), (75, 76), (21, 116), (1, 44), (49, 118), (68, 70), (3, 120), 
   (10, 50), (52, 122), (54, 55), (14, 124), (29, 79), (76, 126), (27, 73), (71, 128), (1, 51), 
   (34, 130), (30, 56), (54, 132), (9, 35), (51, 134), (47, 123), (41, 136), (71, 137), 
   (83, 119), (72, 139), (68, 140)]

/-- The circuit uses exactly 110 XOR gates. -/
theorem gate_count : prog.length = 110 := by rfl

/-- MAIN RESULT: the circuit is well formed and computes every target. -/
theorem cert : SLP.valid n targets prog = true := by decide

-- Trust base. An empty axiom list means the kernel checked everything.
#print axioms cert
#print axioms gate_count

end CertClefiam1