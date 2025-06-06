<?php
/* ---------- เชื่อมต่อฐานข้อมูลผ่านไฟล์ config ---------- */
$pdo = require __DIR__ . '/../../config/config.php';

/* ---------- รับพารามิเตอร์จาก URL ---------- */
$sort       = $_GET['sort']   ?? 'name';
$filterType = $_GET['filter'] ?? '';
$search     = $_GET['search'] ?? '';

/* ---------- ฟิลด์ที่อนุญาตให้เรียงได้ ---------- */
$validSorts = [
    'name'         => 'Hero_Name',
    'first_class'  => 'First_Class',
    'second_class' => 'Second_Class',
];
$sortField  = $validSorts[$sort] ?? 'Hero_Name';

/* ---------- Query ดึงฮีโร่ ตามเงื่อนไข filter / search / sort ---------- */
$sql    = "SELECT * FROM heroes WHERE 1=1";
$params = [];
if ($filterType !== '') {
    $sql             .= " AND (First_Class = :type OR Second_Class = :type)";
    $params[':type'] = $filterType;
}
if ($search !== '') {
    $sql               .= " AND Hero_Name LIKE :search";
    $params[':search'] = "%$search%";
}
$sql .= " ORDER BY $sortField ASC";

$stmt   = $pdo->prepare($sql);
$stmt->execute($params);
$heroes = $stmt->fetchAll(PDO::FETCH_ASSOC);

/* ---------- Query ดึงคลาสทั้งหมด ไม่ซ้ำ + เรียงลำดับ ---------- */
// ดึงข้อมูล First_Class และ Second_Class แล้วรวมเป็นรายการเดียว
$rawHeroClasses = $pdo
    ->query("
        SELECT First_Class FROM heroes
        UNION ALL
        SELECT Second_Class FROM heroes
    ")
    ->fetchAll(PDO::FETCH_COLUMN);

// ปรับรูปแบบตัวพิมพ์ให้อยู่ในรูปแบบเดียว (ขึ้นต้นด้วยตัวใหญ่)
$normalizedHeroClasses = array_filter(array_map(function ($class) {
    $class = trim($class);
    return $class === '' ? null : ucfirst(strtolower($class));
}, $rawHeroClasses));


// กรองค่าซ้ำ แล้วเรียงตามตัวอักษร
$heroClasses = array_unique($normalizedHeroClasses);
sort($heroClasses);

/* ---------- Query ดึงเลนทั้งหมด ไม่ซ้ำ + เรียงลำดับ ---------- */
$lanes = $pdo
    ->query("
        SELECT DISTINCT lane
        FROM (
            SELECT First_Lane  AS lane FROM heroes
             UNION
            SELECT Second_Lane AS lane FROM heroes
        ) AS tmp
        WHERE lane IS NOT NULL AND lane <> ''
        ORDER BY lane
    ")
    ->fetchAll(PDO::FETCH_COLUMN);

/* ---------- กรองเลนซ้ำ + เรียงอีกครั้ง ---------- */
$lanes = array_unique($lanes);
sort($lanes);

/* ---------- PHP Slugify function (similar to Python's) ---------- */
function slugify_php($itemName) {
    // For common cases, direct replacement. Add 'u' modifier for UTF-8.
    $name = preg_replace("/[ '’]/u", "_", $itemName);    // Space & apostrophes
    $name = preg_replace("/[^A-Za-z0-9_]/u", "", $name);  // Keep only A-Z, a-z, 0-9, _
    return $name;
}

/* ---------- Fetch all item data from DB and map to image files ---------- */
$stmtItems = $pdo->query("SELECT ItemID, ItemName FROM items"); // Assuming ItemType might be useful later
$allItemsFromDB = $stmtItems->fetchAll(PDO::FETCH_ASSOC);

$baseItemImagePath = 'src/assets/images/item/'; // Relative to web root

$categorizedItems = ['all' => [], 'farm' => [], 'support' => []];
$itemMapById = []; // For easy lookup by ID if needed later

// Scan all image files once to build a map of slugified_filename => path
$rawImageFilesMap = [];
$itemImageDirectory = __DIR__ . '/src/assets/images/item/';
if (is_dir($itemImageDirectory)) {
    $it = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($itemImageDirectory));
    foreach ($it as $file) {
        if (!$file->isDir()) {
            $ext = strtolower(pathinfo($file->getFilename(), PATHINFO_EXTENSION));
            if (in_array($ext, ['jpg', 'jpeg', 'png', 'webp'])) {
                $relativePath = str_replace(__DIR__ . '/', '', str_replace('\\', '/', $file->getPathname()));
                // Use the filename (without extension) as the key, assuming it's already slugified
                $slugifiedFilename = pathinfo($file->getFilename(), PATHINFO_FILENAME);
                $rawImageFilesMap[$slugifiedFilename] = $relativePath;
            }
        }
    }
}

foreach ($allItemsFromDB as $dbItem) {
    $slugifiedDbItemName = slugify_php($dbItem['ItemName']);
    // Try to find image path using slugified name from DB against slugified filenames from filesystem
    $imagePath = $rawImageFilesMap[$slugifiedDbItemName] ?? null;

    if ($imagePath) {
        $itemData = [
            'id' => $dbItem['ItemID'],
            'name' => $dbItem['ItemName'],
            'path' => $imagePath
        ];
        $categorizedItems['all'][] = $itemData;
        $itemMapById[$dbItem['ItemID']] = $itemData;

        if (str_starts_with($imagePath, $baseItemImagePath . 'farm-item/')) {
            $categorizedItems['farm'][] = $itemData;
        } elseif (str_starts_with($imagePath, $baseItemImagePath . 'support-item/')) {
            $categorizedItems['support'][] = $itemData;
        }
    }
}

?>
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Recommender System</title>
    <link rel="stylesheet" href="src/styles/base/style.css">
</head>

<body>
    <div class="Input-Container">
        <div class="Hero-Header">
            <p>-- Hero --</p>
        </div>

        <!-- Filter by Class (dynamic จาก Database, ไม่มีค่าซ้ำ) -->
        <div class="Filter-Container">
            <h1>Select Filter</h1>
            <div class="Filter-Button">
                <?php foreach ($heroClasses as $class): ?>
                    <button
                        value="<?= htmlspecialchars($class) ?>"
                        onclick="filterByClass('<?= htmlspecialchars($class, ENT_QUOTES) ?>')">
                        <?= htmlspecialchars($class) ?>
                    </button>
                <?php endforeach; ?>
            </div>
        </div>

        <!-- Hero Dropdown -->
        <div class="Hero-Container">
            <h1>Select Hero</h1>
            <div class="Hero-Dropdown">
                <div class="Hero-Dropdown-Toggle" onclick="toggleDropdown()">
                    <span id="selected-text">Select</span>
                    <span class="icon" id="hero-dropdown-icon">▾</span>
                </div>
                <div id="Hero-Dropdown-Menu" class="hidden">
                    <input type="text" id="hero-search-box" placeholder="Select" oninput="HerofilterOption()">
                    <?php foreach ($heroes as $hero): ?>
                        <?php
                        $name       = $hero['Hero_Name'];
                        $folder     = 'src/assets/images/heroes/';
                        $serverPath = __DIR__ . "/src/assets/images/heroes/{$name}.";
                        $img        = 'src/assets/images/placeholder.jpg';
                        foreach (['jpg', 'jpeg', 'png', 'webp'] as $e) {
                            if (file_exists("{$serverPath}{$e}")) {
                                $img = "{$folder}{$name}.{$e}";
                                break;
                            }
                        }
                        ?>
                        <div class="Hero-Option"
                            data-hero-name="<?= htmlspecialchars($name) ?>"
                            data-hero-class="<?= htmlspecialchars($hero['First_Class']) ?>"
                            data-hero-second-class="<?= htmlspecialchars($hero['Second_Class']) ?>"
                            data-hero-lane="<?= htmlspecialchars($hero['First_Lane']) ?>"
                            data-hero-second-lane="<?= htmlspecialchars($hero['Second_Lane']) ?>"
                            onclick="selectHero(this)">

                            <img src="<?= $img ?>" class="hero-thumbnail" alt="<?= htmlspecialchars($name) ?>">
                            <span><?= htmlspecialchars($name) ?></span>
                        </div>
                    <?php endforeach; ?>
                </div>
            </div>
        </div>

        <!-- Select Class & Select Lane -->
        <div class="ClassAndLane-Container">
            <!-- Class -->
            <div class="Class-Container">
                <h1>Select Class</h1>
                <div class="Class-Dropdown">
                    <div class="Class-Dropdown-Toggle" onclick="toggleClassDropdown()">
                        <span id="selected-class-text">Select Class</span>
                        <span class="icon">▾</span>
                    </div>
                    <div id="Class-Dropdown-Menu" class="hidden">
                        <?php foreach ($heroClasses as $class): ?>
                            <div class="Dropdown-Option" onclick="selectClass('<?= htmlspecialchars($class) ?>')">
                                <?= htmlspecialchars($class) ?>
                            </div>
                        <?php endforeach; ?>
                    </div>
                </div>
            </div>

            <!-- Lane -->
            <div class="Lane-Container">
                <h1>Select Lane</h1>
                <div class="Lane-Dropdown">
                    <div class="Lane-Dropdown-Toggle" onclick="toggleLaneDropdown()">
                        <span id="selected-lane-text">Select Lane</span>
                        <span class="icon">▾</span>
                    </div>
                    <div id="Lane-Dropdown-Menu" class="hidden">
                        <?php foreach ($lanes as $lane): ?>
                            <div class="Dropdown-Option" onclick="selectLane('<?= htmlspecialchars($lane) ?>')">
                                <?= htmlspecialchars($lane) ?>
                            </div>
                        <?php endforeach; ?>
                    </div>
                </div>
            </div>
        </div>

    </div> <!-- ปิด Input-Container -->

    <!-- Item Header -->
    <div class="Item-Header">
        <p>-- Item --</p>
    </div>
    <!-- Support Item -->
    <div id="SupportItemSection" class="hidden"> <!-- Use class "hidden" for consistency -->
        <h1>Select Support Item <span>(Only 1 item)</span></h1>
        <div id="selected-support-item" class="dropdown-btn" onclick="toggleSupportDropdown()">
            -- Select Support Item --
        </div>
        <div id="Support-Dropdown-Menu" class="dropdown-menu hidden">
            <?php foreach ($categorizedItems['support'] as $item): ?>
                <div class="dropdown-item"
                     data-item-id="<?= htmlspecialchars($item['id']) ?>"
                     onclick="selectSupportItemJS('<?= htmlspecialchars($item['id']) ?>', '<?= htmlspecialchars($item['name']) ?>', '<?= htmlspecialchars($item['path']) ?>')">
                    <img src="<?= htmlspecialchars($item['path']) ?>" class="dropdown-img" alt="<?= htmlspecialchars($item['name']) ?>">
                    <span class="dropdown-text"><?= htmlspecialchars($item['name']) ?></span>
                </div>
            <?php endforeach; ?>
        </div>
        <input type="hidden" id="selectedSupportItemId" name="support_item_id">
    </div>

    <!-- Farm Item -->
    <div id="FarmItemSection" class="hidden">
        <h1>Select Farm Item <span>(Only 1 item)</span></h1>
        <div id="selected-farm-item" class="dropdown-btn" onclick="toggleFarmDropdown()">
            -- Select Farm Item --
        </div>
        <div id="Farm-Dropdown-Menu" class="dropdown-menu hidden">
            <?php foreach ($categorizedItems['farm'] as $item): ?>
                <div class="dropdown-item Farm-Item-Option"
                     data-item-id="<?= htmlspecialchars($item['id']) ?>"
                     data-item-name="<?= htmlspecialchars($item['name']) ?>"
                     data-item-path="<?= htmlspecialchars($item['path']) ?>"
                     onclick="selectFarmItemJS(this)">
                    <img src="<?= htmlspecialchars($item['path']) ?>" class="dropdown-img" alt="<?= htmlspecialchars($item['name']) ?>">
                    <span class="dropdown-text"><?= htmlspecialchars($item['name']) ?></span>
                </div>
            <?php endforeach; ?>
        </div>
        <input type="hidden" id="selectedFarmItemId" name="farm_item_id">
    </div>

    <!-- Item Selection Popup -->
    <div id="item-popup" class="popup-overlay hidden">
        <div class="popup-content">
            <input id="item-search-box" type="text" placeholder="Search Items" oninput="filterItemList('item-search-box', 'popup-item-list')">
            <div class="popup-item-grid" id="popup-item-list">
                <?php foreach ($categorizedItems['all'] as $itemData): ?>
                    <div class="item-container"
                         data-item-id="<?= htmlspecialchars($itemData['id']) ?>"
                         data-item-name="<?= htmlspecialchars($itemData['name']) ?>"
                         onclick="selectPopupItem('<?= htmlspecialchars($itemData['id']) ?>', '<?= htmlspecialchars($itemData['name']) ?>', '<?= htmlspecialchars($itemData['path']) ?>')">
                        <img src="<?= htmlspecialchars($itemData['path']) ?>" alt="<?= htmlspecialchars($itemData['name']) ?>">
                    </div>
                <?php endforeach; ?>
            </div>
            <button class="popup-close" onclick="closeItemPopup()">X</button> <!-- Removed 'meta' param -->
        </div>
    </div>
    <!-- Force Container -->
    <div class="Force-Container">
        <div class="Force-Text">
            <h1>Select Force Item</h1>
            <h2 id="Force-MaxItem">(Max 3 item)</h2>
        </div>
        <div class="Force-Button">
            <?php for ($i = 0; $i < 3; $i++): ?>
                <button id="force-btn-<?= $i ?>" onclick="forceBanButtonClick(event,'force',<?= $i ?>)">
                    <span class="plus-icon">+</span>
                </button>
            <?php endfor; ?>
        </div>
    </div>

    <!-- BAN Container -->
    <div class="BAN-Container">
        <div class="BAN-Text">
            <h1>Select BAN Item</h1>
            <h2 id="BAN-BANItem">(Max 3 item)</h2>
        </div>
        <div class="BAN-Button">
            <?php for ($i = 0; $i < 3; $i++): ?>
                <button id="ban-btn-<?= $i ?>" onclick="forceBanButtonClick(event,'ban',<?= $i ?>)">
                    <span class="plus-icon">+</span>
                </button>
            <?php endfor; ?>
        </div>
    </div>

    <div class="Calculate-Container">
        <p>//////////////////</p>
        <button id="calculate-btn">Calculate</button>
        <p>//////////////////</p>
    </div>
    <div class="Result-Container">
        <div class="Result-Header">
            <p>-- Result Calculate --</p>
        </div>
        <div class="Early-Game">
            <div class="Early-Text">
                <h1>Early Game </h1>
                <h2>(Level : 3 | Budget : 2,700)</h2>
            </div>
            <div class="Early-Image-Container">
            </div>
        </div>
        <div class="Mid-Game">
            <div class="Mid-Text">
                <h1>Mid Game </h1>
                <h2>(Level : 9 | Budget : 7,500)</h2>
            </div>
            <div class="Mid-Image-Container">
            </div>
        </div>
        <div class="Late-Game">
            <div class="Late-Text">
                <h1>Late Game </h1>
                <h2>(Level : 15 | Budget : 14,000)</h2>
            </div>
            <div class="Late-Image-Container">
            </div>
        </div>
    </div>
    <div class="Compare-Container">
        <div class="Compare-Header"><p>-- Result vs Meta Item --</p></div>
        <div class="Compare-Media" style="display: flex; gap: 2vw;">
            <div class="Compare-Left" style="flex: 1;">
                <div class="Select-Game-Phase-Container">
                    <h1>Select Game Phase</h1>
                    <div class="game-phase-box">
                        <select id="game-phase">
                            <option value="">Select</option>
                            <option value="early">Early Game</option>
                            <option value="mid">Mid Game</option>
                            <option value="late">Late Game</option>
                        </select>
                        <div class="input-box">
                            <div class="input-item"></div>
                            <div class="input-item"></div>
                            <div class="input-item"></div>
                            <div class="input-item"></div>
                            <div class="input-item"></div>
                            <div class="input-item"></div>
                        </div>
                    </div>
                </div>

                <!-- VS Section -->
                <div class="VS-Container">
                    <p>VS</p>
                </div>
                <div class="Comapre-Container"><button id="compare-btn">Compare</button></div>

                <!-- Select Meta Item Section -->
                <div class="Select-Meta-Item-Container">
                    <h1>Select Meta Item</h1>
                    <div class="Select-Meta-Item-Button">
                        <?php for ($i = 0; $i < 6; $i++): ?>
                            <button id="meta-btn-<?= $i ?>" onclick="forceBanButtonClick(event, 'meta', <?= $i ?>)">
                                <span class="plus-icon">+</span>
                            </button>
                        <?php endfor; ?>
                    </div>
                </div>
                <div id="meta-item-popup" class="popup-overlay hidden">
                    <div class="popup-content">
                        <input id="meta-search-box" type="text"
                            placeholder="Search Items"
                            oninput="filterItemList('meta-search-box','meta-popup-item-list')">
                        <div id="meta-popup-item-list" class="popup-item-grid">
                            <?php foreach ($categorizedItems['all'] as $itemData): ?>
                                <div class="item-container"
                                    data-item-id="<?= htmlspecialchars($itemData['id']) ?>"
                                    data-item-name="<?= htmlspecialchars($itemData['name']) ?>"
                                    data-item-path="<?= htmlspecialchars($itemData['path']) ?>"
                                    onclick="selectPopupItem(
                                        '<?= htmlspecialchars($itemData['id']) ?>',
                                        '<?= htmlspecialchars($itemData['name']) ?>',
                                        '<?= htmlspecialchars($itemData['path']) ?>'
                                    )">
                                <img src="<?= htmlspecialchars($itemData['path']) ?>"
                                    alt="<?= htmlspecialchars($itemData['name']) ?>">
                                </div>
                            <?php endforeach; ?>
                        </div>
                        <button class="popup-close" onclick="closeItemPopup('meta')">Close</button>
                    </div>
                </div>

            </div>

            <!-- ฝั่งขวา (Radar Chart) -->
            <div class="Chart-Compare" style="flex: 1;">
                <canvas id="CompareChartCanvas" width="600" height="400"></canvas>
            </div>

        </div> <!-- จบ Compare-Media -->
    </div>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="src/common/scripts/main.js"></script>
</body>
</html>