document.addEventListener("DOMContentLoaded", () => {
    // Анимация появления карточек товаров
    const cards = document.querySelectorAll(".product-card");

    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if(entry.isIntersecting){
                entry.target.style.opacity = 1;
                entry.target.style.transform = "translateY(0)";
            }
        });
    }, { threshold: 0.1 });

    cards.forEach(card => {
        card.style.opacity = 0;
        card.style.transform = "translateY(40px)";
        card.style.transition = "all 0.8s ease";
        observer.observe(card);
    });

    // Обработка добавления в корзину через AJAX
    const addToCartForms = document.querySelectorAll('.add-to-cart-form');
    addToCartForms.forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = new FormData(form);
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();

            if (data.success) {
                // Обновляем счетчик корзины
                const cartCounter = document.getElementById('cart-counter');
                if (cartCounter) {
                    cartCounter.textContent = data.cart_items;
                }

                // Показываем уведомление
                showNotification(data.message, 'success');
            }
        });
    });

    // Обработка добавления в избранное через AJAX
    const wishlistButtons = document.querySelectorAll('.wishlist-btn');
    wishlistButtons.forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();

            const url = btn.href;
            const response = await fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();

            if (data.success) {
                btn.classList.toggle('active', data.in_wishlist);
                showNotification(data.message, 'success');
            }
        });
    });

    // Функция показа уведомлений
    function showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            background: white;
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1rem;
            box-shadow: var(--shadow-md);
            z-index: 9999;
            animation: slideIn 0.3s ease;
        `;
        notification.textContent = message;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    // Добавляем стили для анимации
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
});
// Автоматическое скрытие сообщений через 5 секунд
document.addEventListener('DOMContentLoaded', function() {
    const messages = document.querySelectorAll('.alert');
    messages.forEach(message => {
        setTimeout(() => {
            message.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => {
                if (message.parentElement) {
                    message.remove();
                }
            }, 300);
        }, 5000);
    });
});

// Функция для показа уведомлений
function showNotification(message, type = 'success') {
    const container = document.querySelector('.messages-container');
    if (!container) {
        const newContainer = document.createElement('div');
        newContainer.className = 'messages-container';
        document.body.appendChild(newContainer);
    }

    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.innerHTML = `
        ${message}
        <button class="btn-close" onclick="this.parentElement.remove()">×</button>
    `;

    document.querySelector('.messages-container').appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}