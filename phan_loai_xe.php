<?php
$df = array_map('str_getcsv', file('BMW sales data (2010-2024).csv'));
$headers = array_shift($df);
$data = [];
foreach ($df as $row) $data[] = array_combine($headers, $row);

$region_map = [
    "Asia"=>"Châu Á","Europe"=>"Châu Âu","North America"=>"Bắc Mỹ",
    "South America"=>"Nam Mỹ","Africa"=>"Châu Phi","Middle East"=>"Trung Đông"
];
foreach($data as &$row) $row['Region_VI']=$region_map[$row['Region']]??$row['Region'];

$fuel_map=[]; $region_map_enc=[]; $fuel_idx=0; $region_idx=0;
foreach($data as &$row){
    if(!isset($fuel_map[$row['Fuel_Type']])) $fuel_map[$row['Fuel_Type']]=$fuel_idx++;
    if(!isset($region_map_enc[$row['Region']])) $region_map_enc[$row['Region']]=$region_idx++;
    $row['Fuel_enc']=$fuel_map[$row['Fuel_Type']];
    $row['Region_enc']=$region_map_enc[$row['Region']];
}

$features=[];
foreach($data as $row) $features[]= [
    floatval($row['Price_USD']), 
    floatval($row['Engine_Size_L']), 
    intval($row['Fuel_enc']), 
    intval($row['Region_enc'])
];

$k = $_POST['k'] ?? 3; 
$k = intval($k); 
if($k < 2) $k = 2;
if($k > 6) $k = 6;

function kmeans($X,$k,$max_iter=100){
    $n = count($X); $dim = count($X[0]);
    $centroids = [];
    for($i=0;$i<$k;$i++) $centroids[$i]=$X[rand(0,$n-1)];
    $labels=array_fill(0,$n,0);
    for($iter=0;$iter<$max_iter;$iter++){
        foreach($X as $i=>$x){
            $min_d=PHP_INT_MAX;$idx=0;
            foreach($centroids as $c=>$cent){
                $d=0; for($j=0;$j<$dim;$j++) $d+=pow($x[$j]-$cent[$j],2);
                if($d<$min_d){$min_d=$d;$idx=$c;}
            }
            $labels[$i]=$idx;
        }
        $centroids_new=array_fill(0,$k,array_fill(0,$dim,0));
        $counts=array_fill(0,$k,0);
        foreach($X as $i=>$x){ $c=$labels[$i]; for($j=0;$j<$dim;$j++) $centroids_new[$c][$j]+=$x[$j]; $counts[$c]++; }
        for($c=0;$c<$k;$c++){ if($counts[$c]==0) continue; for($j=0;$j<$dim;$j++) $centroids_new[$c][$j]/=$counts[$c]; }
        $centroids=$centroids_new;
    }
    return $labels;
}

$labels = kmeans($features,$k);
for($i=0;$i<count($data);$i++) $data[$i]['Cluster'] = $labels[$i];

$cluster_desc = array_fill(0,$k,null);
for($c=0;$c<$k;$c++){
    $sub = array_filter($data,function($r) use($c){return $r['Cluster']==$c;});
    $prices = array_column($sub,'Price_USD');
    $engines = array_column($sub,'Engine_Size_L');
    $fuels = array_column($sub,'Fuel_enc');
    $regions = array_column($sub,'Region_enc');
    $fuel_mode = array_search(max(array_count_values($fuels)),array_count_values($fuels));
    $region_mode = array_search(max(array_count_values($regions)),array_count_values($regions));
    $fuel_name = array_search($fuel_mode,$fuel_map);
    $region_name = array_search($region_mode,$region_map_enc);
    $cluster_desc[$c]=[
        'price_min'=>min($prices),
        'price_max'=>max($prices),
        'engine_min'=>min($engines),
        'engine_max'=>max($engines),
        'fuel'=>$fuel_name,
        'region'=>$region_name,
        'samples'=>array_slice($sub,0,10)
    ];
}
?>

<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Phân loại xe BMW</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
body {
    font-family: Arial;
    background: #f1f1f1;
    margin: 0;
    padding: 20px;
    font-size: 16px;
    line-height: 1.5;
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
    color: white;
    text-decoration: none;
    font-weight: bold;
    font-size: 16px;
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
    flex-wrap: wrap;
}

.card {
    background: white;
    padding: 18px;
    border-radius: 12px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.1);
}

table {
    border-collapse: collapse;
    width: 100%;
    font-size: 14px;
    line-height: 1.4;
}

table, th, td {
    border: 1px solid #ccc;
    padding: 6px;
    text-align: center;
}

select,
button {
    width: 100%;
    padding: 10px;
    margin: 6px 0;
    border-radius: 6px;
    border: 1px solid #ccc;
    font-size: 14px;
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

canvas#scatterChart{
    width:100% !important;
    max-width:800px;
    height:400px !important;
    margin:auto;
    display:block;
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

<h2 style="text-align:center;margin-top:20px;">Phân Loại Xe BMW</h2>

<div class="card" style="max-width:400px;margin:auto;">
<form method="post">
<label>Số lượng cụm (K): <span id="kVal"><?= $k ?></span></label>
<input type="range" min="2" max="6" name="k" value="<?= $k ?>" id="kSlider" oninput="kVal.innerText=this.value">
<button type="submit">Phân loại</button>
</form>
</div>

<div class="container">
<div class="card" style="flex:1;">
<h3>Biểu đồ scatter (Giữa Engine và Price)</h3>
<div class="chart-container" style="width:100%; max-width:900px; overflow-y:auto;">
    <canvas id="scatterChart"></canvas>
</div>

<script>
const totalPoints = <?= count($data) ?>;
const baseHeight = 400; 
const extraPerPoint = 4; 
const canvasHeight = Math.max(baseHeight, totalPoints * extraPerPoint);

const canvas = document.getElementById('scatterChart');
canvas.height = canvasHeight;

const ctx = canvas.getContext('2d');
const colors = ['red','blue','green','orange','purple','cyan'];
const datasets = [];

<?php
for($i = 0; $i < $k; $i++){
    echo "datasets.push({label:'Nhóm $i',data:[";
    foreach($data as $r) if($r['Cluster']==$i) echo "{x:".$r['Engine_Size_L'].",y:".$r['Price_USD']."},";
    echo "],backgroundColor:colors[$i],pointRadius:4});";
}
?>

new Chart(ctx, {
    type: 'scatter',
    data: { datasets: datasets },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { position:'bottom', labels: { font: { size: 13 } } },
            tooltip: {
                bodyFont: { size: 12 },
                titleFont: { size: 12 },
                callbacks: {
                    label: function(context){
                        return `Engine: ${context.parsed.x} L, Price: ${context.parsed.y} USD`;
                    }
                }
            }
        },
        scales: {
            x: { title: { display: true, text:'Engine (L)', font: { size: 14 } }, ticks: { font: { size: 12 } } },
            y: { title: { display: true, text:'Price USD', font: { size: 14 } }, ticks: { font: { size: 12 } } }
        }
    }
});
</script>

<?php
for($c=0;$c<$k;$c++){
    $desc=$cluster_desc[$c];
    echo "<div style='background:#e6f0ff;padding:10px;border-radius:6px;margin-bottom:10px;line-height:1.4;'>";
    echo "<b>Nhóm $c</b><br>";
    echo "Tầm giá: ".number_format($desc['price_min'])." – ".number_format($desc['price_max'])." USD<br>";
    echo "Động cơ: ".$desc['engine_min']." – ".$desc['engine_max']." L<br>";
    echo "Nhiên liệu phổ biến: ".$desc['fuel']."<br>";
    echo "Thị trường chính: ".$desc['region']."<br>";
    echo "</div>";

    echo "<b>Một số mẫu xe tiêu biểu</b>";
    echo "<table><tr><th>Model</th><th>Year</th><th>Price USD</th><th>Engine L</th></tr>";
    foreach($desc['samples'] as $s){
        echo "<tr><td>{$s['Model']}</td><td>{$s['Year']}</td><td>".number_format($s['Price_USD'])."</td><td>{$s['Engine_Size_L']}</td></tr>";
    }
    echo "</table><br>";
}
?>
</div>
</div>
</body>
</html>
