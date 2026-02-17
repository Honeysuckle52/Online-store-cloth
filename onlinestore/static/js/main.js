/* ============================================================
   CLOTH Store - main.js
   Single source of truth for all shared JS utilities
   ============================================================ */

// --- Notification system (single global implementation) ---
function showNotification(message, type = 'success') {
    // Remove any existing notification to avoid stacking
    const existing = document.querySelector('.cloth-notification');
    if (existing) existing.remove();

    const notification = document.createElement('div');
    notification.className = `cloth-notification alert alert-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        background: white;
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1rem 2rem;
        box-shadow: var(--shadow-md);
        z-index: 9999;
        animation: slideIn 0.3s ease;
        max-width: 360px;
    `;
    notification.textContent = message;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// --- Wishlist toggle (global, used from product cards & home) ---
function toggleWishlist(element, productId) {
    fetch(`/wishlist/toggle/${productId}/`, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const icon = element.querySelector('i');
            if (data.in_wishlist) {
                icon.classList.remove('bi-heart');
                icon.classList.add('bi-heart-fill');
                element.style.color = '#ff4d4d';
                showNotification('Товар добавлен в избранное', 'success');
            } else {
                icon.classList.remove('bi-heart-fill');
                icon.classList.add('bi-heart');
                element.style.color = 'var(--text-secondary)';
                showNotification('Товар удален из избранного', 'info');
            }
        }
    })
    .catch(() => {
        showNotification('Ошибка соединения', 'error');
    });
}

// --- Quick add to cart (global, used from product cards) ---
function quickAddToCart(variantId) {
    if (!variantId) {
        showNotification('Товар временно недоступен', 'warning');
        return;
    }

    // Get CSRF token from cookie
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value
        || getCookie('csrftoken');

    fetch(`/cart/add/${variantId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const cartCounter = document.getElementById('cart-counter');
            if (cartCounter) {
                cartCounter.textContent = data.cart_items;
            }
            showNotification(data.message, 'success');
        }
    })
    .catch(() => {
        showNotification('Ошибка добавления в корзину', 'error');
    });
}

// --- Helper: get cookie by name ---
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// --- DOMContentLoaded: single listener ---
document.addEventListener('DOMContentLoaded', function () {
    // 1. Animate product cards on scroll
    const cards = document.querySelectorAll('.product-card');
    if (cards.length > 0) {
        const observer = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = 1;
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, { threshold: 0.1 });

        cards.forEach(card => {
            card.style.opacity = 0;
            card.style.transform = 'translateY(40px)';
            card.style.transition = 'all 0.8s ease';
            observer.observe(card);
        });
    }

    // 2. AJAX add-to-cart forms
    const addToCartForms = document.querySelectorAll('.add-to-cart-form');
    addToCartForms.forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    body: formData,
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                });
                const data = await response.json();
                if (data.success) {
                    const cartCounter = document.getElementById('cart-counter');
                    if (cartCounter) {
                        cartCounter.textContent = data.cart_items;
                    }
                    showNotification(data.message, 'success');
                }
            } catch {
                showNotification('Ошибка добавления в корзину', 'error');
            }
        });
    });

    // 3. Auto-hide alert messages after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => {
                if (alert.parentElement) {
                    alert.remove();
                }
            }, 300);
        }, 5000);
    });

    // 4. Mobile catalog filter toggle
    const filterSidebar = document.querySelector('.filters-sidebar');
    const filterToggle = document.querySelector('.mobile-filter-toggle');

    if (filterToggle && filterSidebar) {
        filterToggle.addEventListener('click', function () {
            filterSidebar.classList.toggle('active');
            document.body.style.overflow = filterSidebar.classList.contains('active') ? 'hidden' : '';
        });

        filterSidebar.addEventListener('click', function (e) {
            if (e.target === filterSidebar) {
                filterSidebar.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    }

    // 5. Collapsible filter sections
    const filterTitles = document.querySelectorAll('.filter-title');
    filterTitles.forEach(title => {
        title.addEventListener('click', function () {
            this.classList.toggle('active');
            const content = this.nextElementSibling;
            if (content && content.classList.contains('filter-content')) {
                content.classList.toggle('collapsed');
            }
        });
    });

    // 6. Inject slide animation keyframes once
    if (!document.getElementById('cloth-animations')) {
        const style = document.createElement('style');
        style.id = 'cloth-animations';
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to   { transform: translateX(0);    opacity: 1; }
            }
            @keyframes slideOut {
                from { transform: translateX(0);    opacity: 1; }
                to   { transform: translateX(100%); opacity: 0; }
            }
            @keyframes fadeOut {
                from { opacity: 1; }
                to   { opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
});
