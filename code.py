import logging
import random
from tenacity import ( Retrying, stop_after_attempt,wait_exponential,retry_if_exception_type, before_sleep_log)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class NetworkTempError(Exception): pass
class RateLimitError(Exception): pass
class AuthError(Exception): pass

def call_unreliable_api():
    chance = random.random()
    if chance < 0.4:
        logger.error("[API] lỗi: máy chủ từ chối kết nối")
        raise NetworkTempError("mạng không khả dụng")
    elif chance < 0.7:
        logger.warning("[API] lỗi: Máy chủ đang quá tải")
        raise RateLimitError("Hệ thống quá tải")
    elif chance > 0.95:
        logger.error("[API] lỗi: token không hợp lệ")
        raise AuthError("sai thông tin xác thực")
        
    return {"status": "success", "data": "dữ liệu lấy thành công từ API"}


def main():
    print("hệ thống đồng bộ dữ liệu ")
    while True:
        try:
            user_input = input("nhập số lần thử tối đa: ")
            max_attempts = int(user_input)
            if max_attempts <= 0:
                print("nhập một số lớn hơn 0")
                continue
            break
        except ValueError:
            print("lỗi:chỉ nhập số nguyên")

    print(f"\n đã thiết lập giới hạn: Sẽ từ bỏ sau {max_attempts} lần\n")
    

    
    retry_policy = Retrying(
        stop=stop_after_attempt(max_attempts), 
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=(retry_if_exception_type(NetworkTempError) | retry_if_exception_type(RateLimitError)),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )

    try:
        
        result = retry_policy(call_unreliable_api)
        print("trả kết quả: ")
        print(result)
        
        
    except Exception as e:
        print(f"lỗi hệ thống từ bỏ sau {max_attempts} lần hoặc gặp lỗi logic")
        print(f"chi tiết lỗi cuối cùng: {type(e).__name__} - {e}")

if __name__ == "__main__":
    main()
