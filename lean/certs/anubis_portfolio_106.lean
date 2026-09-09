/-
  Machine-checkable certificate for a Shortest Linear Straight-Line Program.

  Instance    : anubis
  Fingerprint : e91a060b2ec0d36f
  Inputs      : 32 variables over GF(2)
  Outputs     : 32 linear forms
  Gate count  : 106 XOR gates
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

    lean lean/certs/anubis_portfolio_106.lean

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
  [(22, 30), (6, 14), (15, 31), (23, 31), (7, 15), (32, 34), (33, 34), (7, 23), (11, 36), 
   (27, 35), (18, 37), (9, 38), (8, 24), (0, 16), (6, 22), (21, 29), (14, 30), (5, 13), 
   (33, 39), (19, 36), (26, 42), (4, 41), (3, 12), (21, 28), (20, 55), (4, 12), (40, 54), 
   (29, 57), (5, 57), (19, 53), (1, 43), (10, 51), (32, 39), (25, 36), (2, 41), (17, 65), 
   (0, 8), (10, 64), (1, 17), (16, 24), (0, 37), (45, 65), (24, 50), (8, 64), (55, 58), 
   (16, 38), (20, 59), (58, 78), (22, 59), (13, 80), (11, 52), (26, 67), (53, 82), (25, 67), 
   (44, 85), (3, 83), (69, 87), (46, 49), (31, 89), (15, 47), (46, 91), (5, 14), (56, 93), 
   (13, 61), (20, 95), (51, 54), (52, 97), (28, 60), (61, 99), (62, 63), (26, 101), (36, 48), 
   (91, 103), (23, 49), (48, 105), (30, 60), (21, 107), (69, 70), (71, 109), (1, 44), 
   (35, 111), (9, 45), (35, 113), (62, 66), (18, 115), (82, 83), (2, 117), (25, 43), (2, 50), 
   (18, 119), (68, 121), (68, 70), (50, 123), (26, 124), (89, 100), (81, 96), (126, 127), 
   (3, 63), (120, 129), (28, 130), (29, 79), (61, 130), (132, 133), (71, 120), (64, 135), 
   (119, 136)]

/-- The circuit uses exactly 106 XOR gates. -/
theorem gate_count : prog.length = 106 := by rfl

/-- MAIN RESULT: the circuit is well formed and computes every target. -/
theorem cert : SLP.valid n targets prog = true := by decide

-- Trust base. An empty axiom list means the kernel checked everything.
#print axioms cert
#print axioms gate_count

end CertAnubis