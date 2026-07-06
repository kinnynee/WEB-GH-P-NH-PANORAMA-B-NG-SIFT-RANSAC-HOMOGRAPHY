# Panorama Vision Studio

Ứng dụng Streamlit dùng để ghép 2-4 ảnh chồng lấp thành ảnh panorama. Dự án minh họa pipeline xử lý ảnh gồm SIFT, Feature Matching, Lowe Ratio Test, RANSAC, Homography, Warping và Blending.

## Yêu Cầu

- Python 3.11 trở lên
- pip
- Trình duyệt web

## Cài Đặt

Mở terminal tại thư mục dự án:

```bash
cd C:\kiba\Panorama
```

Cài các thư viện cần thiết:

```bash
pip install -r requirements.txt
```

## Chạy Ứng Dụng

Chạy lệnh:

```bash
streamlit run app.py
```

Sau đó mở URL Streamlit hiển thị trong terminal, thường là:

```text
http://localhost:8501
```

## Cách Sử Dụng

1. Vào trang `Workspace`.
2. Bấm `Upload Images` và chọn từ 2 đến 4 ảnh JPG, JPEG hoặc PNG.
3. Sắp xếp ảnh theo thứ tự từ trái sang phải bằng nút `Left` và `Right`.
4. Điều chỉnh tham số nếu cần:
   - `Matcher`: chọn `BFMatcher` hoặc `FLANN`.
   - `Lowe Ratio`: lọc match tốt hơn khi giảm giá trị.
   - `RANSAC Threshold`: ngưỡng loại bỏ match sai.
   - `Blending`: chọn `Feather` hoặc `Simple`.
5. Bấm `Create Panorama` để tạo ảnh panorama.
6. Xem kết quả ở các tab:
   - `Input`: ảnh đầu vào.
   - `Keypoints`: điểm đặc trưng SIFT.
   - `Matching`: các cặp điểm khớp.
   - `RANSAC`: các match còn lại sau RANSAC.
   - `Homography`: ma trận biến đổi.
   - `Panorama`: ảnh panorama cuối cùng.
7. Bấm `Download Panorama` để tải ảnh kết quả hoặc `Download All Results` để tải toàn bộ kết quả dạng ZIP.


## Nơi Lưu Dữ Liệu

Khi chạy ứng dụng:

- Ảnh upload được lưu vào:

```text
data/uploads/
```

- Mỗi lần tạo panorama thành công, kết quả được lưu vào một thư mục riêng:

```text
data/results/<timestamp>/
```

Trong thư mục kết quả sẽ có:

```text
input/
processed_input/
keypoints/
matches/
warped/
blended/
panorama/
metadata.json
```

Ảnh panorama cuối cùng nằm tại:

```text
data/results/<timestamp>/panorama/panorama_result.jpg
```

## Gợi Ý Ảnh Đầu Vào

- Dùng 2-4 ảnh chụp liên tiếp từ trái sang phải.
- Giữ vùng chồng lấp giữa hai ảnh khoảng 35-50%.
- Ảnh nên có nhiều chi tiết như nhà, cây, biển báo, cạnh, họa tiết.
- Tránh ảnh quá mờ, quá tối, bầu trời trống hoặc tường trơn.
- Hạn chế vật thể chuyển động lớn giữa các ảnh.
- Giữ máy ảnh ổn định và hạn chế thay đổi góc nhìn quá mạnh.

## Chạy Kiểm Thử

Chạy toàn bộ test:

```bash
pytest -q
```

Nếu tất cả ổn, terminal sẽ hiển thị số lượng test đã pass.

## Cấu Trúc Dự Án

```text
.
|-- app.py
|-- pages/
|-- ui/
|-- core/
|-- models/
|-- services/
|-- utils/
|-- data/
|   |-- sample/
|   |-- uploads/
|   `-- results/
|-- scripts/
|-- tests/
|-- requirements.txt
`-- README.md
```

## Lỗi Thường Gặp

**Không bấm được Create Panorama**

cần upload ít nhất 2 ảnh và tối đa 4 ảnh.

**Unsupported File Format**

Chỉ dùng file JPG, JPEG hoặc PNG.

**Not Enough Visual Features**

Ảnh quá ít chi tiết. Hãy chọn ảnh sắc nét và có nhiều texture hơn.

**Not Enough Matching Features**

Hai ảnh không đủ vùng chồng lấp hoặc thứ tự ảnh chưa đúng.

**Homography Failed**

Thử tăng vùng chồng lấp, giảm thay đổi góc nhìn hoặc chỉnh lại `RANSAC Threshold`.
