<?php
$raw = file('BMW sales data (2010-2024).csv');

$df = array_map(fn($x)=>str_getcsv($x, ','), $raw);

$headers = array_shift($df);
$data = [];

foreach ($df as $row){
    if(count($row) == count($headers)){
        $data[] = array_combine($headers, $row);
    }
}

foreach($data as &$row){
    $row['Price_USD']      = floatval($row['Price_USD']);
    $row['Engine_Size_L']  = floatval($row['Engine_Size_L']);
    $row['Year']           = intval($row['Year']);
}
unset($row);

$cat_cols = ["Fuel_Type","Region","Transmission","Model"];
$encoders = [];

foreach($cat_cols as $col){
    $values = array_unique(array_column($data, $col));
    $map = array_flip($values);
    $encoders[$col] = $map;

    foreach($data as &$row){
        $row[$col."_enc"] = $map[$row[$col]] ?? 0;
    }
    unset($row);
}

function kmeans_price($X, $k=3, $max_iter=100){
    $n = count($X);

    $centroids = [];
    for ($i=0; $i<$k; $i++){
        $centroids[] = $X[rand(0, $n-1)];
    }

    $labels = array_fill(0, $n, 0);

    for ($iter=0; $iter<$max_iter; $iter++){
        foreach($X as $i=>$x){
            $best = 0;
            $min_d = PHP_INT_MAX;
            foreach($centroids as $c=>$cent){
                $d = pow($x - $cent, 2);
                if($d < $min_d){
                    $min_d = $d;
                    $best = $c;
                }
            }
            $labels[$i] = $best;
        }

        $new = array_fill(0, $k, 0);
        $cnt = array_fill(0, $k, 0);
        foreach($X as $i=>$x){
            $c = $labels[$i];
            $new[$c] += $x;
            $cnt[$c]++;
        }
        for($c=0;$c<$k;$c++){
            if($cnt[$c] > 0) $new[$c] /= $cnt[$c];
        }
        $centroids = $new;
    }
    return $labels;
}

$labels = kmeans_price(array_column($data,'Price_USD'), 3);

$group_avg = [];

for($i=0; $i<3; $i++){
    $indexes = array_filter(array_keys($labels), fn($k)=>$labels[$k]==$i);
    $avg = 0;
    if(count($indexes)>0){
        $avg = array_sum(array_map(fn($x)=>$data[$x]['Price_USD'], $indexes)) / count($indexes);
    }
    $group_avg[$i] = $avg;
}

asort($group_avg);

$names = ["Rẻ", "Trung cấp", "Cao cấp"];
$map_name = [];

$i=0;
foreach($group_avg as $k=>$v){
    $map_name[$k] = $names[$i++];
}

foreach($data as $i=>$row){
    $data[$i]["Segment"] = $map_name[$labels[$i]];
}

$pred_segment = "";

if(isset($_POST["predict"])){
    $engine = floatval($_POST["Engine_Size_L"]);
    $year   = intval($_POST["Year"]);
    $fuel   = $_POST["Fuel_Type"];
    $region = $_POST["Region"];
    $trans  = $_POST["Transmission"];
    $model  = $_POST["Model"];

    $fuel_enc   = $encoders["Fuel_Type"][$fuel] ?? 0;
    $region_enc = $encoders["Region"][$region] ?? 0;
    $trans_enc  = $encoders["Transmission"][$trans] ?? 0;
    $model_enc  = $encoders["Model"][$model] ?? 0;

    $best = "";
    $min_d = PHP_INT_MAX;

    foreach($data as $row){
        $d = pow($engine - $row["Engine_Size_L"],2)
           + pow($year - $row["Year"],2)
           + pow($fuel_enc - $row["Fuel_Type_enc"],2)
           + pow($region_enc - $row["Region_enc"],2)
           + pow($trans_enc - $row["Transmission_enc"],2)
           + pow($model_enc - $row["Model_enc"],2);

        if($d < $min_d){
            $best = $row["Segment"];
            $min_d = $d;
        }
    }
    $pred_segment = $best;
}

$features = ["Engine_Size_L", "Year", "Model_enc", "Region_enc", "Fuel_Type_enc", "Transmission_enc"];
$importance = [];

foreach($features as $f){
    $vals = array_column($data, $f);
    $importance[$f] = (max($vals) - min($vals));
}

$sum_imp = array_sum($importance);
foreach($importance as $k=>$v){
    $importance[$k] = $v / $sum_imp;
}

$imp_labels = ["Engine Size", "Year", "Model", "Region", "Fuel Type", "Transmission"];
$imp_values = array_values($importance);
?>

<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Phân khúc xe BMW</title>

<style>
body{
    font-family: Arial;
    background:#fafafa;
    margin:0;
    padding:0;
}
.container{
    max-width:1200px;
    margin:auto;
    padding:30px;
}
.card{
    background:white;
    padding:25px;
    border-radius:14px;
    margin-bottom:35px;
    box-shadow:0 3px 15px rgba(0,0,0,0.08);
}
input[type=range]{
    width:100%;
    height:6px;
    border-radius:5px;
    background:#eee;
}
select{
    width:100%;
    padding:12px;
    background:#f2f3f5;
    border-radius:8px;
}
button{
    background:#ff4b4b;
    padding:12px 25px;
    border:none;
    color:white;
    border-radius:8px;
}

.navbar{width:100%;background:linear-gradient(to right,#cc3300,#ff9900);padding:14px 0;}
.navbar ul{list-style:none;display:flex;justify-content:center;gap:40px;margin:0;padding:0;}
.navbar ul li a{color:white;text-decoration:none;font-weight:bold;font-size:16px;transition:0.25s;}
.navbar ul li a:hover{color:#ffe6cc;border-bottom:2px solid white;padding-bottom:3px;}
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

<div class="container">

<h1 style="text-align:center; margin-bottom:30px;">PHÂN KHÚC XE BMW</h1>

<div class="card">
    <h2>Độ quan trọng của các yếu tố khi phân khúc xe</h2>
    <canvas id="importanceChart"></canvas>
</div>

<div class="card">
    <h2>Dự đoán phân khúc cho 1 chiếc xe</h2>

    <form method="POST">

        <div class="label">Động cơ (L)</div>
        <input type="range" name="Engine_Size_L" min="1" max="6" step="0.1" value="2">
        <div><b id="engine_display">2.0</b></div>

        <div class="label">Năm</div>
        <input type="range" name="Year" min="2010" max="2024" value="2020">
        <div><b id="year_display">2020</b></div>

        <div class="label">Nhiên liệu</div>
        <select name="Fuel_Type">
            <?php foreach(array_keys($encoders["Fuel_Type"]) as $v) echo "<option>$v</option>"; ?>
        </select>

        <div class="label">Thị trường</div>
        <select name="Region">
            <?php foreach(array_keys($encoders["Region"]) as $v) echo "<option>$v</option>"; ?>
        </select>

        <div class="label">Hộp số</div>
        <select name="Transmission">
            <?php foreach(array_keys($encoders["Transmission"]) as $v) echo "<option>$v</option>"; ?>
        </select>

        <div class="label">Model</div>
        <select name="Model">
            <?php foreach(array_keys($encoders["Model"]) as $v) echo "<option>$v</option>"; ?>
        </select>

        <button type="submit" name="predict">Dự đoán</button>
    </form>

    <?php if($pred_segment!=""): ?>
        <p style="font-size:22px; font-weight:bold; margin-top:20px;">
            Phân khúc dự đoán: <?=$pred_segment?>
        </p>
    <?php endif; ?>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>

document.querySelector("input[name='Engine_Size_L']").oninput = function(){
    document.getElementById("engine_display").innerText = this.value;
};
document.querySelector("input[name='Year']").oninput = function(){
    document.getElementById("year_display").innerText = this.value;
};

new Chart(document.getElementById('segmentChart'), {
    type: 'bar',
    data: {
        labels: ["Rẻ","Trung cấp","Cao cấp"],
        datasets: [{
            label:"Số lượng",
            data:[
                <?=count(array_filter($data, fn($r)=>$r['Segment']=="Rẻ"))?>,
                <?=count(array_filter($data, fn($r)=>$r['Segment']=="Trung cấp"))?>,
                <?=count(array_filter($data, fn($r)=>$r['Segment']=="Cao cấp"))?>
            ],
            backgroundColor:["#FF6384","#FFCE56","#36A2EB"]
        }]
    },
    options:{plugins:{legend:{display:false}}, responsive:true}
});

new Chart(document.getElementById('importanceChart'), {
    type: 'bar',
    data: {
        labels: <?=json_encode($imp_labels)?>,
        datasets: [{
            label: "Importance",
            data: <?=json_encode($imp_values)?>,
            backgroundColor:"#2E86DE"
        }]
    },
    options:{
        indexAxis:'y',
        responsive:true,
        plugins:{legend:{display:false}}
    }
});
</script>

</div>
</body>
</html>
