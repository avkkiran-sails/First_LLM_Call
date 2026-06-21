import json
import os

CHECKPOINT_FILE = "checkpoint.json"

def save_checkpoint(step: int, accumulated: list) -> None:
    """Persist current progress to disk."""
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump({"step": step, "accumulated": accumulated}, f)

def load_checkpoint() -> tuple[int, list]:
    """Return (start_step, results_so_far) from disk, or (0, []) if none exists."""
    if os.path.exists(CHECKPOINT_FILE):
        data = json.load(open(CHECKPOINT_FILE))
        print(f"Resuming from step {data['step'] + 1}")
        return data["step"] + 1, data["accumulated"]
    print("No checkpoint found — starting from step 0")
    return 0, []

def run_pipeline(items: list[str]) -> list[str]:
    start, results = load_checkpoint()
    for i in range(start, len(items)):
        processed = items[i].upper()   # replace with your real per-item logic
        results.append(processed)
        save_checkpoint(i, results)    # write after every completed step
    return results

items = ["alpha", "beta", "gamma", "delta", "epsilon"]

output = run_pipeline(items)
print("Final output:", output)

# To verify resume: delete checkpoint.json, run again, interrupt with
# Ctrl-C after at least two steps, then run a third time — the output
# should begin with "Resuming from step N" and the final list should
# match the output from the uninterrupted first run.