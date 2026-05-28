#!/usr/bin/env python3
"""Quick prediction verification wrapper.
Usage: python3 verify_predictions.py [date]

Reads market data cache and runs verification against predictions.
"""
import sys
import os

# Ensure scripts dir is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Also add the amadeus scripts dir
sys.path.insert(0, os.path.expanduser("~/.hermes/scripts/amadeus"))

from datetime import date, timedelta

def main():
    verify_date = sys.argv[1] if len(sys.argv) > 1 else str(date.today())
    
    # Run verification
    os.system(f"python3 ~/.hermes/scripts/amadeus/amadeus_predictions.py verify")
    
    # Show stats
    print("\n--- Stats ---")
    os.system(f"python3 ~/.hermes/scripts/amadeus/amadeus_predictions.py stats")

if __name__ == "__main__":
    main()
