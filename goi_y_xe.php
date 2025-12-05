<?php
$df = array_map('str_getcsv', file('BMW sales data (2010-2024).csv'));
$headers = array_shift($df);
$data = [];

foreach ($df as $row) {
    $data[] = array_combine($headers, $row);
}

function label_encode($data, $column) {
    $values = array_unique(array_column($data, $column));
    $values = array_values($values); 
    $map = [];
    foreach ($values as $i => $v) $map[$v] = $i;
    foreach ($data as &$row) $row[$column] = $map[$row[$column]];
    return [$data, $map];
}
list($df_encoded, $fuel_map) = label_encode($data, "Fuel_Type");
list($df_encoded, $region_map) = label_encode($df_encoded, "Region");

$X = [];
foreach ($df_encoded as $row) {
    $X[] = [
        floatval($row["Price_USD"]),
        floatval($row["Fuel_Type"]),
        floatval($row["Engine_Size_L"]),
        floatval($row["Region"]),
    ];
}

function euclidean($a, $b) {
    $sum = 0;
    for ($i = 0; $i < count($a); $i++) $sum += pow($a[$i] - $b[$i], 2);
    return sqrt($sum);
}
?>

<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Gợi Ý Xe BMW</title>
<style>
body { font-family: Arial; padding: 20px; background:#f7f7f7; }

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

form { max-width: 500px; margin:auto; padding:20px; background:white; border-radius:12px; box-shadow:0 4px 16px rgba(0,0,0,0.1);}
input, select, button { width: 100%; padding: 10px; margin: 6px 0; border-radius: 6px; border:1px solid #ccc; }
button { background:#ff6600; color:white; font-weight:bold; cursor:pointer; }
button:hover { background:#cc5200; }

.car-card { display: flex; margin-bottom: 25px; border-radius:10px; padding:15px; background:white; box-shadow:0 4px 16px rgba(0,0,0,0.1);}
.car-card img { width: 250px; border-radius: 10px; }
.info { padding-left: 20px; }
.score { color: #007bff; font-size: 20px; font-weight: bold; }

h2 { text-align:center; color:#cc3300; margin-bottom:25px; }
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

<h2>GỢI Ý XE BMW</h2>

<form method="POST">
    <label>Ngân sách tối đa (USD):</label>
    <input type="number" name="budget" min="20000" max="300000" step="5000" required>

    <label>Loại nhiên liệu:</label>
    <select name="fuel">
        <?php foreach ($fuel_map as $k => $v) echo "<option>$k</option>"; ?>
    </select>

    <label>Dung tích động cơ (L):</label>
    <select name="engine_size">
        <option>Không biết / Không quan trọng</option>
        <?php
        $engine_sizes = array_unique(array_column($data, "Engine_Size_L"));
        sort($engine_sizes);
        foreach ($engine_sizes as $e) echo "<option>$e</option>";
        ?>
    </select>

    <label>Khu vực:</label>
    <select name="region">
        <?php foreach ($region_map as $k => $v) echo "<option>$k</option>"; ?>
    </select>

    <button type="submit">Gợi ý xe phù hợp</button>
</form>

<hr>

<?php
if ($_POST) {
    $budget = floatval($_POST["budget"]);
    $fuel_enc = $fuel_map[$_POST["fuel"]];
    $region_enc = $region_map[$_POST["region"]];
    $engine_size = ($_POST["engine_size"] === "Không biết / Không quan trọng") 
        ? array_sum(array_column($data, "Engine_Size_L")) / count($data)
        : floatval($_POST["engine_size"]);

    $user = [$budget, $fuel_enc, $engine_size, $region_enc];
    $distances = [];
    foreach ($X as $i => $row) $distances[$i] = euclidean($user, $row);

    asort($distances);
    $top5 = array_slice($distances, 0, 5, true);

    echo "<h2>Các mẫu xe phù hợp:</h2>";

    $max_dist = max($top5); if ($max_dist==0) $max_dist=1;

    foreach ($top5 as $idx => $dist) {
        $car = $data[$idx];
        $score = 100 * (1 - $dist / $max_dist); $score = max(0, min(100, $score));

        $model = strtolower(str_replace(" ", "", $car["Model"]));
        $color = strtolower(str_replace(" ", "", $car["Color"]));
        $candidates = [
            "image/{$model}_{$color}.jpg",
            "image/{$model}_{$color}.png",
            "image/{$model}.jpg",
            "image/{$model}.png",
        ];
        $img = "image/default_car.png";
        foreach ($candidates as $c) { if(file_exists($c)) { $img=$c; break; } }

        echo "<div class='car-card'>
                <div><img src='$img'></div>
                <div class='info'>
                    <h3>BMW {$car['Model']}</h3>
                    <p><b>Tỉ lệ đề xuất:</b> <span class='score'>".number_format($score,1)."%</span></p>
                    <p><b>Giá:</b> ".number_format($car['Price_USD'])." USD</p>
                    <p><b>Nhiên liệu:</b> {$car['Fuel_Type']}</p>
                    <p><b>Động cơ:</b> {$car['Engine_Size_L']}L</p>
                    <p><b>Thị trường:</b> {$car['Region']}</p>
                </div>
              </div>";
    }
}
?>
</body>
</html>
