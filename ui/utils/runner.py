"""
utils/runner.py

Stub module standing in for the eventual call into the ranking backend.
Nothing here actually executes rank.py — it only simulates the UX
(spinner + progress bar + success message) referenced on the Upload page.

# TODO:
# Replace `simulate_ranking_run()` with a real call into rank.py, e.g.:
#
#     from rank import run_ranking_pipeline
#     results_df = run_ranking_pipeline(dataset_path)
#
# and then:
#     # TODO: Load submission.csv
#     # TODO: Display ranked candidates
"""

import time
from typing import Callable, Optional


def simulate_ranking_run(on_progress: Optional[Callable[[int], None]] = None) -> None:
    """Simulate a ranking run for UI demo purposes only.

    on_progress: optional callback invoked with an int 0-100 so the
    calling page can drive a st.progress() bar.
    """
    steps = 20
    for i in range(steps + 1):
        time.sleep(0.04)
        if on_progress:
            on_progress(int((i / steps) * 100))

    # TODO:
    # Execute rank.py after dataset upload
    # TODO:
    # Load submission.csv
    # TODO:
    # Display ranked candidates
    return None
