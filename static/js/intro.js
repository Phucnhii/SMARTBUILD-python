  // Darkmode
  const darkModeBtnDesktop = document.getElementById('darkModeButton-desktop');
  const darkModeBtnMobile = document.getElementById('darkModeButton');

  function setDarkMode(enabled) {
    if (enabled) {
      document.body.classList.add('dark-mode');
      localStorage.setItem('theme', 'dark');
      darkModeBtnDesktop.textContent = '🌝';
      darkModeBtnMobile.textContent = '🌝';
    } else {
      document.body.classList.remove('dark-mode');
      localStorage.setItem('theme', 'light');
      darkModeBtnDesktop.textContent = '🌚';
      darkModeBtnMobile.textContent = '🌚';
    }
  }

  function toggleDarkMode() {
    const isDark = document.body.classList.contains('dark-mode');
    setDarkMode(!isDark);
  }

  darkModeBtnDesktop.addEventListener('click', toggleDarkMode);
  darkModeBtnMobile.addEventListener('click', toggleDarkMode);

  window.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme') || 'light';
    setDarkMode(savedTheme === 'dark');
  });

// Swiper
const swiper = new Swiper(".team-swiper", {
  slidesPerView: 1, // mỗi slide chiếm 100%
  spaceBetween: 20,
  loop: true,

  navigation: {
    nextEl: ".swiper-button-next",
    prevEl: ".swiper-button-prev",
  },

  pagination: {
    el: ".swiper-pagination",
    clickable: true,
  },
});