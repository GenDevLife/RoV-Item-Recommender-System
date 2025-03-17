const optionsList = document.getElementById("HeroOptionList");
const dropdownMenu = document.getElementById("Hero-Dropdown-Menu");
const selectedText = document.getElementById("selected-text");

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

  document.getElementById("selected-text").innerText = heroName;
  document.getElementById("Hero-Dropdown-Menu").classList.add("hidden");

  const isSupport = firstClass === "Support" || secondClass === "Support";

  // ✅ แสดง/ซ่อนส่วน Support Item
  const supportSection = document.getElementById("SupportItemSection");
  if (isSupport) {
    supportSection.classList.remove("hidden");
  } else {
    supportSection.classList.add("hidden");
  }

  // ✅ ซ่อน/แสดงปุ่ม Force/BAN ที่ 3
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
  const supportItems = document.querySelectorAll(".support-item");

  supportItems.forEach((item) => {
    item.addEventListener("click", function () {
      // ลบ .selected จากทั้งหมดก่อน
      supportItems.forEach((i) => i.classList.remove("selected"));

      // เพิ่ม .selected ให้ไอเทมที่คลิก
      item.classList.add("selected");

      // ดึงชื่อไอเทมที่เลือก (ถ้าต้องการใช้ต่อ)
      const selectedItemName = item.dataset.itemName;
      console.log("Selected Support Item:", selectedItemName);
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
}

// LANE DROPDOWN
function toggleLaneDropdown() {
  document.getElementById('Lane-Dropdown-Menu').classList.toggle('hidden');
}
function selectLane(laneName) {
  document.getElementById('selected-lane-text').textContent = laneName;
  document.getElementById('Lane-Dropdown-Menu').classList.add('hidden');
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

  document.getElementById("selected-text").innerText = heroName;
  document.getElementById("Hero-Dropdown-Menu").classList.add("hidden");

  if (firstClass === "Support") {
    document.getElementById("SupportItemSection").classList.remove("hidden");
  } else {
    document.getElementById("SupportItemSection").classList.add("hidden");
  }
}
function selectSupportItem(name, imgPath) {
  const selected = document.getElementById("selected-support-item");
  selected.innerHTML = `<img src="${imgPath}" alt="${name}"><span>${name}</span>`;
  document.getElementById("Support-Dropdown-Menu").classList.add("hidden");
}
const rawList = [
  { filename: "Sonic_Boots.png", name: "Sonic Boots" },
  { filename: "War_Boots.png", name: "War Boots" },
  { filename: "Gilded_Greaves.png", name: "Gilded Greaves" },
  { filename: "Hermes'_Select.png", name: "Hermes' Select" },
  { filename: "Amulet_of_Longevity.png", name: "Amulet_of_Longevity" },
  { filename: "Ancient_Scriptures.png", name: "Ancient_Scriptures" },
  { filename: "Apocalypse.png", name: "Apocalypse" },
  { filename: "Arcane_Hammer.png", name: "Arcane_Hammer" },
  { filename: "Arctic_Orb.png", name: "Arctic_Orb" },
  { filename: "Astral_Spear.png", name: "Astral_Spear" },
  { filename: "Belt_of_Clarity.png", name: "Belt_of_Clarity" },
  { filename: "Berith's_Agony.png", name: "Berith's_Agony" },
  { filename: "Blitz_Blade.png", name: "Blitz_Blade" },
  { filename: "Bloodied_Club.png", name: "Bloodied_Club" },
  { filename: "Boomstick.png", name: "Boomstick" },
  { filename: "Boots_of_Speed.png", name: "Boots_of_Speed" },
  { filename: "Bow_of_Slaughter.png", name: "Bow_of_Slaughter" },
  { filename: "Chain_Hammer.png", name: "Chain_Hammer" },
  { filename: "Claves_Sancti.png", name: "Claves_Sancti" },
];

const baseImagePath = "image/item/";
const itemList = rawList.map(item => ({
  name: item.name,
  img: baseImagePath + item.filename
}));

let currentSlot = null;
let currentType = null;

function openPopup(type, slotIndex) {
  currentSlot = slotIndex;
  currentType = type;
  document.getElementById("item-search").value = "";
  renderItemList(itemList); // แสดงทั้งหมด
  document.getElementById("item-popup").classList.remove("hidden");
}

function closePopup() {
  document.getElementById("item-popup").classList.add("hidden");
}

function renderItemList(filteredList) {
  const container = document.getElementById("popup-item-list");
  container.innerHTML = "";

  filteredList.forEach(item => {
    const img = document.createElement("img");
    img.src = item.img;
    img.alt = item.name;
    img.title = item.name;
    img.onclick = () => {
      const target = document.getElementById(`${currentType}-btn-${currentSlot}`);
      target.innerHTML = `<img src="${item.img}" alt="${item.name}" style="width:100%; height:100%; object-fit:contain;">`;
      target.dataset.itemName = item.name;
    
      enableItemRemoveOnClick(); // ✅ เปิดให้ลบได้เมื่อคลิกซ้ำ
      // ❌ ไม่ปิด popup แล้ว
    };
    container.appendChild(img);
  });
}
// ✅ ลบไอเทมออกเมื่อคลิกบนปุ่ม Force/BAN ที่มีไอเทม
function enableItemRemoveOnClick() {
  const allForceButtons = document.querySelectorAll("[id^='force-btn-']");
  const allBanButtons = document.querySelectorAll("[id^='ban-btn-']");

  [...allForceButtons, ...allBanButtons].forEach((btn) => {
    btn.onclick = () => {
      if (btn.innerHTML.includes("<img")) {
        // ✅ แก้ตรงนี้ให้ใส่ข้อความ Click Here กลับเข้าไป
        btn.innerHTML = "Click Here";
        btn.removeAttribute("data-item-name");
      } else {
        const type = btn.id.includes("force") ? "force" : "ban";
        const index = parseInt(btn.id.split("-")[2]);
        openPopup(type, index);
      }
    };
  });
}
function filterItemList() {
  const searchValue = document.getElementById("item-search").value.toLowerCase();
  const filtered = itemList.filter(item => item.name.toLowerCase().includes(searchValue));
  renderItemList(filtered);
}
document.addEventListener('click', function (e) {
  if (!e.target.closest('.Hero-Dropdown')) {
    dropdownMenu.classList.add('hidden');
  }
});