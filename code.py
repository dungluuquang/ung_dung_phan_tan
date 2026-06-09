import logging
import random
import uuid
from tenacity import ( Retrying,stop_after_attempt, stop_after_delay,wait_random_exponential,retry_if_exception_type,before_sleep_log,)


logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-8s | %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)



# lỗi được retry 
class NetworkTempError(Exception): pass
class RateLimitError(Exception): pass
class DatabaseTimeoutError(Exception): pass

# lỗi Logic không Retry 
class AuthError(Exception): pass
class DataFormatError(Exception): pass   


# fallback

def fallback_handler(retry_state):
    """hàm sẽ được gọi khi tất cả các lần thử đều thất bại hoặc khi đạt đến giới hạn thời gian"""
    exception = retry_state.outcome.exception()
    logger.critical(f"hệ thống sập sau {retry_state.attempt_number} lần thử")
    logger.critical(f"chi tiết lỗi cuối cùng: {type(exception).__name__} - {exception}")
    
    logger.info("đang nạp dữ liệu dự phòng từ local cache")
    return {
        "status": "warning_fallback", 
        "data": "dữ liệu ngoại tuyến-lần cập nhật cuối: Hôm qua"
    }


# mô phỏng API không ổn định với nhiều loại lỗi khác nhau
def call_unreliable_api(headers):
    trace_id = headers.get("Trace-ID")
    idemp_key = headers.get("Idempotency-Key")
    
    logger.debug(f"Đang gửi Request | Trace-ID: {trace_id} | Idemp-Key: {idemp_key}")
    
    chance = random.random()
    
    # 20% lỗi mạng
    if chance < 0.2:
        logger.error("API máy chủ từ chối kết nối")
        raise NetworkTempError("Network Down")
        
    # 20% lỗi quá tải
    elif chance < 0.4:
        logger.warning("API máy chủ quá tải")
        raise RateLimitError("rate limit exceeded")
        
    # 20% lỗi database phản hồi chậm 
    elif chance < 0.6:
        logger.error("API cơ sở dữ liệu đích phản hồi quá chậm (Timeout)")
        raise DatabaseTimeoutError("DB Timeout")
        
    # 10% Lỗi định dạng dữ liệu (THÊM MỚI - LỖI LOGIC)
    elif chance < 0.7:
        logger.error("API dữ liệu trả về bị hỏng/không đúng chuẩn JSON")
        raise DataFormatError("Bad Data Format")
        
    # 5% Lỗi Token (LỖI LOGIC)
    elif chance > 0.95:
        logger.error("API token xác thực hết hạn (HTTP 401)!")
        raise AuthError("Unauthorized Token")
        
    # 25% Thành công
    return {"status": "thành công", "data": "dữ liệu trực tiếp từ API - lần cập nhật cuối: vài giây trước"}

def main():
    print("hệ thống mô phỏng API không ổn định với retry")
    while True:
        try:
            max_attempts = int(input("nhập số lần thử tối đa: "))
            if max_attempts > 0: break
        except ValueError:
            print("nhập số nguyên!")

    #theo dõi từng request bằng trace-id và idempotency-key để dễ dàng debug và phân tích 
    request_headers = {
        "Trace-ID": f"trace-{uuid.uuid4().hex[:8]}",
        "Idempotency-Key": f"idemp-{uuid.uuid4().hex[:8]}"
    }

    print(f"\ntối đa {max_attempts} lần thử hoặc 15 giây chờ")
    

    # retry
    retry_policy = Retrying(
        stop=(stop_after_attempt(max_attempts) | stop_after_delay(15)),
        wait=wait_random_exponential(multiplier=1, min=1, max=10),
        
        # lọc lỗi gom 3 lỗi hệ thống vào diện được phép Retry
        retry=
        (
            retry_if_exception_type(NetworkTempError) | 
            retry_if_exception_type(RateLimitError) |
            retry_if_exception_type(DatabaseTimeoutError)
        ),
        
        before_sleep=before_sleep_log(logger, logging.WARNING),
        retry_error_callback=fallback_handler
    )

    try:
        # chạy hàm qua policy
        result = retry_policy(call_unreliable_api, request_headers)
        
        
        print("kết quả:")
        print(f"trạng thái: {result['status']}")
        print(f"dữ liệu   : {result['data']}")
       
        
    except AuthError as e:
        # Xử lý nhanh lỗi bảo mật (không Retry, không Fallback)
        
        print(f"lỗi bảo mật,yêu cầu đăng nhập lại({e})")
       
        
    except DataFormatError as e:
        # xử lý nhanh lỗi định dạng (không Retry, không Fallback)
        print("\n" + "="*75)
        print(f"dữ liệu API bị hỏng cấu trúc ({e})")
        print("=" * 75 + "\n")

if __name__ == "__main__":
    main()
