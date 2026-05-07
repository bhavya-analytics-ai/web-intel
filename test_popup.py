"""Quick popup test — run this directly to see the popup."""
import time
from web_intel.popup import log_usage, log_error

print("Sending test stats to popup...")
log_usage("https://example.com", 1243, 87)

time.sleep(2)

log_usage("https://apple.com/about", 2100, 120)

time.sleep(2)

log_error("https://broken.com", "scrape failed", "Connection timed out after 30s")

print("Keeping popup alive for 10 seconds...")
time.sleep(10)
print("Done.")
