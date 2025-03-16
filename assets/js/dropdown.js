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
  
  document.addEventListener('click', function(e) {
    if (!e.target.closest('.Hero-Dropdown')) {
      dropdownMenu.classList.add('hidden');
    }
  });