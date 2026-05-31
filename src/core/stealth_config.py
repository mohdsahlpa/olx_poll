import random
import math

# CURATED BROWSER PROFILES
# Synchronized User-Agents and Client Hints (Sec-CH-UA)
BROWSER_PROFILES = [
    {
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "client_hints": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        "platform": '"Windows"'
    },
    {
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "client_hints": '"Google Chrome";v="124", "Chromium";v="124", "Not.A/Brand";v="24"',
        "platform": '"macOS"'
    },
    {
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "client_hints": '"Google Chrome";v="123", "Chromium";v="123", "Not.A/Brand";v="24"',
        "platform": '"Linux"'
    }
]

def get_stealth_profile():
    """Returns a synchronized User-Agent and Client Hints profile."""
    return random.choice(BROWSER_PROFILES)

def get_poisson_interval(mean: float) -> float:
    """
    Returns a jittered interval based on Poisson distribution.
    Creates truly 'human' intervals centered around the mean.
    """
    # Using Knuth's algorithm for Poisson-like jitter
    L = math.exp(-mean)
    k = 0
    p = 1.0
    while p > L:
        k += 1
        p *= random.random()
    
    # Ensure we stay within a reasonable range (0.5x to 2x of mean)
    val = max(mean * 0.5, min(mean * 2.0, float(k)))
    return val
