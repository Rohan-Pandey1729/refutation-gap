/-
  Machine-checkable certificate for a Shortest Linear Straight-Line Program.

  Instance    : aes_mixcolumns
  Fingerprint : a12ac93d743531f4
  Inputs      : 32 variables over GF(2)
  Outputs     : 32 linear forms
  Gate count  : 98 XOR gates
  Produced by : portfolio_k400_mode1
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

    lean lean/certs/aes_mixcolumns_portfolio_98.lean

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


namespace CertAesmixcolumns

def n : Nat := 32

/-- The target matrix: one coefficient vector per output row. -/
def targets : List SLP.Vec :=
  [
  [false, false, false, false, false, false, false, true, true, false, false, false, false, false, false, true, true, false, false, false, false, false, false, false, true, false, false, false, false, false, false, false],
  [true, false, false, false, false, false, false, true, true, true, false, false, false, false, false, true, false, true, false, false, false, false, false, false, false, true, false, false, false, false, false, false],
  [false, true, false, false, false, false, false, false, false, true, true, false, false, false, false, false, false, false, true, false, false, false, false, false, false, false, true, false, false, false, false, false],
  [false, false, true, false, false, false, false, true, false, false, true, true, false, false, false, true, false, false, false, true, false, false, false, false, false, false, false, true, false, false, false, false],
  [false, false, false, true, false, false, false, true, false, false, false, true, true, false, false, true, false, false, false, false, true, false, false, false, false, false, false, false, true, false, false, false],
  [false, false, false, false, true, false, false, false, false, false, false, false, true, true, false, false, false, false, false, false, false, true, false, false, false, false, false, false, false, true, false, false],
  [false, false, false, false, false, true, false, false, false, false, false, false, false, true, true, false, false, false, false, false, false, false, true, false, false, false, false, false, false, false, true, false],
  [false, false, false, false, false, false, true, false, false, false, false, false, false, false, true, true, false, false, false, false, false, false, false, true, false, false, false, false, false, false, false, true],
  [true, false, false, false, false, false, false, false, false, false, false, false, false, false, false, true, true, false, false, false, false, false, false, true, true, false, false, false, false, false, false, false],
  [false, true, false, false, false, false, false, false, true, false, false, false, false, false, false, true, true, true, false, false, false, false, false, true, false, true, false, false, false, false, false, false],
  [false, false, true, false, false, false, false, false, false, true, false, false, false, false, false, false, false, true, true, false, false, false, false, false, false, false, true, false, false, false, false, false],
  [false, false, false, true, false, false, false, false, false, false, true, false, false, false, false, true, false, false, true, true, false, false, false, true, false, false, false, true, false, false, false, false],
  [false, false, false, false, true, false, false, false, false, false, false, true, false, false, false, true, false, false, false, true, true, false, false, true, false, false, false, false, true, false, false, false],
  [false, false, false, false, false, true, false, false, false, false, false, false, true, false, false, false, false, false, false, false, true, true, false, false, false, false, false, false, false, true, false, false],
  [false, false, false, false, false, false, true, false, false, false, false, false, false, true, false, false, false, false, false, false, false, true, true, false, false, false, false, false, false, false, true, false],
  [false, false, false, false, false, false, false, true, false, false, false, false, false, false, true, false, false, false, false, false, false, false, true, true, false, false, false, false, false, false, false, true],
  [true, false, false, false, false, false, false, false, true, false, false, false, false, false, false, false, false, false, false, false, false, false, false, true, true, false, false, false, false, false, false, true],
  [false, true, false, false, false, false, false, false, false, true, false, false, false, false, false, false, true, false, false, false, false, false, false, true, true, true, false, false, false, false, false, true],
  [false, false, true, false, false, false, false, false, false, false, true, false, false, false, false, false, false, true, false, false, false, false, false, false, false, true, true, false, false, false, false, false],
  [false, false, false, true, false, false, false, false, false, false, false, true, false, false, false, false, false, false, true, false, false, false, false, true, false, false, true, true, false, false, false, true],
  [false, false, false, false, true, false, false, false, false, false, false, false, true, false, false, false, false, false, false, true, false, false, false, true, false, false, false, true, true, false, false, true],
  [false, false, false, false, false, true, false, false, false, false, false, false, false, true, false, false, false, false, false, false, true, false, false, false, false, false, false, false, true, true, false, false],
  [false, false, false, false, false, false, true, false, false, false, false, false, false, false, true, false, false, false, false, false, false, true, false, false, false, false, false, false, false, true, true, false],
  [false, false, false, false, false, false, false, true, false, false, false, false, false, false, false, true, false, false, false, false, false, false, true, false, false, false, false, false, false, false, true, true],
  [true, false, false, false, false, false, false, true, true, false, false, false, false, false, false, false, true, false, false, false, false, false, false, false, false, false, false, false, false, false, false, true],
  [true, true, false, false, false, false, false, true, false, true, false, false, false, false, false, false, false, true, false, false, false, false, false, false, true, false, false, false, false, false, false, true],
  [false, true, true, false, false, false, false, false, false, false, true, false, false, false, false, false, false, false, true, false, false, false, false, false, false, true, false, false, false, false, false, false],
  [false, false, true, true, false, false, false, true, false, false, false, true, false, false, false, false, false, false, false, true, false, false, false, false, false, false, true, false, false, false, false, true],
  [false, false, false, true, true, false, false, true, false, false, false, false, true, false, false, false, false, false, false, false, true, false, false, false, false, false, false, true, false, false, false, true],
  [false, false, false, false, true, true, false, false, false, false, false, false, false, true, false, false, false, false, false, false, false, true, false, false, false, false, false, false, true, false, false, false],
  [false, false, false, false, false, true, true, false, false, false, false, false, false, false, true, false, false, false, false, false, false, false, true, false, false, false, false, false, false, true, false, false],
  [false, false, false, false, false, false, true, true, false, false, false, false, false, false, false, true, false, false, false, false, false, false, false, true, false, false, false, false, false, false, true, false]
  ]

/-- The circuit: gate k computes signal (n+k) = signal a XOR signal b. -/
def prog : List (Nat × Nat) :=
  [(7, 31), (15, 23), (7, 15), (23, 31), (0, 24), (8, 16), (6, 30), (21, 29), (14, 22), 
   (5, 13), (1, 25), (10, 18), (9, 17), (2, 26), (12, 20), (3, 27), (4, 28), (11, 19), 
   (16, 33), (36, 50), (8, 36), (24, 34), (42, 50), (35, 52), (37, 53), (30, 41), (40, 57), 
   (13, 38), (33, 38), (30, 31), (7, 60), (22, 59), (21, 63), (8, 17), (54, 65), (50, 55), 
   (53, 67), (39, 46), (5, 69), (20, 41), (29, 59), (58, 72), (18, 44), (45, 74), (9, 43), 
   (25, 75), (76, 77), (7, 35), (40, 79), (4, 71), (70, 81), (1, 26), (76, 83), (48, 81), 
   (29, 85), (21, 48), (41, 87), (60, 61), (14, 89), (42, 43), (2, 91), (38, 39), (14, 93), 
   (22, 61), (34, 95), (1, 44), (36, 97), (32, 98), (53, 54), (32, 100), (9, 101), (20, 49), 
   (33, 48), (103, 104), (54, 68), (35, 106), (97, 107), (3, 49), (34, 109), (32, 45), 
   (109, 111), (32, 46), (47, 113), (19, 110), (4, 114), (105, 114), (115, 117), (28, 46), 
   (115, 119), (19, 33), (43, 121), (47, 122), (2, 110), (10, 124), (47, 125), (27, 122), 
   (111, 127), (125, 128)]

/-- The circuit uses exactly 98 XOR gates. -/
theorem gate_count : prog.length = 98 := by rfl

/-- MAIN RESULT: the circuit is well formed and computes every target. -/
theorem cert : SLP.valid n targets prog = true := by decide

-- Trust base. An empty axiom list means the kernel checked everything.
#print axioms cert
#print axioms gate_count

end CertAesmixcolumns