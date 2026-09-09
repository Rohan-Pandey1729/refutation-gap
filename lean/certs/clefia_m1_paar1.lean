/-
  Machine-checkable certificate for a Shortest Linear Straight-Line Program.

  Instance    : clefia_m1
  Fingerprint : 60591a0ce16495fa
  Inputs      : 32 variables over GF(2)
  Outputs     : 32 linear forms
  Gate count  : 121 XOR gates
  Produced by : paar1
  Source run  : ciphers_paar_corrected

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

    lean lean/certs/clefia_m1_paar1.lean

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
  [(5, 21), (6, 22), (13, 29), (14, 30), (2, 7), (3, 23), (7, 31), (10, 15), (26, 31), 
   (32, 33), (34, 35), (11, 15), (15, 23), (18, 23), (0, 8), (0, 16), (1, 9), (1, 17), (4, 12), 
   (4, 20), (5, 13), (6, 14), (7, 15), (7, 19), (8, 24), (9, 25), (12, 28), (16, 24), (17, 25), 
   (19, 27), (20, 28), (21, 29), (22, 30), (23, 31), (27, 31), (33, 36), (35, 39), (36, 39), 
   (37, 55), (40, 68), (41, 47), (41, 49), (42, 56), (42, 57), (43, 66), (45, 67), (0, 34), 
   (78, 65), (1, 35), (80, 59), (2, 34), (82, 44), (83, 60), (18, 37), (85, 40), (86, 74), 
   (4, 44), (88, 61), (89, 75), (5, 62), (91, 71), (6, 63), (93, 76), (7, 58), (95, 64), 
   (8, 32), (97, 65), (9, 33), (99, 59), (10, 32), (101, 38), (102, 60), (11, 40), (104, 45), 
   (105, 72), (12, 38), (107, 61), (108, 73), (13, 62), (110, 77), (14, 63), (112, 70), 
   (15, 51), (114, 64), (16, 34), (116, 54), (17, 35), (118, 46), (18, 34), (120, 38), 
   (121, 48), (19, 69), (123, 74), (3, 11), (125, 20), (126, 38), (127, 75), (21, 50), 
   (129, 71), (22, 52), (131, 76), (23, 53), (133, 58), (24, 32), (135, 54), (25, 33), 
   (137, 46), (26, 32), (139, 44), (140, 48), (27, 69), (142, 72), (28, 37), (144, 43), 
   (145, 73), (29, 50), (147, 77), (30, 52), (149, 70), (31, 51), (151, 53)]

/-- The circuit uses exactly 121 XOR gates. -/
theorem gate_count : prog.length = 121 := by rfl

/-- MAIN RESULT: the circuit is well formed and computes every target. -/
theorem cert : SLP.valid n targets prog = true := by decide

-- Trust base. An empty axiom list means the kernel checked everything.
#print axioms cert
#print axioms gate_count

end CertClefiam1