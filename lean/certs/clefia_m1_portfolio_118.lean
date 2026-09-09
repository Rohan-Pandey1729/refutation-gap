/-
  Machine-checkable certificate for a Shortest Linear Straight-Line Program.

  Instance    : clefia_m1
  Fingerprint : 60591a0ce16495fa
  Inputs      : 32 variables over GF(2)
  Outputs     : 32 linear forms
  Gate count  : 118 XOR gates
  Produced by : portfolio_k20_mode1
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

    lean lean/certs/clefia_m1_portfolio_118.lean

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
  [(5, 21), (13, 29), (14, 30), (6, 22), (7, 32), (23, 32), (7, 33), (23, 33), (15, 31), 
   (23, 38), (0, 35), (24, 34), (31, 39), (27, 40), (15, 36), (31, 37), (11, 45), (12, 28), 
   (22, 30), (4, 20), (15, 38), (34, 40), (19, 41), (3, 54), (26, 53), (10, 56), (1, 37), 
   (9, 58), (35, 41), (2, 60), (18, 61), (0, 44), (8, 47), (16, 52), (24, 46), (50, 51), 
   (15, 67), (15, 59), (9, 35), (69, 70), (17, 71), (26, 69), (49, 50), (7, 74), (16, 70), 
   (24, 76), (25, 42), (8, 78), (16, 43), (1, 80), (28, 72), (11, 82), (3, 83), (28, 62), 
   (29, 85), (20, 86), (29, 55), (13, 48), (22, 89), (5, 90), (42, 47), (30, 88), (5, 93), 
   (65, 80), (49, 85), (4, 96), (13, 97), (21, 57), (4, 99), (12, 100), (17, 34), (44, 53), 
   (25, 103), (102, 104), (19, 104), (9, 106), (27, 107), (4, 108), (2, 105), (47, 52), 
   (8, 102), (0, 112), (88, 89), (108, 114), (20, 115), (2, 10), (18, 26), (63, 91), (92, 119), 
   (66, 95), (94, 121), (111, 118), (73, 123), (49, 84), (114, 125), (35, 53), (46, 75), 
   (68, 127), (110, 111), (117, 130), (47, 127), (128, 132), (101, 128), (68, 134), (65, 123), 
   (11, 136), (42, 137), (8, 117), (19, 139), (95, 140), (3, 121), (24, 64), (118, 143), 
   (142, 144), (42, 46), (16, 146), (27, 117), (147, 148)]

/-- The circuit uses exactly 118 XOR gates. -/
theorem gate_count : prog.length = 118 := by rfl

/-- MAIN RESULT: the circuit is well formed and computes every target. -/
theorem cert : SLP.valid n targets prog = true := by decide

-- Trust base. An empty axiom list means the kernel checked everything.
#print axioms cert
#print axioms gate_count

end CertClefiam1