import subprocess
import sys

print("Running DailySOC Digest pipeline...\n")

steps = [
    ["python", "src/main.py"],
    ["python", "src/dashboard.py"]
]

for step in steps:
    result = subprocess.run(step)
    if result.returncode != 0:
        print("SOC pipeline failed")
        sys.exit(1)

print("\nSOC pipeline completed successfully")
