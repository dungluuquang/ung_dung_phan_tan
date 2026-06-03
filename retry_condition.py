from tenacity import retry, retry_if_exception_type, retry_if_result, stop_after_attempt


class ConnectionError(Exception): pass
class AuthError(Exception): pass

# chỉ thử lại nếu gặp lỗi mạng. Lỗi khác (như AuthError) sẽ văng ra luôn.
@retry(stop=stop_after_attempt(3), retry=retry_if_exception_type(ConnectionError))
def retry_on_specific_exception(error_type):
    print(f"đang gọi API, giả lập ném ra lỗi: {error_type.__name__}")
    raise error_type("Có lỗi xảy ra!")

# hàm kiểm tra kết quả. Trả về True nếu kết quả là 503 (cần retry)
def is_status_503(result):
    return result == 503

# thử lại nếu hàm trả về số 503
@retry(stop=stop_after_attempt(3), retry=retry_if_result(is_status_503))
def retry_on_specific_result():
    print("hàm chạy bình thường nhưng API trả về HTTP Status 503 (Quá tải). Sẽ retry...")
    return 503 # trả về 503 thay vì raise Exception



# thử lỗi mạng nếu được truyền vào ConnectionError -> sẽ retry 3 lần
try:

    retry_on_specific_exception(ConnectionError)
except Exception:
    print("thử đủ 3 lần với ConnectionError.")

# Truyền vào AuthError -> Hàm ném lỗi và kết thúc ngay lập tức (không retry)
try:
    retry_on_specific_exception(AuthError)
except Exception as e:
    print(f" Dừng ngay lập tức! bắt được lỗi không nằm trong danh sách retry: {type(e).__name__}")

print("\nlọc theo Kết quả trả về (HTTP Status)")
result = retry_on_specific_result()
print(f"kết thúc. Giá trị cuối cùng nhận được: {result}")
