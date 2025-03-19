<?php
// Database connection settings
$host = "localhost";
$username = "root";
$password = "";
$database = "rov"; // Replace with your actual database name

// Create database connection
try {
  $conn = new PDO("mysql:host=$host;dbname=$database", $username, $password);
  $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
  die("Connection failed: " . $e->getMessage());
}

// Determine sort order
$sort = isset($_GET['sort']) ? $_GET['sort'] : 'name';
$validSorts = ['name' => 'Hero_Name', 'first_class' => 'First_Class', 'second_class' => 'Second_Class'];
$sortField = isset($validSorts[$sort]) ? $validSorts[$sort] : 'Hero_Name';

// Get filter type if set
$filterType = isset($_GET['filter']) ? $_GET['filter'] : '';

// Get search query if set
$searchQuery = isset($_GET['search']) ? $_GET['search'] : '';

// Prepare the SQL query based on filters and search
$sql = "SELECT * FROM heroes WHERE 1=1";
$params = [];

if (!empty($filterType)) {
  $sql .= " AND (First_Class = :filterType OR Second_Class = :filterType)";
  $params[':filterType'] = $filterType;
}

if (!empty($searchQuery)) {
  $sql .= " AND Hero_Name LIKE :searchQuery";
  $params[':searchQuery'] = "%$searchQuery%";
}

$sql .= " ORDER BY $sortField ASC";

// Execute query
$stmt = $conn->prepare($sql);
$stmt->execute($params);
$heroes = $stmt->fetchAll(PDO::FETCH_ASSOC);

// Get unique hero classes for filter buttons
$classesQuery = $conn->query("SELECT DISTINCT First_Class FROM heroes UNION SELECT DISTINCT Second_Class FROM heroes WHERE Second_Class IS NOT NULL");
$heroClasses = $classesQuery->fetchAll(PDO::FETCH_COLUMN);

/* ---------------------------------------------------------
   ฟังก์ชันสำหรับดึงไฟล์รูปทั้งหมดจากโฟลเดอร์ item 
   (รวมโฟลเดอร์ย่อย) โดยใช้ RecursiveDirectoryIterator
   --------------------------------------------------------- */
function getAllItemImages($directory) {
  $extensions = ['jpg','jpeg','png','webp'];
  $images = [];
  if (is_dir($directory)) {
    // ใช้ \RecursiveDirectoryIterator และ \RecursiveIteratorIterator จาก global namespace
    $iterator = new \RecursiveIteratorIterator(new \RecursiveDirectoryIterator($directory));
    foreach ($iterator as $file) {
      if (!$file->isDir()) {
        $ext = strtolower(pathinfo($file->getFilename(), PATHINFO_EXTENSION));
        if (in_array($ext, $extensions)) {
          // แปลง path จากระบบไฟล์ (absolute) เป็น relative URL
          $fullPath = str_replace('\\', '/', $file->getPathname());
          $relativePath = str_replace($_SERVER['DOCUMENT_ROOT'], '', $fullPath);
          $images[] = $relativePath;
        }
      }
    }
  }
  return $images;
}

// เรียกไฟล์รูปทั้งหมดจากโฟลเดอร์ item (รวมโฟลเดอร์ย่อย)
$allItemImages = getAllItemImages("image/item");

/* ---------------------------------------------------------
   ส่วนสำหรับ Farm Item และ Support Item (ใช้ glob)
   --------------------------------------------------------- */
$farmItemDir = "image/item/Farm Item";
$farmItemImages = glob($farmItemDir . "*.{jpg,jpeg,png,webp}", GLOB_BRACE);

$supportItemDir = "image/item/Support Item/";
$supportItemImages = glob($supportItemDir . "*.{jpg,jpeg,png,webp}", GLOB_BRACE);

?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1.0">
  <title>Recommender System</title>
  <link rel="stylesheet" href="./assets/css/style.css">
  <script src="./assets/js/node_modules/chart.js/dist/chart.umd.js"></script>
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
             $baseFileName = preg_replace('/[^a-zA-Z0-9]/', '', $heroName); // ลบอักขระพิเศษออกจากชื่อ
 
             $imageFolder = 'image/heroes/';
             $extensions = ['jpg', 'jpeg', 'png', 'webp'];
             $heroImage = 'image/placeholder.jpg'; // fallback
 
             foreach ($extensions as $ext) {
               $tryPath = $imageFolder . $hero['Hero_Name'] . '.' . $ext;
               if (file_exists($tryPath)) {
                 $heroImage = $tryPath;
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
      <button class="popup-close" onclick="closeItemPopup()">Close</button>
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
        <!-- ใช้ forceBanButtonClick() เพื่อเปิด popup หรือเคลียร์ไอเทม -->
        <button id="force-btn-<?= $i ?>" onclick="forceBanButtonClick(event, 'force', <?= $i ?>)">Click Here</button>
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
        <button id="ban-btn-<?= $i ?>" onclick="forceBanButtonClick(event, 'ban', <?= $i ?>)">Click Here</button>
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
      <p>-- Result vs Meta item --</p>
    </div>
    <div class="Compare-Media">
      <div class="Input-Space">
        <div class="Select-Game-Phase-Container">
          <h1>Select Game Phase</h1>
          <div class="Select-Game-Phase-Dropdown"></div>
          <div class="Result-Game-Phase-Container">
            <img>
            <img>
            <img>
            <img>
            <img>
            <img>
          </div>
        </div>
        <div class="VS-Container">
          <p>VS</p>
        </div>
        <div class="Select-Meta-Item-Container">
          <h1>Select Meta Item</h1>
          <div class="Select-Meta-Item-Button">
            <button></button>
            <button></button>
            <button></button>
            <button></button>
            <button></button>
            <button></button>
          </div>
        </div>
      </div>
      <div class="Chart-Compare">
        <canvas id="Chart-Compare"></canvas>
      </div>
    </div>
  </div>

  <!-- Inline Script สำหรับ Item Popup -->
  <script>
    let currentSlot = null;
    let currentType = null;

    // เมื่อคลิกปุ่ม Force/BAN
    function forceBanButtonClick(event, type, slotIndex) {
      const btn = event.currentTarget;
      // ถ้ามีไอเทมอยู่แล้วในปุ่ม => เคลียร์ให้กลับเป็น "Click Here"
      if (btn.querySelector('img')) {
        btn.innerHTML = "Click Here";
      } else {
        currentSlot = slotIndex;
        currentType = type;
        document.getElementById('item-search').value = "";
        document.getElementById('item-popup').classList.remove('hidden');
      }
    }

    // ปุ่ม Close ใน Popup
    function closeItemPopup() {
      document.getElementById('item-popup').classList.add('hidden');
    }

    // เมื่อเลือกไอเทมใน Popup ให้แสดงไอเทมนั้นในปุ่มที่คลิก (และไม่ปิด Popup)
    function selectPopupItem(itemName, itemPath) {
      const buttonId = (currentType === 'force')
        ? `force-btn-${currentSlot}`
        : `ban-btn-${currentSlot}`;
      const button = document.getElementById(buttonId);
      button.innerHTML = `<img src="${itemPath}" alt="${itemName}" style="width:100%; height:100%; object-fit:contain;">`;
      // ไม่ปิด Popup เพื่อให้ไอเทมยังคงแสดงอยู่
    }

    // ฟังก์ชันค้นหาไอเทมใน Popup
    function filterItemList() {
      const searchValue = document.getElementById('item-search').value.toLowerCase();
      const items = document.querySelectorAll('#popup-item-list .item-container');
      items.forEach(item => {
        let name = item.querySelector('img').getAttribute('alt').toLowerCase();
        item.style.display = name.includes(searchValue) ? 'inline-block' : 'none';
      });
    }
  </script>

  <!-- Script สำหรับ dropdown.js (Hero/Class/Lane) -->
  <script src="./assets/js/dropdown.js"></script>
</body>
</html>
