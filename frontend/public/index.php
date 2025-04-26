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

/* ---------- ฟังก์ชันดึงรูปภาพไอเท็มทั้งหมด ---------- */
function getAllItemImages($directory)
{
    $exts   = ['jpg', 'jpeg', 'png', 'webp'];
    $images = [];
    if (is_dir($directory)) {
        $it = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($directory));
        foreach ($it as $file) {
            if (!$file->isDir()) {
                $ext = strtolower(pathinfo($file->getFilename(), PATHINFO_EXTENSION));
                if (in_array($ext, $exts)) {
                    $path    = str_replace(__DIR__ . '/', '', str_replace('\\', '/', $file->getPathname()));
                    $images[] = $path;
                }
            }
        }
    }
    return $images;
}
$allItemImages = getAllItemImages(__DIR__ . '/src/assets/images/item/');

/* ---------- ฟังก์ชันดึง Farm/Support Item ---------- */
$farmItemImages = array_map(
    fn($p) => str_replace(__DIR__ . '/', '', $p),
    glob(__DIR__ . '/src/assets/images/item/farm-item/*.{jpg,jpeg,png,webp}', GLOB_BRACE)
);
$supportItemImages = array_map(
    fn($p) => str_replace(__DIR__ . '/', '', $p),
    glob(__DIR__ . '/src/assets/images/item/support-item/*.{jpg,jpeg,png,webp}', GLOB_BRACE)
);
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
                        onclick="filterByClass('<?= rawurlencode($class) ?>')">
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
    <div id="SupportItemSection" class="hidden">
        <h1>Select Support Item <span>(Only 1 item)</span></h1>
        <div id="selected-support-item" class="dropdown-btn" onclick="toggleSupportDropdown()">
            -- Select Support Item --
        </div>
        <div id="Support-Dropdown-Menu" class="dropdown-menu hidden">
            <?php foreach ($supportItemImages as $itemPath): ?>
                <?php $itemName = pathinfo($itemPath, PATHINFO_FILENAME); ?>
                <div class="dropdown-item" onclick="selectSupportItem('<?= $itemName ?>','<?= $itemPath ?>')">
                    <img src="<?= $itemPath ?>" class="dropdown-img" alt="<?= $itemName ?>">
                    <span class="dropdown-text"><?= $itemName ?></span>
                </div>
            <?php endforeach; ?>
        </div>
        <input type="hidden" id="selectedSupportItem" name="support_item">
    </div>

    <!-- Farm Item -->
    <div id="FarmItemSection" class="hidden">
        <h1>Select Farm Item <span>(Only 1 item)</span></h1>
        <div id="selected-farm-item" class="dropdown-btn" onclick="toggleFarmDropdown()">
            -- Select Farm Item --
        </div>
        <div id="Farm-Dropdown-Menu" class="dropdown-menu hidden">
            <?php foreach ($farmItemImages as $itemPath): ?>
                <?php $itemName = pathinfo($itemPath, PATHINFO_FILENAME); ?>
                <div class="dropdown-item Farm-Item-Option" data-item-name="<?= $itemName ?>">
                    <img src="<?= $itemPath ?>" class="dropdown-img" alt="<?= $itemName ?>">
                    <span class="dropdown-text"><?= $itemName ?></span>
                </div>
            <?php endforeach; ?>
        </div>
        <input type="hidden" id="selectedFarmItem" name="farm_item">
    </div>

    <!-- Item Selection Popup -->
    <div id="item-popup" class="popup-overlay hidden">
        <div class="popup-content">
            <input id="item-search" type="text" placeholder="Search Items" oninput="filterItemList()">
            <div id="popup-item-list" class="popup-item-grid">
                <?php foreach ($allItemImages as $itemPath): ?>
                    <?php $itemName = pathinfo($itemPath, PATHINFO_FILENAME); ?>
                    <div class="item-container" onclick="selectPopupItem('<?= htmlspecialchars($itemName) ?>','<?= htmlspecialchars($itemPath) ?>')">
                        <img src="<?= $itemPath ?>" alt="<?= htmlspecialchars($itemName) ?>">
                    </div>
                <?php endforeach; ?>
            </div>
            <button class="popup-close" onclick="closeItemPopup()">X</button>
        </div>
    </div>

    <!-- Meta Item Popup -->
    <div id="meta-item-popup" class="popup-overlay hidden">
        <div class="popup-content">
            <input id="meta-search" type="text" placeholder="Search Items" oninput="filterItemList('meta')">
            <div id="meta-popup-item-list" class="popup-item-grid">
                <?php foreach ($allItemImages as $itemPath): ?>
                    <?php $itemName = pathinfo($itemPath, PATHINFO_FILENAME); ?>
                    <div class="item-container" onclick="selectPopupItem('<?= htmlspecialchars($itemName) ?>','<?= htmlspecialchars($itemPath) ?>')">
                        <img src="<?= $itemPath ?>" alt="<?= htmlspecialchars($itemName) ?>">
                    </div>
                <?php endforeach; ?>
            </div>
            <button class="popup-close" onclick="closeItemPopup('meta')">Close</button>
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
                <button id="ban-btn-<?= @$i ?>" onclick="forceBanButtonClick(event,'ban',<?= $i ?>)">
                    <span class="plus-icon">+</span>
                </button>
            <?php endfor; ?>
        </div>
    </div>

    <div class="Calculate-Container">
        <p>//////////////////</p>
        <button>Calculate</button>
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
                <img>
                <img>
                <img>
                <img>
                <img>
                <img>
            </div>
        </div>
        <div class="Mid-Game">
            <div class="Mid-Text">
                <h1>Mid Game </h1>
                <h2>(Level : 9 | Budget : 7,500)</h2>
            </div>
            <div class="Mid-Image-Container">
                <img>
                <img>
                <img>
                <img>
                <img>
                <img>
            </div>
        </div>
        <div class="Late-Game">
            <div class="Late-Text">
                <h1>Late Game </h1>
                <h2>(Level : 15 | Budget : 14,000)</h2>
            </div>
            <div class="Late-Image-Container">
                <img>
                <img>
                <img>
                <img>
                <img>
                <img>
            </div>
        </div>
    </div>
    <div class="Compare-Container">
        <div class="Compare-Header">
            <p>-- Result vs Meta Item --</p>
        </div>
        <div class="Select-Game-Phase-Container">
            <h1>Select Game Phase</h1>
            <div class="game-phase-box">
                <select id="game-phase">
                    <option value="select">Select</option>
                    <option value="early">Early Game</option>
                    <option value="mid">Mid Game</option>
                    <option value="late">Late Game</option>
                </select>
                <!-- ช่อง 6 ช่องที่คุณต้องการ -->
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
        <!-- Select Meta Item Section -->
        <div class="Select-Meta-Item-Container">
            <h1>Select Meta Item</h1>
            <div class="Select-Meta-Item-Button">
                <button id="meta-btn-0" onclick="forceBanButtonClick(event, 'meta', 0)">Click Here</button>
                <button id="meta-btn-1" onclick="forceBanButtonClick(event, 'meta', 1)">Click Here</button>
                <button id="meta-btn-2" onclick="forceBanButtonClick(event, 'meta', 2)">Click Here</button>
                <button id="meta-btn-3" onclick="forceBanButtonClick(event, 'meta', 3)">Click Here</button>
                <button id="meta-btn-4" onclick="forceBanButtonClick(event, 'meta', 4)">Click Here</button>
                <button id="meta-btn-5" onclick="forceBanButtonClick(event, 'meta', 5)">Click Here</button>
            </div>
        </div>
        <!-- Meta Item Popup -->
        <div id="meta-item-popup" class="popup-overlay hidden">
            <div class="popup-content">
                <input id="meta-search" type="text" placeholder="Search Items" oninput="filterItemList('meta')">
                <div id="meta-popup-item-list" class="popup-item-grid">
                    <?php foreach ($allItemImages as $itemPath): ?>
                        <?php $itemName = pathinfo($itemPath, PATHINFO_FILENAME); ?>
                        <div class="item-container" onclick="selectPopupItem('<?= htmlspecialchars($itemName) ?>', '<?= htmlspecialchars($itemPath) ?>')">
                            <img src="<?= $itemPath ?>" alt="<?= htmlspecialchars($itemName) ?>">
                        </div>
                    <?php endforeach; ?>
                </div>
                <button class="popup-close" onclick="closeItemPopup('meta')">Close</button>
            </div>
        </div>
        <!-- Radar Chart (empty placeholder for now) -->
        <div class="Chart-Compare">
            <canvas id="CompareChartCanvas" width="600" height="400"></canvas>
        </div>
    </div>
    <!-- Inline Script สำหรับ Item Popup -->
    <script>
        let currentSlot = null;
        let currentType = null;

        // ฟังก์ชันที่ใช้ในการคลิกปุ่ม Force/Ban/Meta
        function forceBanButtonClick(event, type, slotIndex) {
            const btn = event.currentTarget;

            // ถ้ามีไอเทมในปุ่มแล้ว ให้เคลียร์
            if (btn.querySelector('img')) {
                btn.innerHTML = "Click Here";
            } else {
                currentSlot = slotIndex;
                currentType = type;
                document.getElementById('meta-search').value = ""; // เคลียร์ช่องค้นหา
                if (type === 'meta') {
                    document.getElementById('meta-item-popup').classList.remove('hidden'); // เปิด Meta Item Popup
                } else {
                    document.getElementById('item-popup').classList.remove('hidden'); // เปิด Item Popup
                }
            }
        }

        // ปิด popup
        function closeItemPopup(type) {
            if (type === 'meta') {
                document.getElementById('meta-item-popup').classList.add('hidden');
            } else {
                document.getElementById('item-popup').classList.add('hidden');
            }
        }

        // เมื่อเลือกไอเทมจาก popup
        function selectPopupItem(itemName, itemPath) {
            const buttonId = `${currentType}-btn-${currentSlot}`;
            const button = document.getElementById(buttonId);

            // เพิ่มไอเทมที่เลือกเข้าไปในปุ่ม
            button.innerHTML = `<img src="${itemPath}" alt="${itemName}" style="width:100%; height:100%; object-fit:contain;">`;
        }

        // ฟังก์ชันค้นหาไอเทมใน popup
        function filterItemList(type) {
            const searchValue = document.getElementById('meta-search').value.toLowerCase();
            const items = document.querySelectorAll(`#${type}-popup-item-list .item-container`);
            items.forEach(item => {
                let name = item.querySelector('img').getAttribute('alt').toLowerCase();
                item.style.display = name.includes(searchValue) ? 'inline-block' : 'none';
            });
        }
        // ฟังก์ชันกรอง class แล้วรีโหลดหน้า
        function filterByClass(encodedClass) {
            const params = new URLSearchParams(window.location.search);
            params.set('filter', decodeURIComponent(encodedClass));
            window.location.search = params.toString();
        }
    </script>
    <script src="src/common/scripts/dropdown.js"></script>
</body>

</html>