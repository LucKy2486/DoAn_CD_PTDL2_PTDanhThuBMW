<?php
$df = array_map('str_getcsv', file('BMW sales data (2010-2024).csv'));
$headers = array_shift($df);
$data = [];
foreach ($df as $row) {
    $data[] = array_combine($headers, $row);
}

$region_map = [
    "Asia" => "Châu Á",
    "Europe" => "Châu Âu",
    "North America" => "Bắc Mỹ",
    "South America" => "Nam Mỹ",
    "Africa" => "Châu Phi",
    "Middle East" => "Trung Đông"
];
foreach ($data as &$row) {
    $row['Region_VI'] = $region_map[$row['Region']] ?? $row['Region'];
}

$models        = array_unique(array_column($data, "Model"));
$regions_raw   = array_unique(array_column($data, "Region"));
$colors        = array_unique(array_column($data, "Color"));
$fuels         = array_unique(array_column($data, "Fuel_Type"));
$transmissions = array_unique(array_column($data, "Transmission"));
$engines       = array_unique(array_column($data, "Engine_Size_L"));

sort($models);
sort($regions_raw);
sort($colors);
sort($fuels);
sort($transmissions);
sort($engines);

$regions = [];
foreach ($regions_raw as $r) $regions[] = $region_map[$r] ?? $r;

$region_reverse = array_flip($region_map);

$years = range(2025, 2035);

$predicted_price = null;
$vnd_price = null;
$img_show = "image/default_car.png";

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $input = [
        "Model" => $_POST["model"],
        "Year" => intval($_POST["year"]),
        "Region" => $region_reverse[$_POST["region"]] ?? $_POST["region"],
        "Color" => $_POST["color"],
        "Fuel_Type" => $_POST["fuel"],
        "Transmission" => $_POST["transmission"],
        "Engine_Size_L" => floatval($_POST["engine"]),
        "Mileage_KM" => 0,
        "Sales_Volume" => 0,
        "Sales_Classification" => "A",
        "Market_Trend" => 0.0
    ];

    $json_b64 = base64_encode(json_encode($input, JSON_UNESCAPED_UNICODE));
    $python = escapeshellarg("D:\\Anaconda\\python.exe");
    $script = escapeshellarg(__DIR__ . "\\python_code\\du_doan.py");
    $cmd = "$python $script " . escapeshellarg($json_b64);

    $predicted_price = shell_exec("$cmd 2>&1");

    if (is_numeric(trim($predicted_price))) {
        $vnd_price = floatval($predicted_price) * 24000;
    }

    function extract_series($model_name) {
        if (preg_match('/(\d+)/', $model_name, $m)) return $m[1];
        return "";
    }

    $model_clean = strtolower(str_replace(" ", "", $_POST["model"]));
    $color_clean = strtolower($_POST["color"]);
    $series = extract_series($_POST["model"]);

    $candidates = [];
    if (is_numeric($series)) {
        $candidates[] = "{$series}_series_{$color_clean}";
        $candidates[] = "{$series}series_{$color_clean}";
    }
    $candidates[] = "{$model_clean}_{$color_clean}";
    $candidates[] = $model_clean;

    foreach ($candidates as $name) {
        if (file_exists("image/$name.jpg")) { $img_show = "image/$name.jpg"; break; }
        if (file_exists("image/$name.png")) { $img_show = "image/$name.png"; break; }
    }
}
?>

<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Dự đoán giá xe BMW</title>
<style>
body {
    font-family: Arial;
    background: #f1f1f1;
    margin: 0;
    padding: 20px;
}

.navbar {
    width: 100%;
    background: linear-gradient(to right, #cc3300, #ff9900);
    padding: 14px 0;
}

.navbar ul {
    list-style: none;
    display: flex;
    justify-content: center;
    gap: 40px;
    margin: 0;
    padding: 0;
}

.navbar ul li a {
    font-family: Arial;
    font-weight: bold;
    font-size: 16px;
    color: white;
    text-decoration: none;
    transition: 0.25s;
}

.navbar ul li a:hover {
    color: #ffe6cc;
    border-bottom: 2px solid white;
    padding-bottom: 3px;
}

.container {
    display: flex;
    gap: 20px;
    margin-top: 20px;
}

.form-section,
.result-section {
    flex: 1;
    min-width: 350px;
}

.card {
    background: white;
    padding: 18px;
    border-radius: 12px;
    box-shadow: 0 4px 18px rgba(0, 0, 0, 0.1);
}

img {
    width: 100%;
    border-radius: 12px;
    margin-bottom: 12px;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.2);
}

select,
button {
    width: 100%;
    padding: 10px;
    margin: 6px 0;
    border-radius: 6px;
    border: 1px solid #ccc;
}

button {
    background: #ff6600;
    color: white;
    font-weight: bold;
    cursor: pointer;
}

button:hover {
    background: #cc5200;
}

.price {
    font-size: 26px;
    font-weight: bold;
    margin-top: 10px;
}
</style>
</head>
<body>


<div class="navbar">
    <ul>
        <li><a href="home.php">Trang chủ</a></li>
        <li><a href="du_doan_gia_xe.php">Dự Đoán Giá Xe</a></li>
        <li><a href="goi_y_xe.php">Gợi Ý Xe</a></li>
        <li><a href="phan_loai_xe.php">Phân Loại Xe</a></li>
        <li><a href="phan_khuc_xe.php">Phân Khúc Xe</a></li>
    </ul>
</div>

<h2 style="text-align:center;">Dự đoán giá xe BMW</h2>

<div class="container">
    <div class="form-section">
        <div class="card">
            <form method="post">
                <label>Model:</label>
                <select name="model"><?php foreach($models as $m) echo "<option>$m</option>"; ?></select>

                <label>Thị trường:</label>
                <select name="region"><?php foreach($regions as $r) echo "<option>$r</option>"; ?></select>

                <label>Màu xe:</label>
                <select name="color"><?php foreach($colors as $c) echo "<option>$c</option>"; ?></select>

                <label>Nhiên liệu:</label>
                <select name="fuel"><?php foreach($fuels as $f) echo "<option>$f</option>"; ?></select>

                <label>Hộp số:</label>
                <select name="transmission"><?php foreach($transmissions as $t) echo "<option>$t</option>"; ?></select>

                <label>Động cơ (L):</label>
                <select name="engine"><?php foreach($engines as $e) echo "<option>$e</option>"; ?></select>

                <label>Năm dự đoán:</label>
                <select name="year"><?php foreach($years as $y) echo "<option>$y</option>"; ?></select>

                <button type="submit">Dự đoán</button>
            </form>
        </div>
    </div>

    <?php if ($predicted_price !== null): ?>
    <div class="result-section">
        <div class="card">
            <img src="<?= $img_show ?>">

            <div style="font-size:17px; line-height:1.6;">
                <b>Tên xe:</b> <?= htmlspecialchars($_POST["model"]) ?><br>
                <b>Năm dự đoán:</b> <?= htmlspecialchars($_POST["year"]) ?><br><br>
                <b>Thông số:</b><br>
                • <b>Thị trường:</b> <?= htmlspecialchars($_POST["region"]) ?><br>
                • <b>Màu xe:</b> <?= htmlspecialchars($_POST["color"]) ?><br>
                • <b>Nhiên liệu:</b> <?= htmlspecialchars($_POST["fuel"]) ?><br>
                • <b>Hộp số:</b> <?= htmlspecialchars($_POST["transmission"]) ?><br>
                • <b>Động cơ:</b> <?= htmlspecialchars($_POST["engine"]) ?> L<br>
            </div>

            <hr>

            <?php if (is_numeric(trim($predicted_price))): ?>
                <div class="price"><?= number_format($predicted_price,0) ?> USD</div>
                <div class="price" style="color:#d9534f;"><?= number_format($vnd_price,0,',','.') ?> VND</div>
            <?php else: ?>
                <div style="color:red; font-weight:bold;">
                    Lỗi Python:<br>
                    <pre><?= htmlspecialchars($predicted_price) ?></pre>
                </div>
            <?php endif; ?>
        </div>
    </div>
    <?php endif; ?>
</div>

</body>
</html>
