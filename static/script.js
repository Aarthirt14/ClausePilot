// ============================================
// ClausePilot - Global JavaScript
// ============================================

// Sidebar Toggle for Mobile
const sidebarToggle = document.getElementById('sidebarToggle');
const sidebarClose = document.getElementById('sidebarClose');
const sidebar = document.getElementById('sidebar');

if (sidebarToggle) {
  sidebarToggle.addEventListener('click', () => {
    sidebar.classList.add('show');
  });
}

if (sidebarClose) {
  sidebarClose.addEventListener('click', () => {
    sidebar.classList.remove('show');
  });
}

// Close sidebar when clicking outside on mobile
document.addEventListener('click', (e) => {
  if (window.innerWidth < 992) {
    if (sidebar && sidebar.classList.contains('show')) {
      if (!sidebar.contains(e.target) && e.target !== sidebarToggle) {
        sidebar.classList.remove('show');
      }
    }
  }
});

// Theme Toggle (Dark Mode)
const themeToggle = document.getElementById('themeToggle');
const htmlElement = document.documentElement;

// Check for saved theme preference or default to 'light'
const currentTheme = localStorage.getItem('theme') || 'light';
htmlElement.setAttribute('data-bs-theme', currentTheme);

// Update button text
if (themeToggle) {
  updateThemeButton(currentTheme);
}

if (themeToggle) {
  themeToggle.addEventListener('click', () => {
    const theme = htmlElement.getAttribute('data-bs-theme') === 'dark' ? 'light' : 'dark';
    htmlElement.setAttribute('data-bs-theme', theme);
    localStorage.setItem('theme', theme);
    updateThemeButton(theme);
  });
}

function updateThemeButton(theme) {
  if (!themeToggle) return;
  
  if (theme === 'dark') {
    themeToggle.innerHTML = '<i class="bi bi-sun"></i><span>Light Mode</span>';
  } else {
    themeToggle.innerHTML = '<i class="bi bi-moon-stars"></i><span>Dark Mode</span>';
  }
}

// Initialize Bootstrap tooltips globally
document.addEventListener('DOMContentLoaded', () => {
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }
  });
});
