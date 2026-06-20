"""
Latency metric: Measures execution time.
"""
import time
from typing import Callable

class LatencyMetric:
    """
    Utility class to measure execution latency.
    """
    
    @staticmethod
    def measure(func: Callable) -> tuple:
        """
        Executes a function and returns (result, latency_in_seconds).
        """
        start_time = time.perf_counter()
        result = func()
        end_time = time.perf_counter()
        latency = end_time - start_time
        return result, latency
