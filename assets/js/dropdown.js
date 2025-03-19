const dropdownMenu = document.getElementById("Hero-Dropdown-Menu");
const selectedText = document.getElementById("selected-text");

function toggleDropdown() {
  dropdownMenu.classList.toggle("hidden");
  document.getElementById("hero-search-box").value = "";
  HerofilterOption();
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
  const firstLane = heroElement.dataset.heroFirstLane;
  const secondLane = heroElement.dataset.heroSecondLane;

  document.getElementById("selected-text").innerText = heroName;
  document.getElementById("Hero-Dropdown-Menu").classList.add("hidden");

  // Determine if the hero is Support, Jungle, or Farm
  const isSupport = firstClass === "Support" || secondClass === "Support";
  const isJungle = firstLane === "Jungle" || secondLane === "Jungle";
  const isFarm = firstLane === "Farm" || secondLane === "Farm"; // Farm lane condition

  // Get the sections
  const supportSection = document.getElementById("SupportItemSection");
  const jungleSection = document.getElementById("JungleItemSection");
  const farmSection = document.getElementById("FarmItemSection"); // Farm section

  // Show the corresponding sections based on the hero's class and lane
  if (isSupport) {
    supportSection.classList.remove("hidden");
    jungleSection.classList.add("hidden");
    farmSection.classList.add("hidden");
  } else if (isJungle) {
    jungleSection.classList.remove("hidden");
    supportSection.classList.add("hidden");
    farmSection.classList.add("hidden");
  } else if (isFarm) {
    farmSection.classList.remove("hidden"); // Show Farm section when hero is in Farm lane
    supportSection.classList.add("hidden");
    jungleSection.classList.add("hidden");
  } else {
    supportSection.classList.add("hidden");
    jungleSection.classList.add("hidden");
    farmSection.classList.add("hidden");
  }

  // Adjust Force/Ban items
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

function filterByClass(className) {
  const allOptions = document.querySelectorAll('.Hero-Option');
  document.getElementById('hero-search-box').value = '';
  allOptions.forEach(option => {
    const heroClass = option.getAttribute('data-hero-class');
    const secondClass = option.getAttribute('data-hero-second-class');
    option.style.display = (heroClass === className || secondClass === className) ? 'flex' : 'none';
  });
  document.getElementById('Hero-Dropdown-Menu').classList.remove('hidden');

  if (className === "Jungle") {
    document.getElementById("JungleItemSection").classList.remove("hidden");
    document.getElementById("FarmItemSection").classList.add("hidden");
    document.getElementById("SupportItemSection").classList.add("hidden");
  } else if (className === "Farm") {
    document.getElementById("FarmItemSection").classList.remove("hidden");
    document.getElementById("JungleItemSection").classList.add("hidden");
    document.getElementById("SupportItemSection").classList.add("hidden");
  } else {
    document.getElementById("FarmItemSection").classList.add("hidden");
    document.getElementById("JungleItemSection").classList.add("hidden");
    document.getElementById("SupportItemSection").classList.add("hidden");
  }
}

function toggleClassDropdown() {
  document.getElementById('Class-Dropdown-Menu').classList.toggle('hidden');
}

function selectClass(className) {
  document.getElementById('selected-class-text').textContent = className;
  document.getElementById('Class-Dropdown-Menu').classList.add('hidden');
}

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

document.addEventListener("DOMContentLoaded", function () {
  const supportItems = document.querySelectorAll(".support-item");
  supportItems.forEach((item) => {
    item.addEventListener("click", function () {
      supportItems.forEach((i) => i.classList.remove("selected"));
      item.classList.add("selected");
      const selectedItemName = item.dataset.itemName;
      console.log("Selected Support Item:", selectedItemName);
    });
  });

  const farmItems = document.querySelectorAll(".farm-item");
  farmItems.forEach((item) => {
    item.addEventListener("click", function () {
      farmItems.forEach((i) => i.classList.remove("selected"));
      item.classList.add("selected");
      const selectedItemName = item.dataset.itemName;
      console.log("Selected Farm Item:", selectedItemName);
    });
  });
});

document.addEventListener('click', function (e) {
  if (!e.target.closest('.Hero-Dropdown')) {
    dropdownMenu.classList.add('hidden');
  }
});

// Function to update the Game Phase
function updateGamePhase() {
  const selectedPhase = document.getElementById('game-phase').value;
  console.log('Selected Game Phase:', selectedPhase);

  // Example: When Early Game is selected, show items for early game
  if (selectedPhase === 'early') {
    displayMetaItems();
  } else if (selectedPhase === 'mid') {
    displayMetaItems();
  } else if (selectedPhase === 'late') {
    displayMetaItems();
  }
}

// Function to display meta items when a game phase is selected
function displayMetaItems() {
  const metaItemsContainer = document.getElementById('meta-items');
  // Example: Add more logic here to dynamically populate meta items based on game phase
  metaItemsContainer.style.display = 'flex';
}

// Example of handling Meta Item button click
document.querySelectorAll('.Meta-Item-Container button').forEach(button => {
  button.addEventListener('click', function () {
    alert('You selected ' + button.innerText);
  });
});
