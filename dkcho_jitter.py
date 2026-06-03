from tenacity import retry, wait_fixed, wait_exponential, wait_random_exponential, stop_after_attempt
import time

# chờ cố định 2 giây giữa các lần thử
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def wait_fixed_demo():
    print(f"[{time.strftime('%X')}] hàm chạy lỗi, sẽ chờ 2s rồi thử lại...")
    raise Exception("Lỗi")

# chờ cấp số nhân (2^x): 2s, 4s... (tối đa 10s)
@retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=1, min=2, max=10))
def wait_exponential_demo():
    print(f"[{time.strftime('%X')}] hàm chạy lỗi, sẽ chờ theo cấp số nhân...")
    raise Exception("Lỗi")

# chờ cấp số nhân kết hợp Jitter (độ nhiễu ngẫu nhiên) để tránh bão request
@retry(stop=stop_after_attempt(5), wait=wait_random_exponential(multiplier=1, max=10))
def wait_jitter_demo():
    print(f"[{time.strftime('%X')}] hàm chạy lỗi, thời gian chờ sẽ được cộng thêm Jitter ngẫu nhiên...")
    raise Exception("Lỗi")


try:
    print("\n Test: Wait Fixed (Chờ 2s)")
    wait_fixed_demo()
except Exception: pass

try:
    print("\nTest: Wait Exponential")
    wait_exponential_demo()
except Exception: pass

try:
    
    wait_jitter_demo()
except Exception: pass
print("-" * 40)
