let currentSlot = null;
let currentType = null;
let selectedForceItems = [null, null, null];
let selectedBanItems = [null, null, null];
let selectedMetaItems = [null, null, null, null, null, null];
let selectedSupportItemId = null;
let selectedFarmItemId = null;
let selectedHeroOptionElement = null;

function toggleDropdown() {
  document.getElementById('Hero-Dropdown-Menu').classList.toggle('hidden');
  // Clear search and refilter when opening/closing
  const heroSearchBox = document.getElementById("hero-search-box");
  if (heroSearchBox) {
    heroSearchBox.value = "";
    HerofilterOption();
  }
}

function HerofilterOption() {
  const heroSearchBox = document.getElementById('hero-search-box');
  if (!heroSearchBox) return;
  const input = heroSearchBox.value.toLowerCase();
  const options = document.querySelectorAll('#Hero-Dropdown-Menu .Hero-Option');
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

  if (selectedHeroOptionElement) {
    selectedHeroOptionElement.classList.remove('selected');
  }
  heroElement.classList.add('selected');
  selectedHeroOptionElement = heroElement;

  // Show/hide support section
  const isSupport = firstClass === "Support" || secondClass === "Support";
  const supportItemSection = document.getElementById("SupportItemSection");
  if (supportItemSection) {
    if (isSupport) {
      supportItemSection.classList.remove("hidden");
    } else {
      supportItemSection.classList.add("hidden");
      selectedSupportItemId = null;
      const disp = document.getElementById('selected-support-item');
      if (disp) disp.innerHTML = `-- Select Support Item --`;
      const hid = document.getElementById('selectedSupportItemId');
      if (hid) hid.value = '';
    }
  }

  // Show/hide 3rd force/ban buttons
  const forceBtn2 = document.getElementById("force-btn-2");
  const banBtn2 = document.getElementById("ban-btn-2");
  const forceMaxText = document.getElementById("Force-MaxItem");
  const banMaxText = document.getElementById("BAN-BANItem");

  if (isSupport) {
    forceBtn2.style.display = "none";
    banBtn2.style.display = "none";
    forceMaxText.innerText = "(Max 2 item)";
    banMaxText.innerText = "(Max 2 item)";
    if (selectedForceItems[2] !== null) {
      selectedForceItems[2] = null;
      forceBtn2.innerHTML = `<span class="plus-icon">+</span>`;
      delete forceBtn2.dataset.itemId;
    }
    if (selectedBanItems[2] !== null) {
      selectedBanItems[2] = null;
      banBtn2.innerHTML = `<span class="plus-icon">+</span>`;
      delete banBtn2.dataset.itemId;
    }
  } else {
    forceBtn2.style.display = "inline-block";
    banBtn2.style.display = "inline-block";
    forceMaxText.innerText = "(Max 3 item)";
    banMaxText.innerText = "(Max 3 item)";
  }

  // Reset class/lane toggles
  document.getElementById("selected-class-text").innerText = "Select Class";
  document.getElementById("selected-lane-text").innerText = "Select Lane";

  const classMenu = document.getElementById("Class-Dropdown-Menu");
  if (classMenu) {
    classMenu.innerHTML = "";
    if (firstClass) {
      const opt1 = document.createElement("div");
      opt1.className = "Dropdown-Option";
      opt1.textContent = firstClass;
      opt1.onclick = () => selectClass(firstClass);
      classMenu.appendChild(opt1);
    }
    if (secondClass && secondClass !== firstClass) {
      const opt2 = document.createElement("div");
      opt2.className = "Dropdown-Option";
      opt2.textContent = secondClass;
      opt2.onclick = () => selectClass(secondClass);
      classMenu.appendChild(opt2);
    }
  }

  const laneMenu = document.getElementById("Lane-Dropdown-Menu");
  if (laneMenu) {
    laneMenu.innerHTML = "";
    if (firstLane) {
      const opt1 = document.createElement("div");
      opt1.className = "Dropdown-Option";
      opt1.textContent = firstLane;
      opt1.onclick = () => selectLane(firstLane);
      laneMenu.appendChild(opt1);
    }
    if (secondLane && secondLane !== firstLane) {
      const opt2 = document.createElement("div");
      opt2.className = "Dropdown-Option";
      opt2.textContent = secondLane;
      opt2.onclick = () => selectLane(secondLane);
      laneMenu.appendChild(opt2);
    }
  }

  const farmItemSection = document.getElementById("FarmItemSection");
  if (farmItemSection) farmItemSection.classList.add("hidden");
  selectedFarmItemId = null;
  const farmDisp = document.getElementById('selected-farm-item');
  if (farmDisp) farmDisp.innerHTML = `-- Select Farm Item --`;
  document.getElementById('selectedFarmItemId').value = '';
}

function filterByClass(className) {
  // decode URL-encoded class (to match data-hero-class)
  className = decodeURIComponent(className);
  const allOptions = document.querySelectorAll('.Hero-Option');
  const searchBox = document.getElementById('hero-search-box');
  if (searchBox) searchBox.value = '';

  allOptions.forEach(option => {
    const c1 = option.getAttribute('data-hero-class');
    const c2 = option.getAttribute('data-hero-second-class');
    option.style.display = (c1 === className || c2 === className) ? 'flex' : 'none';
  });
  document.getElementById('Hero-Dropdown-Menu').classList.remove('hidden');
}

function toggleClassDropdown() {
  document.getElementById('Class-Dropdown-Menu').classList.toggle('hidden');
}
function selectClass(className) {
  document.getElementById('selected-class-text').textContent = className;
  document.getElementById('Class-Dropdown-Menu').classList.add('hidden');
  const supportItemSection = document.getElementById("SupportItemSection");
  if (supportItemSection) {
    if (className === "Support") {
      supportItemSection.classList.remove("hidden");
    } else {
      supportItemSection.classList.add("hidden");
      selectedSupportItemId = null;
      const disp = document.getElementById('selected-support-item');
      if (disp) disp.innerHTML = `-- Select Support Item --`;
      const hid = document.getElementById('selectedSupportItemId');
      if (hid) hid.value = '';
    }
  }
  const f2 = document.getElementById("force-btn-2");
  const b2 = document.getElementById("ban-btn-2");
  const fx = document.getElementById("Force-MaxItem");
  const bx = document.getElementById("BAN-BANItem");
  if (className === "Support") {
    f2.style.display = "none";
    b2.style.display = "none";
    fx.innerText = "(Max 2 item)";
    bx.innerText = "(Max 2 item)";
    if (selectedForceItems[2] !== null) {
      selectedForceItems[2] = null;
      f2.innerHTML = `<span class="plus-icon">+</span>`;
      delete f2.dataset.itemId;
    }
    if (selectedBanItems[2] !== null) {
      selectedBanItems[2] = null;
      b2.innerHTML = `<span class="plus-icon">+</span>`;
      delete b2.dataset.itemId;
    }
  } else {
    f2.style.display = "inline-block";
    b2.style.display = "inline-block";
    fx.innerText = "(Max 3 item)";
    bx.innerText = "(Max 3 item)";
  }
}

function toggleLaneDropdown() {
  document.getElementById('Lane-Dropdown-Menu').classList.toggle('hidden');
}
function selectLane(laneName) {
  document.getElementById('selected-lane-text').textContent = laneName;
  document.getElementById('Lane-Dropdown-Menu').classList.add('hidden');
  const farmItemSection = document.getElementById("FarmItemSection");
  if (farmItemSection) {
    if (laneName === "Farm") {
      farmItemSection.classList.remove("hidden");
    } else {
      farmItemSection.classList.add("hidden");
      selectedFarmItemId = null;
      const disp = document.getElementById('selected-farm-item');
      if (disp) disp.innerHTML = `-- Select Farm Item --`;
      const hid = document.getElementById('selectedFarmItemId');
      if (hid) hid.value = '';
    }
  }
}

function toggleSupportDropdown() {
  document.getElementById("Support-Dropdown-Menu").classList.toggle("hidden");
}
function toggleFarmDropdown() {
  document.getElementById("Farm-Dropdown-Menu").classList.toggle("hidden");
}

function selectSupportItemJS(itemId, itemName, itemPath) {
  const disp = document.getElementById('selected-support-item');
  if (disp) {
    disp.innerHTML = `<img src="${itemPath}" class="dropdown-img" alt="${itemName}" style="height:20px;margin-right:5px;vertical-align:middle;"> ${itemName}`;
  }
  const hid = document.getElementById('selectedSupportItemId');
  if (hid) hid.value = itemId;
  selectedSupportItemId = itemId;
  toggleSupportDropdown();
}

function selectFarmItemJS(element) {
  const itemId = element.dataset.itemId;
  const itemName = element.dataset.itemName;
  const itemPath = element.dataset.itemPath;
  const disp = document.getElementById('selected-farm-item');
  if (disp) {
    disp.innerHTML = `<img src="${itemPath}" class="dropdown-img" alt="${itemName}" style="height:20px;margin-right:5px;vertical-align:middle;"> ${itemName}`;
  }
  const hid = document.getElementById('selectedFarmItemId');
  if (hid) hid.value = itemId;
  selectedFarmItemId = itemId;
  toggleFarmDropdown();
}

function forceBanButtonClick(event, type, slotIndex) {
  const btn = event.currentTarget;
  currentSlot = slotIndex;
  currentType = type;

  if (btn.dataset.itemId) {
    // ถ้ามีการเลือกแล้ว ให้รีเซ็ตปุ่มกลับเป็น "+"
    btn.innerHTML = `<span class="plus-icon">+</span>`;
    btn.classList.remove('selected');
    delete btn.dataset.itemId;
    if (type === 'force')      selectedForceItems[slotIndex] = null;
    else if (type === 'ban')   selectedBanItems[slotIndex]  = null;
    else if (type === 'meta')  selectedMetaItems[slotIndex] = null;
  } else {
    // เปิด popup ทั้งสองกรณี (force/ban หรือ meta)
    if (type === 'meta') {
      const mBox = document.getElementById('meta-search-box');
      mBox && (mBox.value = "");
      const pop = document.getElementById('meta-item-popup');
      pop.classList.remove('hidden');
      pop.classList.add('show');
    } else {
      const iBox = document.getElementById('item-search-box');
      iBox && (iBox.value = "");
      const pop = document.getElementById('item-popup');
      pop.classList.remove('hidden');
      pop.classList.add('show');
    }
  }
}

function closeItemPopup(popupType) {
  const pop = (popupType === 'meta')
    ? document.getElementById('meta-item-popup')
    : document.getElementById('item-popup');

  pop.classList.add('hidden');
  pop.classList.remove('show');

  currentType = null;
  currentSlot = null;
}

function selectPopupItem(itemId, itemName, itemPath) {
  if (currentType === null || currentSlot === null) return;
  const buttonId = `${currentType}-btn-${currentSlot}`;
  const button = document.getElementById(buttonId);
  if (button) {
    button.innerHTML = `<img src="${itemPath}" alt="${itemName}" style="width:100%;height:100%;object-fit:contain;">`;
    button.dataset.itemId = itemId;
    if (currentType === 'force') {
      selectedForceItems[currentSlot] = itemId;
    } else if (currentType === 'ban') {
      selectedBanItems[currentSlot] = itemId;
    } else if (currentType === 'meta') {
      selectedMetaItems[currentSlot] = itemId;
      button.classList.add('selected');
    }
  }
  closeItemPopup(currentType === 'meta' ? 'meta' : undefined);
}


function filterItemList(searchBoxId, itemListId) {
    const searchInput = document.getElementById(searchBoxId);
    if (!searchInput) return;
    const searchValue = searchInput.value.toLowerCase();
    const items = document.querySelectorAll(`#${itemListId} .item-container`);
    items.forEach(item => {
        const name = item.dataset.itemName.toLowerCase();
        item.style.display = name.includes(searchValue) ? 'inline-block' : 'none';
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const calculateBtn = document.getElementById('calculate-btn');
    if (calculateBtn) {
        calculateBtn.addEventListener('click', async () => {
            const heroName = document.getElementById('selected-text').textContent;
            let heroClass = document.getElementById('selected-class-text').textContent;
            let lane = document.getElementById('selected-lane-text').textContent;
            
            if (!heroName || heroName === 'Select' || heroName === 'Select Hero') {
                alert('Please select a hero.');
                return;
            }
            if (!heroClass || heroClass === 'Select Class') {
                if (selectedHeroOptionElement && selectedHeroOptionElement.dataset.heroClass) {
                    heroClass = selectedHeroOptionElement.dataset.heroClass;
                } else {
                    alert('Please select a hero class.');
                    return;
                }
            }
            if (!lane || lane === 'Select Lane') {
                if (selectedHeroOptionElement && selectedHeroOptionElement.dataset.heroLane) {
                    lane = selectedHeroOptionElement.dataset.heroLane;
                } else if (selectedHeroOptionElement && selectedHeroOptionElement.dataset.heroSecondLane) {
                    lane = selectedHeroOptionElement.dataset.heroSecondLane;
                } else {
                    alert('Please select a lane.');
                    return;
                }
            }
            
            const forceIds = selectedForceItems.filter(id => id !== null);
            const banIds = selectedBanItems.filter(id => id !== null);
            
            if (selectedFarmItemId && !forceIds.includes(selectedFarmItemId)) {
                forceIds.push(selectedFarmItemId);
            }
            if (selectedSupportItemId && !forceIds.includes(selectedSupportItemId)) {
                forceIds.push(selectedSupportItemId);
            }
            
            const payload = {
                hero: heroName,
                lane: lane,
                heroClass: heroClass,
                force: forceIds,
                ban: banIds
            };
            console.log("Sending payload:", payload);
            
            try {
                const response = await fetch('http://localhost:5000/ga', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
                }
                const result = await response.json();
                console.log("Received result:", result);
                displayResults(result);
            } catch (error) {
                console.error('Error calling API:', error);
                alert(`Error: ${error.message}`);
            }
        });
    }
    
    // Initial chart draw and filter button styling
    updateCompareChart([0,0,0,0,0,0,0], [0,0,0,0,0,0,0]);
    const filterButtons = document.querySelectorAll('.Filter-Button button');
    filterButtons.forEach(button => {
        button.addEventListener('click', function () {
            filterButtons.forEach(b => b.classList.remove('selected'));
            this.classList.add('selected');
        });
    });
    
    // Compare button updates both image boxes and radar chart
    const phaseSelect = document.getElementById('game-phase');
    phaseSelect.addEventListener('change', () => updateCompareSection(phaseSelect.value));
    const compareBtn = document.getElementById('compare-btn');
    if (compareBtn && phaseSelect) {
        compareBtn.addEventListener('click', async () => {
            const phase = phaseSelect.value;
            if (!phase) {
                alert('Please select a game phase first.');
                return;
      }
      // อัพเดตกล่องภาพไอเทมฝั่งซ้าย
      updateCompareSection(phase);

      // ดึงค่า stats แล้วอัพเดตกราฟ
      const hero = document.getElementById('selected-text').textContent;
      const resultItems = getResultItems(phase);
      const metaItems = selectedMetaItems.filter(id => id !== null);
      try {
        const [stats1, stats2] = await Promise.all([
          calculateStats(resultItems, hero, phase),
          calculateMetaStats(metaItems, hero, phase)
        ]);
        updateCompareChart(stats1, stats2);
      } catch (e) {
        console.error(e);
        alert('Error updating chart');
      }
    });
  }
});

function displayResults(data) {
  const phases = ['Early','Mid','Late'];
  phases.forEach(phase => {
    const phaseData = data[phase];
    const container = document.querySelector(`.${phase}-Game .${phase}-Image-Container`);
    if (container) {
      container.innerHTML = '';
      for (let i=0; i<6; i++){
        const img = document.createElement('img');
        if (phaseData.items[i]) {
          const item = phaseData.items[i];
          img.src = item.img;
          img.alt = item.name;
          img.title = item.name;
          img.dataset.itemId = item.id;
        }
        container.appendChild(img);
      }
    }
  });
}

function getResultItems(phase) {
  const map = {'early':'Early','mid':'Mid','late':'Late'};
  const container = document.querySelector(`.${map[phase]}-Game .${map[phase]}-Image-Container`);
  if (!container) return [];
  return Array.from(container.querySelectorAll('img'))
    .map(img => img.dataset.itemId)
    .filter(id => id);
}

async function calculateStats(items, hero, phase) {
  const response = await fetch('http://localhost:5000/calculate_stats', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({hero, phase, items})
  });
  if (!response.ok) throw new Error('Failed to calculate stats');
  return (await response.json()).stats;
}

async function calculateMetaStats(metaItems, hero, phase) {
  const response = await fetch('http://localhost:5000/calculate_stats', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({hero, phase, items:metaItems})
  });
  if (!response.ok) throw new Error('Failed to calculate meta stats');
  return (await response.json()).stats;
}

let compareChart = null;
function updateCompareChart(resultStats, metaStats) {
  const labels = ['Phys_ATK','Magic_Power','Phys_Defense','HP','Cooldown_Reduction','Critical_Rate','Movement_Speed'];
  const resultData = labels.map(l => resultStats[l]||0);
  const metaData = labels.map(l => metaStats[l]||0);
  const ctx = document.getElementById('CompareChartCanvas').getContext('2d');
  if (compareChart) compareChart.destroy();
  compareChart = new Chart(ctx, {
    type:'radar',
    data:{labels,datasets:[
      {label:'Result Item',data:resultData,borderColor:'red',backgroundColor:'rgba(255,0,0,0.2)',pointBackgroundColor:'red'},
      {label:'Meta Item',data:metaData,borderColor:'white',backgroundColor:'rgba(255,255,255,0.2)',pointBackgroundColor:'white'}
    ]},
    options:{
      responsive:true,
      maintainAspectRatio:false,
      scales:{r:{angleLines:{color:'#888'},grid:{color:'#555'},pointLabels:{color:'#fff',font:{size:14}},ticks:{backdropColor:'transparent',color:'white',beginAtZero:true}}},
      plugins:{legend:{labels:{color:'white',font:{size:14}}}}
    }
  });
}

function updateCompareSection(phase) {
  const boxes = document.querySelectorAll('.Select-Game-Phase-Container .input-box .input-item');
  if (!phase) {
    boxes.forEach(b=>b.innerHTML='');
    return;
  }
  const cap = phase.charAt(0).toUpperCase() + phase.slice(1);
  const imgs = document.querySelectorAll(`.${cap}-Game .${cap}-Image-Container img`);
  boxes.forEach((box,i)=>{
    box.innerHTML = '';
    if (imgs[i]) {
      const img = document.createElement('img');
      img.src = imgs[i].src;
      img.alt = imgs[i].alt;
      img.style.maxWidth = '100%';
      img.style.maxHeight = '100%';
      box.appendChild(img);
    }
  });
}
