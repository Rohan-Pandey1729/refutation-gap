/-
  Machine-checkable certificate for a Shortest Linear Straight-Line Program.

  Instance    : anubis
  Fingerprint : e91a060b2ec0d36f
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

    lean lean/certs/anubis_paar1.lean

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
  [(6, 14), (22, 30), (1, 23), (3, 15), (7, 11), (9, 31), (0, 15), (2, 32), (7, 8), (17, 33), 
   (19, 23), (27, 31), (2, 25), (4, 12), (4, 20), (5, 13), (5, 21), (6, 22), (7, 10), (10, 35), 
   (12, 28), (13, 29), (14, 30), (15, 16), (15, 18), (17, 40), (18, 31), (19, 26), (20, 28), 
   (21, 29), (23, 26), (24, 34), (25, 38), (27, 56), (32, 37), (35, 36), (42, 43), (31, 33), 
   (69, 38), (8, 31), (71, 63), (24, 33), (73, 37), (74, 44), (75, 55), (25, 41), (77, 51), 
   (78, 62), (4, 11), (80, 33), (81, 62), (82, 65), (5, 52), (84, 68), (6, 53), (86, 60), 
   (7, 54), (88, 61), (23, 33), (90, 40), (0, 16), (92, 23), (93, 37), (16, 41), (95, 50), 
   (96, 63), (36, 41), (98, 44), (99, 58), (3, 7), (101, 12), (102, 33), (103, 58), (104, 59), 
   (13, 46), (106, 68), (14, 48), (108, 60), (15, 49), (110, 61), (31, 32), (112, 55), 
   (15, 24), (114, 57), (8, 18), (116, 64), (117, 66), (1, 50), (119, 59), (120, 66), (10, 20), 
   (122, 36), (123, 39), (124, 43), (21, 52), (126, 67), (22, 45), (128, 53), (23, 47), 
   (130, 54), (7, 23), (132, 24), (133, 32), (7, 16), (135, 64), (0, 26), (137, 32), (138, 34), 
   (139, 57), (9, 34), (141, 39), (142, 65), (28, 39), (144, 42), (145, 51), (29, 46), 
   (147, 67), (30, 45), (149, 48), (31, 47), (151, 49)]

/-- The circuit uses exactly 121 XOR gates. -/
theorem gate_count : prog.length = 121 := by rfl

/-- MAIN RESULT: the circuit is well formed and computes every target. -/
theorem cert : SLP.valid n targets prog = true := by decide

-- Trust base. An empty axiom list means the kernel checked everything.
#print axioms cert
#print axioms gate_count

end CertAnubis