from tenacity import retry
import time

attempts_2_1 = 0

@retry
def simple_retry_demo():
    global attempts_2_1
    attempts_2_1 += 1
    print(f"[{time.strftime('%X')}] lần thử thứ {attempts_2_1}...")
    
    # Giả lập lỗi ở 3 lần đầu, lần thứ 4 mới thành công
    if attempts_2_1 < 4:
        print("  lỗi! Tenacity sẽ tự động gọi lại hàm này.")
        raise Exception("Lỗi tạm thời")
        
    print("    Thành công!")
    return "Dữ liệu lấy thành công"

print("thử retry")
simple_retry_demo()
print("-" * 40)
