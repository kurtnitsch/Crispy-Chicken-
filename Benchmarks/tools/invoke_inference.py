import time, random, sys
verified = "--verified" in sys.argv
time.sleep(random.uniform(0.01,0.03) if not verified else random.uniform(0.5,0.6))
