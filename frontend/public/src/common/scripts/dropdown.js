const optionsList = document.getElementById("HeroOptionList");
const dropdownMenu = document.getElementById("Hero-Dropdown-Menu");
const selectedText = document.getElementById("selected-text");
const classSelect = document.getElementById("class-select");
const laneSelect = document.getElementById("lane-select");
const farmSection = document.getElementById("FarmItemSection");

function toggleDropdown() {
  dropdownMenu.classList.toggle("hidden");
  document.getElementById("hero-search-box").value = "";
  HerofilterOptions();
}

function filterOptions() {
  const searchValue = document.getElementById("hero-search-box").value.toLowerCase();
  optionsList.innerHTML = "";

  items.filter(item => item.name.toLowerCase().includes(searchValue)).forEach(item => {
    const div = document.createElement("div");
    div.classList.add("option");
    div.innerHTML = `<img src="${item.img}" alt="${item.name}"><span>${item.name}</span>`;
    div.onclick = () => {
      selectedText.textContent = item.name;
      dropdownMenu.classList.add("hidden");
    };
    optionsList.appendChild(div);
  });
}
function toggleDropdown() {
  document.getElementById('Hero-Dropdown-Menu').classList.toggle('hidden');
}
function HerofilterOption() {
  const input = document.getElementById('hero-search-box').value.toLowerCase();
  const options = document.querySelectorAll('.Hero-Option');
  options.forEach(option => {
    const name = option.dataset.heroName.toLowerCase();
    option.style.display = name.includes(input) ? 'flex' : 'none';
  });
}
function selectHero(heroElement) {
  const heroName = heroElement.dataset.heroName;
  const firstClass = heroElement.dataset.heroClass;
  const secondClass = heroElement.dataset.heroSecondClass || "";
  const firstLane = heroElement.dataset.heroLane;
  const secondLane = heroElement.dataset.heroSecondLane || "";

  document.getElementById("selected-text").innerText = heroName;
  document.getElementById("Hero-Dropdown-Menu").classList.add("hidden");

  // === แสดง Support Item ถ้าเป็น Support เท่านั้น ===
  const isSupport = firstClass === "Support" || secondClass === "Support";
  const supportSection = document.getElementById("SupportItemSection");
  if (isSupport) {
    supportSection.classList.remove("hidden");
  } else {
    supportSection.classList.add("hidden");
  }
  //ซ่อน/แสดงปุ่ม Force/BAN ที่ 3
  const forceBtn2 = document.getElementById("force-btn-2");
  const banBtn2 = document.getElementById("ban-btn-2");

  const forceMaxText = document.getElementById("Force-MaxItem");
  const banMaxText = document.getElementById("BAN-BANItem");

  if (isSupport) {
    forceBtn2.style.display = "none";
    banBtn2.style.display = "none";
    forceMaxText.innerText = "(Max 2 item)";
    banMaxText.innerText = "(Max 2 item)";
  } else {
    forceBtn2.style.display = "inline-block";
    banBtn2.style.display = "inline-block";
    forceMaxText.innerText = "(Max 3 item)";
    banMaxText.innerText = "(Max 3 item)";
  }
}
document.addEventListener("DOMContentLoaded", function () {
  const supportItems = document.querySelectorAll(".Support-Item-Option");

  supportItems.forEach((item) => {
    item.addEventListener("click", function () {
      // ลบ .selected จากทั้งหมดก่อน
      supportItems.forEach((i) => i.classList.remove("selected"));

      // เพิ่ม .selected ให้ไอเทมที่คลิก
      item.classList.add("selected");

      // ดึงชื่อไอเทมที่เลือก
      const selectedItemName = item.dataset.itemName;
      console.log("Selected Support Item:", selectedItemName);
    });
  });

  const farmItems = document.querySelectorAll(".Farm-Item-Option");
  farmItems.forEach((item) => {
    item.addEventListener("click", function () {
      const name = item.dataset.itemName;
      const img = item.querySelector("img").src;

      // ลบ selected ก่อน แล้วใส่ใหม่
      farmItems.forEach(i => i.classList.remove("selected"));
      item.classList.add("selected");

      const selected = document.getElementById("selected-farm-item");
      selected.innerHTML = `<img src="${img}" alt="${name}"><span>${name}</span>`;

      document.getElementById("Farm-Dropdown-Menu").classList.add("hidden");
      document.getElementById("selectedFarmItem").value = name;

      console.log("Selected Farm Item:", name);
    });
  });
});

function filterByClass(className) {
  const allOptions = document.querySelectorAll('.Hero-Option');
  document.getElementById('hero-search-box').value = ''; // Reset search box

  allOptions.forEach(option => {
    const heroClass = option.getAttribute('data-hero-class');
    const secondClass = option.getAttribute('data-hero-second-class');

    if (heroClass === className || secondClass === className) {
      option.style.display = 'flex';
    } else {
      option.style.display = 'none';
    }
  });

  document.getElementById('Hero-Dropdown-Menu').classList.remove('hidden'); // เปิด dropdown ให้เห็นเลย
}
// CLASS DROPDOWN
function toggleClassDropdown() {
  document.getElementById('Class-Dropdown-Menu').classList.toggle('hidden');
}
function selectClass(className) {
  document.getElementById('selected-class-text').textContent = className;
  document.getElementById('Class-Dropdown-Menu').classList.add('hidden');

  // ✅ ถ้าเลือก Support → แสดง Section ด้วยการตั้ง display
  const supportSection = document.getElementById("SupportItemSection");
  if (className === "Support") {
    supportSection.style.display = "block"; // ✅ โชว์
  } else {
    supportSection.style.display = "none"; // ✅ ซ่อน
  }
}


// LANE DROPDOWN
function toggleLaneDropdown() {
  document.getElementById('Lane-Dropdown-Menu').classList.toggle('hidden');
}
function selectLane(laneName) {
  document.getElementById('selected-lane-text').textContent = laneName;
  document.getElementById('Lane-Dropdown-Menu').classList.add('hidden');

  // ✅ ถ้าเลือก Farm → แสดง Farm Item Section
  const farmSection = document.getElementById("FarmItemSection");
  if (laneName === "Farm") {
    farmSection.classList.remove("hidden");
  } else {
    farmSection.classList.add("hidden");
  }
}

function toggleSupportDropdown() {
  document.getElementById("Support-Dropdown-Menu").classList.toggle("hidden");
}
function toggleFarmDropdown() {
  document.getElementById("Farm-Dropdown-Menu").classList.toggle("hidden");
}

// เรียกตอนโหลดเพื่อดึงไอเทมจาก PHP มาใส่ใน dropdown
document.addEventListener("DOMContentLoaded", function () {
  const supportItemMenu = document.getElementById("Support-Dropdown-Menu");
  const supportItemSection = document.getElementById("SupportItemSection");

  // ซ่อนไว้ก่อน
  supportItemSection.classList.add("hidden");

  // ดึงรายการ Support Item (ที่ฝั่ง PHP generate มาใน index.php)
  const supportItems = document.querySelectorAll(".Support-Item-Option");

  supportItems.forEach((item) => {
    item.addEventListener("click", () => {
      const name = item.dataset.itemName;
      const img = item.querySelector("img").src;

      // แสดงชื่อและรูปบนปุ่ม dropdown
      const selected = document.getElementById("selected-support-item");
      selected.innerHTML = `<img src="${img}" alt="${name}"><span>${name}</span>`;

      // ซ่อน dropdown หลังเลือก
      document.getElementById("Support-Dropdown-Menu").classList.add("hidden");

      console.log("Selected Support Item:", name); // ใช้ต่อในระบบได้เลย
    });
  });
});

// ✅ เมื่อเลือก Hero ให้แสดง Support Item Section เฉพาะเมื่อเป็น Support
function selectHero(heroElement) {
  const heroName = heroElement.dataset.heroName;
  const firstClass = heroElement.dataset.heroClass;
  const secondClass = heroElement.dataset.heroSecondClass || "";
  const firstLane = heroElement.dataset.heroLane;
  const secondLane = heroElement.dataset.heroSecondLane || "";

  // ตั้งค่า Hero Name
  document.getElementById("selected-text").innerText = heroName;
  document.getElementById("Hero-Dropdown-Menu").classList.add("hidden");
  
  // ✅ ซ่อน Support Item Section ทันที
  document.getElementById("SupportItemSection").classList.add("hidden");

  // ✅ ตั้งค่า Select Class แบบ Dynamic
  const classMenu = document.getElementById("Class-Dropdown-Menu");
  classMenu.innerHTML = "";

  if (firstClass) {
    const classOption1 = document.createElement("div");
    classOption1.className = "Dropdown-Option";
    classOption1.textContent = firstClass;
    classOption1.onclick = () => selectClass(firstClass);
    classMenu.appendChild(classOption1);
  }
  if (secondClass && secondClass !== firstClass) {
    const classOption2 = document.createElement("div");
    classOption2.className = "Dropdown-Option";
    classOption2.textContent = secondClass;
    classOption2.onclick = () => selectClass(secondClass);
    classMenu.appendChild(classOption2);
  }
  document.getElementById("selected-class-text").innerText = "Select Class";
  // ✅ ตั้งค่า Support Section
  const isSupport = firstClass === "Support" || secondClass === "Support";
  const supportSection = document.getElementById("SupportItemSection");
  if (isSupport) {
    supportSection.classList.remove("hidden");
  } else {
    supportSection.classList.add("hidden");
  }

  // ✅ ตั้งค่า Force/BAN Item Limit
  const forceBtn2 = document.getElementById("force-btn-2");
  const banBtn2 = document.getElementById("ban-btn-2");
  const forceMaxText = document.getElementById("Force-MaxItem");
  const banMaxText = document.getElementById("BAN-BANItem");

  if (isSupport) {
    forceBtn2.style.display = "none";
    banBtn2.style.display = "none";
    forceMaxText.innerText = "(Max 2 item)";
    banMaxText.innerText = "(Max 2 item)";
  } else {
    forceBtn2.style.display = "inline-block";
    banBtn2.style.display = "inline-block";
    forceMaxText.innerText = "(Max 3 item)";
    banMaxText.innerText = "(Max 3 item)";
  }

  // ✅ ตั้งค่า Lane
  const laneMenu = document.getElementById("Lane-Dropdown-Menu");
  laneMenu.innerHTML = "";

  if (firstLane) {
    const laneOption1 = document.createElement("div");
    laneOption1.className = "Dropdown-Option";
    laneOption1.textContent = firstLane;
    laneOption1.onclick = () => selectLane(firstLane);
    laneMenu.appendChild(laneOption1);
  }
  if (secondLane && secondLane !== firstLane) {
    const laneOption2 = document.createElement("div");
    laneOption2.className = "Dropdown-Option";
    laneOption2.textContent = secondLane;
    laneOption2.onclick = () => selectLane(secondLane);
    laneMenu.appendChild(laneOption2);
  }
  document.getElementById("selected-lane-text").innerText = "Select Lane";

   // ✅ ซ่อน Farm Item Section ไว้ด้วย
  farmSection.classList.add("hidden");
}

// Select all buttons in the button container
const buttons = document.querySelectorAll('.Filter-Button button');

// Add event listener to each button
buttons.forEach(button => {
  button.addEventListener('click', function () {
    // Remove 'selected' class from all buttons
    buttons.forEach(b => b.classList.remove('selected'));

    // Add 'selected' class to the clicked button
    this.classList.add('selected');
  });
});
function selectSupportItem(name, imgPath) {
  // แสดงชื่อ + รูปบนปุ่ม
  const selected = document.getElementById("selected-support-item");
  selected.innerHTML = `<img src="${imgPath}" alt="${name}" style="width:32px; height:32px;"> <span>${name}</span>`;

  // ปิด Dropdown
  document.getElementById("Support-Dropdown-Menu").classList.add("hidden");

  // อัปเดต hidden input เพื่อส่งค่าไป PHP
  document.getElementById("selectedSupportItem").value = name;

  console.log("Selected Support Item:", name);
}
let currentMetaButtonIndex = null; // จำปุ่ม meta ที่กดไว้
// =============================
// เปิด Popup สำหรับ Select Meta Item ใต้ปุ่ม
function forceBanButtonClick(event, type, index) {
  if (type === 'meta') {
    currentMetaButtonIndex = index;
    const popup = document.getElementById('meta-item-popup');
    const button = document.getElementById(`meta-btn-${index}`);

    popup.style.top = (button.offsetTop + button.offsetHeight + 5) + 'px'; // ห่างจากปุ่ม 5px
    popup.style.left = button.offsetLeft + 'px';

    popup.classList.add('show');
  }
}

// =============================
// เลือกไอเทมจาก Popup แล้วเอาไปใส่ปุ่มที่กด
function selectPopupItem(name, imgPath) {
  if (currentMetaButtonIndex !== null) {
    const button = document.getElementById(`meta-btn-${currentMetaButtonIndex}`);
    button.innerHTML = `<img src="${imgPath}" alt="${name}" style="width:32px;height:32px;">`;

    // ปิด popup หลังเลือกเสร็จ
    document.getElementById('meta-item-popup').classList.remove('show');

    console.log('Selected Meta Item:', name);
  }
}

// =============================
// ปิด Popup ด้วยปุ่ม Close
function closeItemPopup(type) {
  if (type === 'meta') {
    document.getElementById('meta-item-popup').classList.remove('show');
  }
}

// =============================
// (Option) ฟิลเตอร์ค้นหาไอเทมใน Popup
function filterItemList(type) {
  if (type === 'meta') {
    const searchValue = document.getElementById('meta-search').value.toLowerCase();
    const items = document.querySelectorAll('#meta-popup-item-list .item-container');

    items.forEach(item => {
      const itemName = item.querySelector('img').alt.toLowerCase();
      if (itemName.includes(searchValue)) {
        item.style.display = 'block';
      } else {
        item.style.display = 'none';
      }
    });
  }
}

let currentForceButtonIndex = null;
let currentBanButtonIndex = null;
function forceBanButtonClick(event, type, index) {
  const button = document.getElementById(`${type}-btn-${index}`);
  const popup = document.getElementById('meta-item-popup');

  // เช็กว่าเลือกไอเทมแล้วหรือยัง (มี data-selected อยู่ไหม)
  if (button.dataset.selected === "true") {
    // ถ้าเลือกแล้ว คลิกซ้ำ = เคลียร์ไอเทมออก
    button.innerHTML = '<span class="plus-icon">+</span>';
    delete button.dataset.selected; // ลบ data-selected ออก
    return; // ไม่ต้องเปิด popup
  }
  // ถ้าไม่ได้เลือกไอเทม ➔ เปิด popup
  if (type === 'force') {
    currentForceButtonIndex = index;
    currentBanButtonIndex = null;
    currentMetaButtonIndex = null;
  } else if (type === 'ban') {
    currentForceButtonIndex = null;
    currentBanButtonIndex = index;
    currentMetaButtonIndex = null;
  } else if (type === 'meta') {
    currentForceButtonIndex = null;
    currentBanButtonIndex = null;
    currentMetaButtonIndex = index;
  }
  popup.classList.add('show');
}


function selectPopupItem(name, imgPath) {
  const popup = document.getElementById('meta-item-popup');
  if (currentForceButtonIndex !== null) {
    const button = document.getElementById(`force-btn-${currentForceButtonIndex}`);
    button.innerHTML = `<img src="${imgPath}" alt="${name}" style="width:40px;height:40px;">`;
    button.dataset.selected = "true"; // ✅ Mark ว่าเลือกแล้ว
  } else if (currentBanButtonIndex !== null) {
    const button = document.getElementById(`ban-btn-${currentBanButtonIndex}`);
    button.innerHTML = `<img src="${imgPath}" alt="${name}" style="width:40px;height:40px;">`;
    button.dataset.selected = "true"; // ✅ Mark ว่าเลือกแล้ว
  } else if (currentMetaButtonIndex !== null) {
    const button = document.getElementById(`meta-btn-${currentMetaButtonIndex}`);
    button.innerHTML = `<img src="${imgPath}" alt="${name}" style="width:40px;height:40px;">`;
    button.dataset.selected = "true"; // ✅ Mark ว่าเลือกแล้ว
  }
  popup.classList.remove('show');
}


function closeItemPopup(type) {
  if (type === 'meta') {
    document.getElementById('meta-item-popup').classList.remove('show');
  }
}

function filterItemList(type) {
  if (type === 'meta') {
    const searchValue = document.getElementById('meta-search').value.toLowerCase();
    const items = document.querySelectorAll('#meta-popup-item-list .item-container');

    items.forEach(item => {
      const itemName = item.querySelector('img').alt.toLowerCase();
      if (itemName.includes(searchValue)) {
        item.style.display = 'block';
      } else {
        item.style.display = 'none';
      }
    });
  }
}

let compareChart = null;

function updateCompareChart(resultStats = [0, 0, 0, 0, 0], metaStats = [0, 0, 0, 0, 0]) {
    const ctx = document.getElementById('CompareChartCanvas').getContext('2d');

    if (compareChart) {
        compareChart.destroy();  // ลบกราฟเดิมก่อน
    }

    compareChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Attack', 'Defense', 'Magic', 'Speed', 'Utility'], // เปลี่ยนหมวดหมู่ตามจริงได้
            datasets: [
                {
                    label: 'Result Item',
                    data: resultStats,
                    borderColor: 'red',
                    backgroundColor: 'rgba(255, 0, 0, 0.2)',
                    pointBackgroundColor: 'red'
                },
                {
                    label: 'Meta Item',
                    data: metaStats,
                    borderColor: 'white',
                    backgroundColor: 'rgba(255, 255, 255, 0.2)',
                    pointBackgroundColor: 'white'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    angleLines: { color: '#888' },
                    grid: { color: '#555' },
                    pointLabels: {
                        color: '#fff',
                        font: { size: 14 }
                    },
                    ticks: {
                        backdropColor: 'transparent',
                        color: 'white',
                        stepSize: 20,
                        beginAtZero: true
                    }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        color: 'white',
                        font: { size: 14 }
                    }
                }
            }
        }
    });
}
// เรียกตอนโหลดหน้าเว็บ เพื่อวาดกราฟเบื้องต้น
document.addEventListener('DOMContentLoaded', function() {
  updateCompareChart(
      [80, 65, 70, 85, 60],  // ข้อมูลฝั่ง Result Item (ตัวอย่าง)
      [90, 70, 75, 80, 65]   // ข้อมูลฝั่ง Meta Item (ตัวอย่าง)
  );
});


