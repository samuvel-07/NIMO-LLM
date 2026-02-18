# brain/thresholds.py

# Confidence Thresholds
EXECUTION_THRESHOLD = 0.80
CLARIFICATION_THRESHOLD = 0.60
DANGEROUS_THRESHOLD = 0.92

# High-Risk Skills (Require higher confidence or confirmation)
DANGEROUS_SKILLS = {
    "shutdown_system",
    "delete_files",
    "format_drive",
    "kill_process"
}
