/-
  Machine-checkable certificate for a Shortest Linear Straight-Line Program.

  Instance    : anubis
  Fingerprint : e91a060b2ec0d36f
  Inputs      : 32 variables over GF(2)
  Outputs     : 32 linear forms
  Gate count  : 105 XOR gates
  Produced by : portfolio k=400 mode=1 seed=805311476
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

    lean lean/certs/anubis_best_105.lean

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
  [(6, 14), (22, 30), (7, 15), (7, 23), (15, 31), (3, 34), (23, 31), (32, 35), (33, 36), 
   (27, 38), (33, 35), (32, 36), (18, 40), (9, 43), (8, 24), (0, 16), (17, 34), (14, 30), 
   (21, 29), (6, 22), (5, 13), (18, 45), (21, 28), (11, 37), (4, 20), (19, 41), (5, 12), 
   (4, 58), (20, 54), (11, 44), (12, 55), (26, 61), (2, 41), (28, 57), (0, 8), (25, 48), 
   (39, 64), (10, 68), (10, 26), (1, 17), (16, 24), (24, 39), (0, 40), (46, 48), (8, 42), 
   (16, 43), (58, 65), (54, 62), (9, 47), (38, 80), (38, 46), (1, 82), (55, 56), (29, 84), 
   (47, 67), (17, 86), (42, 72), (19, 62), (63, 89), (31, 51), (52, 91), (37, 69), (65, 93), 
   (10, 88), (71, 95), (14, 60), (5, 97), (15, 50), (51, 99), (7, 49), (50, 101), (1, 64), 
   (53, 103), (30, 59), (21, 105), (50, 52), (23, 52), (49, 108), (13, 57), (56, 110), (2, 67), 
   (61, 112), (33, 107), (106, 114), (20, 69), (11, 116), (32, 98), (107, 118), (53, 66), 
   (25, 120), (41, 63), (4, 122), (2, 81), (87, 88), (124, 125), (42, 70), (3, 127), (67, 128), 
   (39, 71), (26, 66), (130, 131), (48, 70), (71, 133), (45, 134), (19, 135)]

/-- The circuit uses exactly 105 XOR gates. -/
theorem gate_count : prog.length = 105 := by rfl

/-- MAIN RESULT: the circuit is well formed and computes every target. -/
theorem cert : SLP.valid n targets prog = true := by decide

-- Trust base. An empty axiom list means the kernel checked everything.
#print axioms cert
#print axioms gate_count

end CertAnubis