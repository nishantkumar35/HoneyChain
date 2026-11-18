/**
 * HoneyChain — UI Interactions & Micro-Animations
 */

document.addEventListener('DOMContentLoaded', () => {

  // --- Mobile Navigation Drawer Toggle ---
  const mobileBtn = document.getElementById('mobile-menu-btn');
  const mobileMenu = document.getElementById('mobile-menu');

  if (mobileBtn && mobileMenu) {
    mobileBtn.addEventListener('click', () => {
      mobileMenu.classList.toggle('hidden');
    });
  }

  // --- Auto-Dismiss Flash Messages with Smooth Fade ---
  const messagesContainer = document.getElementById('messages-container');
  if (messagesContainer) {
    setTimeout(() => {
      messagesContainer.style.transition = 'opacity 0.6s cubic-bezier(0.16, 1, 0.3, 1), transform 0.6s ease';
      messagesContainer.style.opacity = '0';
      messagesContainer.style.transform = 'translateY(-10px)';
      setTimeout(() => messagesContainer.remove(), 600);
    }, 4500);
  }

  // --- Batch Search Input Auto-Capitalize ---
  const batchSearchInput = document.querySelector('input[name="batch_id"]');
  if (batchSearchInput) {
    batchSearchInput.addEventListener('input', (e) => {
      const start = e.target.selectionStart;
      const end = e.target.selectionEnd;
      e.target.value = e.target.value.toUpperCase();
      e.target.setSelectionRange(start, end);
    });
  }

  // --- Card Tilt / Hover Micro-Interactions on Interactive Cards ---
  const interactiveCards = document.querySelectorAll('.card-shadow-hover');
  interactiveCards.forEach(card => {
    card.addEventListener('mouseenter', () => {
      card.style.transition = 'transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.25s ease';
    });
  });

});
