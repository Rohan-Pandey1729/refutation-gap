/-
  Machine-checkable certificate for a Shortest Linear Straight-Line Program.

  Instance    : aes_mixcolumns
  Fingerprint : a12ac93d743531f4
  Inputs      : 32 variables over GF(2)
  Outputs     : 32 linear forms
  Gate count  : 108 XOR gates
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

    lean lean/certs/aes_mixcolumns_paar1.lean

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
  [(7, 15), (23, 31), (7, 31), (15, 23), (0, 8), (1, 9), (2, 10), (3, 11), (4, 12), (5, 13), 
   (6, 14), (16, 24), (17, 25), (18, 26), (19, 27), (20, 28), (21, 29), (22, 30), (8, 32), 
   (50, 43), (9, 32), (52, 36), (53, 44), (10, 37), (55, 45), (11, 32), (57, 38), (58, 46), 
   (12, 32), (60, 39), (61, 47), (13, 40), (63, 48), (14, 41), (65, 49), (15, 33), (67, 42), 
   (0, 35), (69, 43), (1, 8), (71, 16), (72, 35), (73, 44), (2, 9), (75, 17), (76, 45), 
   (3, 10), (78, 18), (79, 35), (80, 46), (4, 11), (82, 19), (83, 35), (84, 47), (5, 12), 
   (86, 20), (87, 48), (6, 13), (89, 21), (90, 49), (7, 14), (92, 22), (93, 33), (24, 33), 
   (95, 36), (25, 33), (97, 37), (98, 43), (26, 38), (100, 44), (27, 33), (102, 39), (103, 45), 
   (28, 33), (105, 40), (106, 46), (29, 41), (108, 47), (30, 42), (110, 48), (31, 32), 
   (112, 49), (16, 34), (114, 36), (0, 17), (116, 24), (117, 34), (118, 37), (1, 18), 
   (120, 25), (121, 38), (2, 19), (123, 26), (124, 34), (125, 39), (3, 20), (127, 27), 
   (128, 34), (129, 40), (4, 21), (131, 28), (132, 41), (5, 22), (134, 29), (135, 42), (6, 23), 
   (137, 30), (138, 32)]

/-- The circuit uses exactly 108 XOR gates. -/
theorem gate_count : prog.length = 108 := by rfl

/-- MAIN RESULT: the circuit is well formed and computes every target. -/
theorem cert : SLP.valid n targets prog = true := by decide

-- Trust base. An empty axiom list means the kernel checked everything.
#print axioms cert
#print axioms gate_count

end CertAesmixcolumns