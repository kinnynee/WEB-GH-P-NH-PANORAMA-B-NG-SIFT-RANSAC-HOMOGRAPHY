# Panorama Vision Studio

Ứng dụng web Streamlit tương tác để trực quan hóa quá trình ghép ảnh panorama với pipeline thật gồm SIFT, Feature Matching, Lowe Ratio Test, RANSAC, Homography, Warping và Blending.

## Mục Tiêu

Dự án này được xây dựng cho bài tập nhập môn xử lý ảnh số. Ứng dụng cho phép người dùng tải lên 2-4 ảnh có vùng chồng lấp, điều chỉnh các tham số quan trọng, chạy pipeline tạo panorama, xem các kết quả trung gian và tải về ảnh panorama cuối cùng hoặc gói ZIP chứa tất cả kết quả.

## Công Nghệ

- Python 3.11+
- Streamlit
- OpenCV
- NumPy
- Pillow
- Pytest

Dự án không dùng `cv2.Stitcher_create()` làm thuật toán chính. Mỗi bước cốt lõi đều được cài đặt rõ ràng.

## Kiến Trúc

```text
.
|-- app.py
|-- pages/
|   |-- home.py
|   |-- workspace.py
|   `-- algorithm.py
|-- ui/
|   |-- styles.py
|   |-- components.py
|   `-- navigation.py
|-- core/
|   |-- preprocessing.py
|   |-- features.py
|   |-- matching.py
|   |-- homography.py
|   |-- warping.py
|   |-- blending.py
|   `-- stitcher.py
|-- models/
|   `-- result_models.py
|-- services/
|   |-- processing_service.py
|   `-- export_service.py
|-- utils/
|   |-- image_utils.py
|   |-- validation.py
|   `-- visualization.py
|-- data/sample/
|-- scripts/
|   `-- generate_sample_images.py
|-- tests/
|-- requirements.txt
`-- README.md
```

## Pipeline Thuật Toán

1. Tải và kiểm tra tính hợp lệ của ảnh.
2. Thay đổi kích thước các ảnh quá lớn.
3. Chuyển ảnh RGB sang ảnh mức xám.
4. Phát hiện keypoint SIFT và descriptor 128 chiều.
5. Khớp descriptor bằng BFMatcher hoặc FLANN với KNN, `k=2`.
6. Áp dụng Lowe Ratio Test.
7. Ước lượng Homography bằng RANSAC.
8. Tính canvas chung từ các góc ảnh sau khi biến đổi.
9. Biến đổi phối cảnh ảnh bằng `cv2.warpPerspective`.
10. Trộn ảnh bằng Simple hoặc Feather blending.
11. Cắt bỏ các vùng viền đen không sử dụng.
12. Trả về panorama cuối cùng và các hình trực quan hóa trung gian.

Với 3-4 ảnh, ứng dụng ghép tuần tự từ trái sang phải:

```text
Ảnh 1 + Ảnh 2 -> Panorama Trung Gian
Panorama Trung Gian + Ảnh 3 -> Panorama Cập Nhật
Panorama Cập Nhật + Ảnh 4 -> Panorama Cuối Cùng
```

## Cài Đặt

```bash
pip install -r requirements.txt
```

## Chạy Ứng Dụng

```bash
streamlit run app.py
```

Sau đó mở URL Streamlit cục bộ được hiển thị trong terminal.

## Kiểm Thử

```bash
pytest -q
```

Bộ kiểm thử sử dụng các ảnh mẫu cục bộ có tính xác định và không cần truy cập internet.

## Dữ Liệu Mẫu

Tạo ảnh mẫu:

```bash
python scripts/generate_sample_images.py
```

Ứng dụng cũng có nút **Load Sample Images** trong trang Workspace. Các ảnh này là những vùng cắt tổng hợp có tính xác định, đủ nhiều texture cho SIFT, matching, Homography và kiểm thử đầu cuối.

## Hướng Dẫn Chụp Ảnh

- Chụp 2-4 ảnh từ trái sang phải.
- Giữ độ chồng lấp 35-50% giữa các ảnh liền kề.
- Ưu tiên cảnh có texture, cạnh, biển báo, tòa nhà, cây cối hoặc các chi tiết khác.
- Tránh bầu trời quá trống, tường trắng, nhòe chuyển động và các chủ thể chuyển động lớn.
- Xoay máy ảnh từ một vị trí ổn định để giảm thị sai.
- Giữ độ phơi sáng và tiêu cự tương tự giữa các ảnh.

## Tham Số Chính

- **Matcher:** `BFMatcher` hoặc `FLANN`
- **Lowe Ratio:** mặc định `0.75`
- **RANSAC Threshold:** mặc định `5.0 px`
- **Blending:** `Feather` hoặc `Simple`

Giá trị mặc định nội bộ:

- `max_image_size = 1600`
- `sift_nfeatures = 2000`
- `min_good_matches = 10`

## Xuất Kết Quả

Ứng dụng hỗ trợ:

- `panorama_result.jpg`
- `panorama_results.zip`

Cấu trúc ZIP:

```text
output/
|-- input/
|-- keypoints/
|-- matches/
|   |-- raw_matches/
|   `-- ransac_inliers/
|-- panorama/
|   |-- pair_XX_intermediate.png
|   `-- panorama_result.jpg
`-- metadata.json
```

`metadata.json` bao gồm cấu hình, số lượng ảnh, số lượng keypoint, số match thô/match tốt, số inlier, tỷ lệ inlier, thời gian xử lý, trạng thái và độ phân giải cuối cùng.

## Lỗi Thường Gặp

- **Not Enough Images:** tải lên ít nhất 2 ảnh.
- **Too Many Images:** chỉ sử dụng tối đa 4 ảnh.
- **Unsupported File Format:** sử dụng JPG, JPEG hoặc PNG.
- **Not Enough Visual Features:** sử dụng ảnh sắc nét hơn và có nhiều texture hơn.
- **Not Enough Matching Features:** tăng độ chồng lấp hoặc kiểm tra thứ tự ảnh.
- **Homography Failed:** giảm thị sai, dùng các khung hình liền kề hoặc điều chỉnh RANSAC threshold.
- **Canvas Calculation Failed:** kiểm tra thứ tự ảnh và tránh thay đổi phối cảnh quá mạnh.

## Giới Hạn Hiện Tại

- Hỗ trợ ghép tuần tự 2-4 ảnh, nhưng chất lượng tốt nhất khi các khung hình liền kề được chụp từ trái sang phải.
- Feather blending dựa trên khoảng cách và phù hợp cho bài tập môn học, không phải bộ trộn multi-band đầy đủ.
- Ứng dụng không bao gồm đăng nhập, lưu trữ cơ sở dữ liệu, công cụ quản trị, lưu trữ đám mây hay tính năng mạng xã hội.
- Kết quả phụ thuộc nhiều vào độ chồng lấp, texture, thị sai và độ nhất quán phơi sáng của ảnh.
