// dropdown.js

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
  document.getElementById("selected-text").innerText = heroName;
  document.getElementById("Hero-Dropdown-Menu").classList.add("hidden");

  const isSupport = firstClass === "Support" || secondClass === "Support";
  const supportSection = document.getElementById("SupportItemSection");
  if (isSupport) {
    supportSection.classList.remove("hidden");
  } else {
    supportSection.classList.add("hidden");
  }

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
});

document.addEventListener('click', function (e) {
  if (!e.target.closest('.Hero-Dropdown')) {
    dropdownMenu.classList.add('hidden');
  }
});
