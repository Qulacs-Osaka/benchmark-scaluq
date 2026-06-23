# Default thread count when run standalone (execall.sh exports its own value).
: "${OMP_NUM_THREADS:=96}"
export OMP_NUM_THREADS

rm -f "$1.json"
# Write pytest output to a log file instead of the terminal, so the run is immune
# to a broken stdout/stderr pipe (e.g. SSH dropping while zellij is detached).
# Follow progress with: tail -f "$1.log"
PYTHONUNBUFFERED=1 uv run python -m pytest "$1.py" --benchmark-json="$1.json" --benchmark-min-rounds=5 -q > "$1.log" 2>&1
