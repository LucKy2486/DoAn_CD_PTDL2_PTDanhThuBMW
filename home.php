<?php
$usd_to_vnd = 24000;

$df = array_map('str_getcsv', file('BMW sales data (2010-2024).csv'));
$headers = array_shift($df);
$data = [];
foreach ($df as $row) {
    $data[] = array_combine($headers, $row);
}

//Region Việt Hóa
$region_map = [
    "Asia" => "Châu Á",
    "Europe" => "Châu Âu",
    "North America" => "Bắc Mỹ",
    "South America" => "Nam Mỹ",
    "Africa" => "Châu Phi",
    "Middle East" => "Trung Đông"
];
foreach ($data as &$row) $row['Region_VI'] = $region_map[$row['Region']] ?? $row['Region'];

function categorize_brand($model) {
    $m = strtolower(trim($model));
    if (str_starts_with($m, "m")) return "BMW M";
    if (str_starts_with($m, "i")) return "BMW i";
    return "BMW";
}

function extract_series($model) {
    $m = strtolower(trim($model));
    if (str_starts_with($m, "i") || str_starts_with($m, "m")) return strtoupper(substr($m,1));
    if (str_contains($m, "series")) return trim(explode("series", $m)[0]);
    if (in_array($m[0], ["x","z"])) return strtoupper($m[0]);
    if (preg_match('/\d+/', $m, $matches)) return $matches[0];
    return "";
}

foreach ($data as &$row) {
    $row['Brand_Type'] = categorize_brand($row['Model']);
    $row['Series'] = extract_series($row['Model']);
}

$regions = array_unique(array_column($data,'Region_VI'));
$years = array_unique(array_column($data,'Year'));
sort($years);

$selected_region = $_POST['region'] ?? "Châu Á";
$selected_year   = $_POST['year'] ?? 2016;
$selected_brand  = $_POST['brand'] ?? "BMW";
$selected_series = $_POST['series'] ?? "3";

?>

<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>BMW Home</title>
<link rel="stylesheet" href="css/style.css">
<style>
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

.filter-wrapper {
    text-align: center;
    margin: 35px 0 40px 0;
    font-family: Arial, sans-serif;
}

select {
    padding: 10px 14px;
    font-size: 16px;
    margin: 0 6px;
    border: 1px solid #ccc;
    border-radius: 4px;
}

.brand-tabs {
    display: inline-flex;
    border: 1px solid #dcdcdc;
    border-radius: 4px;
    overflow: hidden;
    margin-top: 25px;
}

.brand-tab {
    padding: 14px 35px;
    font-size: 20px;
    font-weight: 600;
    cursor: pointer;
    background: #fff;
    border-right: 1px solid #dcdcdc;
    transition: 0.2s ease;
    user-select: none;
}

.brand-tab:last-child {
    border-right: none;
}

.brand-tab:hover {
    background: #f2f2f2;
}

.brand-tab.active {
    background: #000;
    color: #fff;
}

.series-list {
    display: flex;
    justify-content: center;
    gap: 45px;
    margin-top: 30px;
}

.series-item {
    font-size: 26px;
    cursor: pointer;
    padding-bottom: 6px;
    transition: 0.2s;
    color: #444;
}

.series-item:hover {
    color: #000;
}

.series-item.active {
    font-weight: bold;
    border-bottom: 2px solid #000;
    color: #000;
}

.series-hidden {
    display: none;
}

.car-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 40px;
    padding: 20px 40px;
    max-width: 1500px;
    margin: auto;
}

.car-item {
    width: 100%;
    max-width: 330px;
    font-family: Arial;
    text-align: left;
    transition: 0.3s;
}

.car-img {
    width: 100%;
    height: 210px;
    object-fit: cover;
    border-radius: 10px;
}

.car-item h3 {
    font-size: 22px;
    font-weight: bold;
    margin-top: 10px;
}

.car-item p {
    font-size: 15px;
    margin: 3px 0;
}

.price {
    margin-top: 10px;
    font-weight: bold;
}

.car-link {
    text-decoration: none;
    color: black;
}

.car-link:hover .car-item {
    transform: translateY(-6px);
    transition: 0.3s;
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

<div class="filter-wrapper">
    <form id="frm" method="post">
        <select name="region" onchange="this.form.submit()">
            <?php foreach($regions as $r): ?>
                <option value="<?= $r ?>" <?= $r==$selected_region?"selected":"" ?>><?= $r ?></option>
            <?php endforeach; ?>
        </select>
        <select name="year" onchange="this.form.submit()">
            <?php foreach($years as $y): ?>
                <option value="<?= $y ?>" <?= $y==$selected_year?"selected":"" ?>><?= $y ?></option>
            <?php endforeach; ?>
        </select>
        <input type="hidden" name="brand" id="brand" value="<?= $selected_brand ?>">
        <input type="hidden" name="series" id="series" value="<?= $selected_series ?>">
    </form>

    <div class="brand-tabs">
        <div class="brand-tab <?= $selected_brand=='BMW'?'active':'' ?>" onclick="selectBrand('BMW')">BMW</div>
        <div class="brand-tab <?= $selected_brand=='BMW M'?'active':'' ?>" onclick="selectBrand('BMW M')">BMW M</div>
        <div class="brand-tab <?= $selected_brand=='BMW i'?'active':'' ?>" onclick="selectBrand('BMW i')">BMW i</div>
    </div>

    <div class="series-list <?= $selected_brand!='BMW'?'series-hidden':'' ?>">
        <?php foreach(["3","4","5","7","X","Z"] as $s): ?>
            <div class="series-item <?= $selected_series==$s?'active':'' ?>" onclick="selectSeries('<?= $s ?>')"><?= $s ?></div>
        <?php endforeach; ?>
    </div>
</div>

<script>
function selectBrand(b){ document.getElementById("brand").value=b; if(b!="BMW")document.getElementById("series").value=""; document.getElementById("frm").submit();}
function selectSeries(s){ document.getElementById("series").value=s; document.getElementById("frm").submit();}
</script>

<div class="car-grid">
<?php
$filtered = array_filter($data, function($row)
    use ($selected_region,$selected_year,$selected_brand,$selected_series)
{
    if ($row['Region_VI'] != $selected_region) return false;
    if ($row['Year'] != $selected_year) return false;
    if ($row['Brand_Type'] != $selected_brand) return false;
    if ($selected_brand == "BMW" && $row['Series'] != $selected_series) return false;
    return true;
});

foreach ($filtered as $row):
    $model = strtolower(str_replace(" ", "", $row['Model']));
    $color = strtolower(trim($row["Color"]));
    $series = extract_series($row["Model"]);

    $candidates = [];
    if (is_numeric($series)) {
        $candidates[] = "{$series}_series_{$color}";
        $candidates[] = "{$series}series_{$color}";
    }
    if (str_starts_with($model,"x") || str_starts_with($model,"i") || str_starts_with($model,"m")) {
        $candidates[] = "{$model}_{$color}";
    }
    $candidates[] = "{$model}_{$color}";
    $candidates[] = $model;

    $img_path = "image/default_car.png";
    foreach($candidates as $name){
        if(file_exists("image/$name.jpg")){ $img_path="image/$name.jpg"; break; }
        if(file_exists("image/$name.png")){ $img_path="image/$name.png"; break; }
    }
?>
    <a href="chi_tiet_xe.php?model=<?= urlencode($row['Model']) ?>&year=<?= $row['Year'] ?>&color=<?= urlencode($row['Color']) ?>&region=<?= urlencode($row['Region_VI']) ?>" class="car-link">
        <div class="car-item">
            <img src="<?= $img_path ?>" class="car-img">
            <h3>BMW <?= htmlspecialchars($row['Model']) ?></h3>
            <p>Màu: <?= htmlspecialchars($row['Color']) ?></p>
            <p>Nhiên liệu: <?= htmlspecialchars($row['Fuel_Type']) ?></p>
            <p class="price">Giá từ <?= number_format($row['Price_USD']*$usd_to_vnd, 0, ',', '.') ?> VNĐ</p>
        </div>
    </a>
<?php endforeach; ?>
</div>

</body>
</html>
