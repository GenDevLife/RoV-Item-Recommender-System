<?php
/* ---------- เชื่อมต่อฐานข้อมูลผ่านไฟล์ config ---------- */
$pdo = require __DIR__ . '/../../config/config.php';   // ← คืนค่า PDO มาในตัวแปร $pdo

/* ---------- การเตรียม Query ---------- */
$sort       = $_GET['sort']   ?? 'name';
$filterType = $_GET['filter'] ?? '';
$search     = $_GET['search'] ?? '';

$validSorts = [
    'name'         => 'Hero_Name',
    'first_class'  => 'First_Class',
    'second_class' => 'Second_Class',
];
$sortField  = $validSorts[$sort] ?? 'Hero_Name';

/* ---------- สร้าง SQL ตามเงื่อนไข ---------- */
$sql    = "SELECT * FROM heroes WHERE 1=1";
$params = [];

if ($filterType !== '') {
    $sql .= " AND (First_Class = :type OR Second_Class = :type)";
    $params[':type'] = $filterType;
}

if ($search !== '') {
    $sql .= " AND Hero_Name LIKE :search";
    $params[':search'] = "%$search%";
}

$sql .= " ORDER BY $sortField ASC";

/* ---------- ดึงข้อมูล ---------- */
$stmt   = $pdo->prepare($sql);
$stmt->execute($params);
$heroes = $stmt->fetchAll(PDO::FETCH_ASSOC);

/* ---------- ดึงคลาสทั้งหมด ---------- */
$classesStmt = $pdo->query(
    "SELECT DISTINCT First_Class FROM heroes
     UNION
     SELECT DISTINCT Second_Class FROM heroes WHERE Second_Class IS NOT NULL"
);
$heroClasses = $classesStmt->fetchAll(PDO::FETCH_COLUMN);

/* --------------------------------------------------------- 
   ฟังก์ชันสำหรับดึงไฟล์รูปทั้งหมดจากโฟลเดอร์ item 
   (รวมโฟลเดอร์ย่อย) โดยใช้ RecursiveDirectoryIterator 
   --------------------------------------------------------- */
function getAllItemImages($directory) {
    $extensions = ['jpg', 'jpeg', 'png', 'webp'];
    $images = [];
    if (is_dir($directory)) {
        $iterator = new \RecursiveIteratorIterator(new \RecursiveDirectoryIterator($directory));
        foreach ($iterator as $file) {
            if (!$file->isDir()) {
                $ext = strtolower(pathinfo($file->getFilename(), PATHINFO_EXTENSION));
                if (in_array($ext, $extensions)) {
                    $fullPath = str_replace('\\', '/', $file->getPathname());
                    $relativePath = str_replace(__DIR__ . '/', '', $fullPath);
                    $images[] = $relativePath;
                }
            }
        }
    }
    return $images;
}

// เรียกไฟล์รูปทั้งหมดจากโฟลเดอร์ item (รวมโฟลเดอร์ย่อย)
$allItemImages = getAllItemImages(__DIR__ . '/src/assets/images/item/');

/* --------------------------------------------------------- 
   ส่วนสำหรับ Farm Item และ Support Item (ใช้ glob) 
   --------------------------------------------------------- */
$farmItemDir = __DIR__ . '/src/assets/images/item/farm-item/';
$farmItemImages = glob($farmItemDir . "*.{jpg,jpeg,png,webp}", GLOB_BRACE);
$farmItemImages = array_map(function($path) {
    return str_replace(__DIR__ . '/', '', $path);
}, $farmItemImages);

$supportItemDir = __DIR__ . '/src/assets/images/item/support-item/';
$supportItemImages = glob($supportItemDir . "*.{jpg,jpeg,png,webp}", GLOB_BRACE);
$supportItemImages = array_map(function($path) {
    return str_replace(__DIR__ . '/', '', $path);
}, $supportItemImages);
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Recommender System</title>
    <link rel="stylesheet" href="src/styles/base/style.css">
</head>
<body>
    <!-- Input, Hero, Filter, และ Hero Dropdown -->
    <div class="Input-Container">
        <div class="Hero-Header">
            <p>-- Hero --</p>
        </div>
        <div class="Filter-Container">
            <h1>Select Filter</h1>
            <div class="Filter-Button">
                <button value="Fighter" onclick="filterByClass('Fighter')">Fighter</button>
                <button value="Tank" onclick="filterByClass('Tank')">Tank</button>
                <button value="Mage" onclick="filterByClass('Mage')">Mage</button>
                <button value="Carry" onclick="filterByClass('Carry')">Carry</button>
                <button value="Support" onclick="filterByClass('Support')">Support</button>
            </div>
        </div>
        <div class="Hero-Container">
            <h1>Select Hero</h1>
            <div class="Hero-Dropdown">
                <div class="Hero-Dropdown-Toggle" onclick="toggleDropdown()">
                    <span id="selected-text">Select</span>
                    <span class="icon" id="hero-dropdown-icon">▾</span>
                </div>
                <div class="hidden" id="Hero-Dropdown-Menu">
                    <input type="text" id="hero-search-box" placeholder="Select" oninput="HerofilterOption()">
                    <?php foreach ($heroes as $hero): ?>
                        <?php
                        $heroName = $hero['Hero_Name'];
                        $baseFileName = preg_replace('/[^a-zA-Z0-9]/', '', $heroName);
                        
                        $imageFolder = 'src/assets/images/heroes/'; // Path สำหรับ HTML
                        $serverImageFolder = __DIR__ . '/src/assets/images/heroes/'; // Path สำหรับระบบไฟล์
                        $heroImage = 'src/assets/images/placeholder.jpg'; // Default
                        $extensions = ['jpg', 'jpeg', 'png', 'webp'];
                        
                        foreach ($extensions as $ext) {
                            $tryPath = $serverImageFolder . $hero['Hero_Name'] . '.' . $ext;
                            if (file_exists($tryPath)) {
                                $heroImage = $imageFolder . $hero['Hero_Name'] . '.' . $ext;
                                break;
                            }
                        }
                        ?>
                        <div class="Hero-Option"
                            data-hero-name="<?= htmlspecialchars($heroName) ?>"
                            data-hero-class="<?= htmlspecialchars($hero['First_Class']) ?>"
                            data-hero-second-class="<?= htmlspecialchars($hero['Second_Class']) ?>"
                            onclick="selectHero(this)">
                            <img src="<?= $heroImage ?>" class="hero-thumbnail" alt="<?= htmlspecialchars($heroName) ?>">
                            <span><?= htmlspecialchars($heroName) ?></span>
                        </div>
                    <?php endforeach; ?>
                </div>
            </div>
        </div>
        <div class="ClassAndLane-Container">
            <div class="Class-Container">
                <h1>Select Class</h1>
                <div class="Class-Dropdown">
                    <div class="Class-Dropdown-Toggle" onclick="toggleClassDropdown()">
                        <span id="selected-class-text">Select Class</span>
                        <span class="icon">?</span>
                    </div>
                    <div class="hidden" id="Class-Dropdown-Menu">
                        <div class="Dropdown-Option" onclick="selectClass('Fighter')">Fighter</div>
                        <div class="Dropdown-Option" onclick="selectClass('Tank')">Tank</div>
                        <div class="Dropdown-Option" onclick="selectClass('Mage')">Mage</div>
                        <div class="Dropdown-Option" onclick="selectClass('Carry')">Carry</div>
                        <div class="Dropdown-Option" onclick="selectClass('Support')">Support</div>
                    </div>
                </div>
            </div>
            <div class="Lane-Container">
                <h1>Select Lane</h1>
                <div class="Lane-Dropdown">
                    <div class="Lane-Dropdown-Toggle" onclick="toggleLaneDropdown()">
                        <span id="selected-lane-text">Select Lane</span>
                        <span class="icon">?</span>
                    </div>
                    <div id="FarmItemSection" class="hidden">
                        <h1>Select Farm Item <span>(Only 1 item)</span></h1>
                        <div id="selected-farm-item" class="dropdown-btn" onclick="toggleFarmDropdown()">-- Select Farm Item --</div>
                        <div id="Farm-Dropdown-Menu" class="dropdown-menu hidden">
                            <?php
                            foreach ($farmItemImages as $itemPath) {
                                $itemName = pathinfo($itemPath, PATHINFO_FILENAME);
                                echo "<div class='dropdown-item' onclick=\"selectFarmItem('$itemName', '$itemPath')\">
                                        <img src='$itemPath' class='dropdown-img' alt='$itemName'>
                                        <span class='dropdown-text'>$itemName</span>
                                    </div>";
                            }
                            ?>
                        </div>
                    </div>
                    <input type="hidden" id="selectedFarmItem" name="farm_item">
                    <div id="SupportItemSection" class="hidden">
                        <h1>Select Support Item <span>(Only 1 item)</span></h1>
                        <div id="selected-support-item" class="dropdown-btn" onclick="toggleSupportDropdown()">-- Select Support Item --</div>
                        <div id="Support-Dropdown-Menu" class="dropdown-menu hidden">
                            <?php
                            foreach ($supportItemImages as $itemPath) {
                                $itemName = pathinfo($itemPath, PATHINFO_FILENAME);
                                echo "<div class='dropdown-item' onclick=\"selectSupportItem('$itemName', '$itemPath')\">
                                        <img src='$itemPath' class='dropdown-img' alt='$itemName'>
                                        <span class='dropdown-text'>$itemName</span>
                                    </div>";
                            }
                            ?>
                        </div>
                    </div>
                    <input type="hidden" id="selectedSupportItem" name="support_item">
                    <div class="hidden" id="Lane-Dropdown-Menu">
                        <div class="Dropdown-Option" onclick="selectLane('Dark Slayer Lane')">Dark Slayer Lane</div>
                        <div class="Dropdown-Option" onclick="selectLane('Abyssal Dragon Lane')">Abyssal Dragon Lane</div>
                        <div class="Dropdown-Option" onclick="selectLane('Middle Lane')">Middle Lane</div>
                        <div class="Dropdown-Option" onclick="selectLane('Jungle')">Jungle</div>
                        <div class="Dropdown-Option" onclick="selectLane('Roaming')">Roaming</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="Item-Header">
        <p>-- Item --</p>
    </div>
    <!-- Item Selection Popup with Search -->
    <div id="item-popup" class="popup-overlay hidden">
        <div class="popup-content">
            <input id="item-search" type="text" placeholder="Search Items" oninput="filterItemList()">
            <div id="popup-item-list" class="popup-item-grid">
                <?php foreach ($allItemImages as $itemPath): ?>
                    <?php $itemName = pathinfo($itemPath, PATHINFO_FILENAME); ?>
                    <div class="item-container" onclick="selectPopupItem('<?= htmlspecialchars($itemName) ?>', '<?= htmlspecialchars($itemPath) ?>')">
                        <img src="<?= $itemPath ?>" alt="<?= htmlspecialchars($itemName) ?>">
                    </div>
                <?php endforeach; ?>
            </div>
            <button class="popup-close" onclick="closeItemPopup()">X</button>
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
                <button id="force-btn-<?= $i ?>" onclick="forceBanButtonClick(event, 'force', <?= $i ?>)">
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
                <button id="ban-btn-<?= $i ?>" onclick="forceBanButtonClick(event, 'ban', <?= $i ?>)">
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
    </script>
    <script src="src/common/scripts/dropdown.js"></script>
</body>
</html>