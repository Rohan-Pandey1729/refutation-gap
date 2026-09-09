#!/usr/bin/env python3
"""Train and evaluate a learned distance oracle.

The label is free: the exact oracle that Boyar-Peralta already runs produces it.
Training data comes from scripts/collect_oracle_data.py.

METRIC NOTE. The oracle answers "no" ~96% of the time, so accuracy is a useless
headline number -- a constant "no" scores 96%. What matters operationally:

  - recall on positives : a missed positive costs the outer search one extra gate
  - precision          : a false positive makes the search take a step that does
                         not actually reduce the distance; it cannot produce a
                         wrong circuit, because the verifier is downstream
  - inference cost     : the whole point is to be cheaper than the DFS it replaces
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from slp.instance import apply_program
from slp.oracle.features import FEATURE_NAMES, featurize_batch


def load_dataset(paths, max_records=None):
    X, y, groups = [], [], []
    for path in paths:
        d = np.load(path, allow_pickle=True)
        n = int(d["n_inputs"])
        progs = d["programs"]
        rep, step, xs, budget, label = (d["rep"], d["step"], d["x"],
                                        d["budget"], d["label"])
        keep = label >= 0                      # drop capped/unlabelled
        rep, step, xs, budget, label = (rep[keep], step[keep], xs[keep],
                                        budget[keep], label[keep])
        order = np.lexsort((step, rep))
        rep, step, xs, budget, label = (rep[order], step[order], xs[order],
                                        budget[order], label[order])
        # group by (rep, step): the added-set is constant within a group
        key = rep.astype(np.int64) * 100000 + step.astype(np.int64)
        bounds = np.flatnonzero(np.diff(key)) + 1
        for lo, hi in zip(np.r_[0, bounds], np.r_[bounds, len(key)]):
            r, s = int(rep[lo]), int(step[lo])
            prog = [tuple(op) for op in progs[r][:s]]
            sigs = apply_program(n, prog)
            added = np.array(sigs[n:], dtype=np.uint64)
            X.append(featurize_batch(n, added, xs[lo:hi].astype(np.uint64),
                                     budget[lo:hi].astype(np.int16)))
            y.append(label[lo:hi])
            groups.append(np.full(hi - lo, hash(Path(path).stem) & 0xFFFF))
        if max_records and sum(len(a) for a in y) > max_records:
            break
    return (np.concatenate(X), np.concatenate(y).astype(np.int8),
            np.concatenate(groups))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/oracle")
    ap.add_argument("--holdout-frac", type=float, default=0.3)
    ap.add_argument("--max-iter", type=int, default=300)
    ap.add_argument("--out", default="models/oracle.joblib")
    args = ap.parse_args()

    paths = sorted(Path(args.data).glob("*.npz"))
    if not paths:
        print(f"no data in {args.data}", file=sys.stderr)
        return 2

    # Hold out whole INSTANCES, not random rows: the question is whether the
    # oracle generalises to a matrix it has never seen, not whether it can
    # memorise queries from a matrix it has.
    n_hold = max(1, int(len(paths) * args.holdout_frac))
    train_paths, test_paths = paths[:-n_hold], paths[-n_hold:]
    print(f"train instances: {len(train_paths)}   held-out instances: {len(test_paths)}")
    print(f"held out: {[p.stem for p in test_paths]}")

    t0 = time.time()
    Xtr, ytr, _ = load_dataset(train_paths)
    Xte, yte, _ = load_dataset(test_paths)
    print(f"train {Xtr.shape}  test {Xte.shape}  ({time.time()-t0:.1f}s to featurize)")
    print(f"positive rate: train {ytr.mean():.4f}  test {yte.mean():.4f}")

    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.metrics import (average_precision_score, precision_recall_curve,
                                 roc_auc_score)

    clf = HistGradientBoostingClassifier(
        max_iter=args.max_iter, learning_rate=0.1, max_leaf_nodes=63,
        l2_regularization=1.0, early_stopping=True, validation_fraction=0.1,
        random_state=0)
    t0 = time.time()
    clf.fit(Xtr, ytr)
    train_s = time.time() - t0

    t0 = time.time()
    p = clf.predict_proba(Xte)[:, 1]
    infer_s = time.time() - t0
    per_query_us = infer_s / len(Xte) * 1e6

    base_acc = 1.0 - yte.mean()
    auc = roc_auc_score(yte, p)
    ap_score = average_precision_score(yte, p)
    prec, rec, thr = precision_recall_curve(yte, p)

    print(f"\ntrained in {train_s:.1f}s")
    print(f"inference: {per_query_us:.2f} us/query  ({len(Xte):,d} queries in {infer_s:.2f}s)")
    print(f"\nconstant-'no' accuracy baseline : {base_acc:.4f}")
    print(f"model accuracy @0.5             : {((p>0.5).astype(int)==yte).mean():.4f}")
    print(f"ROC AUC                         : {auc:.4f}")
    print(f"average precision (PR AUC)      : {ap_score:.4f}   (chance = {yte.mean():.4f})")

    print(f"\n{'threshold':>10s} {'recall':>8s} {'precision':>10s} {'flagged/query':>14s}")
    for target_recall in (0.99, 0.95, 0.90, 0.80, 0.50):
        idx = np.searchsorted(-rec, -target_recall)
        idx = min(idx, len(thr) - 1)
        t = thr[idx]
        sel = p >= t
        print(f"{t:10.4f} {rec[idx]:8.4f} {prec[idx]:10.4f} {sel.mean():14.4f}")

    imp = sorted(zip(FEATURE_NAMES, clf.feature_importances_
                     if hasattr(clf, "feature_importances_") else [0]*len(FEATURE_NAMES)),
                 key=lambda kv: -kv[1])[:10] if hasattr(clf, "feature_importances_") else []
    if imp:
        print("\ntop features:")
        for name, v in imp:
            print(f"  {name:26s} {v:.4f}")

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    import joblib
    joblib.dump({"model": clf, "feature_names": FEATURE_NAMES}, args.out)
    print(f"\nsaved {args.out}")

    metrics = {"base_acc": float(base_acc), "auc": float(auc),
               "avg_precision": float(ap_score), "pos_rate": float(yte.mean()),
               "per_query_us": float(per_query_us), "train_seconds": float(train_s),
               "n_train": int(len(ytr)), "n_test": int(len(yte)),
               "held_out": [p.stem for p in test_paths]}
    Path("runs/oracle_metrics.json").write_text(json.dumps(metrics, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
