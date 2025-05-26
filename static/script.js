document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput');
    if (!searchInput) return;

    let timeout = null;
    searchInput.addEventListener('input', () => {
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            // Просто отправляем форму фильтрации
            const form = document.getElementById('filterForm');
            if(form) form.submit();
        }, 300);
    });
});
