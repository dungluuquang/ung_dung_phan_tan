from tenacity import retry, stop_after_attempt, stop_after_delay
import time

# dừng sau tối đa 3 lần thử
@retry(stop=stop_after_attempt(3))
def stop_after_3_tries():
    print(f"[{time.strftime('%X')}] Đang thử (chỉ thử tối đa 3 lần)...")
    raise Exception("Lỗi hệ thống luôn xảy ra!")

# dừng sau khi đã trôi qua 2 giây kể từ lần thử đầu tiên
@retry(stop=stop_after_delay(2))
def stop_after_2_seconds():
    print(f"[{time.strftime('%X')}] Đang thử (sẽ từ bỏ sau 2 giây)...")
    time.sleep(0.6) # Giả lập hàm mất 0.6s để chạy
    raise Exception("Lỗi timeout!")


try:
    print("test: dừng sau 3 lần thử")
    stop_after_3_tries()
except Exception as e:
    print("đã vượt quá 3 lần thử, chương trình bắt được lỗi cuối cùng.\n")

try:
    print("Test: dừng sau 2 giây")
    stop_after_2_seconds()
except Exception as e:
    print(" hết 2 giây, chương trình bắt được lỗi cuối cùng.")
print("-" * 40)
