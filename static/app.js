// Custom JS for Data Entry App
function showNotification(message, color = '#28a745') {
    const notif = document.getElementById('notification');
    notif.style.background = color;
    document.getElementById('notification-message').textContent = message;
    notif.style.display = 'block';
    notif.style.opacity = '1';
    setTimeout(() => {
        notif.style.opacity = '0';
        setTimeout(() => notif.style.display = 'none', 400);
    }, 2000);
}
function showLoading() {
    document.getElementById('loading').style.display = 'flex';
}
function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}
async function ajaxWithLoading(fn) {
    showLoading();
    try { await fn(); } finally { hideLoading(); }
}
document.getElementById('itemForm').addEventListener('submit', function(e) {
    e.preventDefault();
    ajaxWithLoading(async () => {
        const form = e.target;
        const formData = new FormData(form);
        const response = await fetch('/', {
            method: 'POST',
            body: formData
        });
        if (response.ok) {
            const html = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const newRows = doc.querySelectorAll('#itemTable tr');
            const table = document.getElementById('itemTable');
            while (table.rows.length > 1) table.deleteRow(1);
            for (let i = 1; i < newRows.length; i++) {
                table.appendChild(newRows[i].cloneNode(true));
            }
            form.reset();
            showNotification('Item added successfully!');
        } else {
            showNotification('Failed to add item.', '#dc3545');
        }
    });
});
document.getElementById('itemTable').addEventListener('click', function(e) {
    if (e.target.classList.contains('delete-btn')) {
        if (!confirm('Are you sure you want to delete this item?')) return;
        ajaxWithLoading(async () => {
            const id = e.target.getAttribute('data-id');
            const csrfToken = $("input[name='csrf_token']").val();
            const response = await fetch(`/delete/${id}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest' },
                body: `csrf_token=${encodeURIComponent(csrfToken)}`
            });
            if (response.ok) {
                let data;
                try {
                    data = await response.json();
                } catch (err) {
                    data = null;
                }
                if (data && data.success) {
                    const row = e.target.closest('tr');
                    row.parentNode.removeChild(row);
                    showNotification('Item deleted!', '#ffc107');
                } else {
                    showNotification('Failed to delete item.', '#dc3545');
                }
            } else {
                showNotification('Failed to delete item.', '#dc3545');
            }
        });
    }
    if (e.target.classList.contains('edit-btn')) {
        const row = e.target.closest('tr');
        document.getElementById('edit-id').value = row.getAttribute('data-id');
        document.getElementById('edit-name').value = row.children[1]?.textContent || '';
        document.getElementById('edit-brand').value = row.children[2]?.textContent || '';
        document.getElementById('edit-model').value = row.children[3]?.textContent || '';
        document.getElementById('edit-location').value = row.children[4]?.textContent || '';
        document.getElementById('edit-serial_number').value = row.children[5]?.textContent || '';
        document.getElementById('edit-owner').value = row.children[6]?.textContent || '';
        document.getElementById('edit-status').value = row.children[7]?.querySelector('.status-badge')?.textContent.trim() || '';
        document.getElementById('editModal').style.display = 'flex';
    }
    if (e.target.classList.contains('view-item-btn')) {
        const itemId = e.target.getAttribute('data-item-id');
        ajaxWithLoading(() => {
            const detailContent = document.getElementById('item-detail-content');
            detailContent.innerHTML = '<div class="text-center py-4"><div class="spinner-border" role="status"></div></div>';
            fetch(`/item/${itemId}`)
                .then(response => response.json())
                .then(data => {
                    if (data && data.success) {
                        const item = data.item;
                        let html = '<ul class="list-group">';
                        for (const [key, value] of Object.entries(item)) {
                            html += `<li class='list-group-item d-flex justify-content-between align-items-center'><span class='fw-bold text-capitalize'>${key.replace('_',' ')}</span><span>${value}</span></li>`;
                        }
                        html += '</ul>';
                        detailContent.innerHTML = html;
                    } else {
                        detailContent.innerHTML = '<div class="alert alert-danger">Failed to load item details.</div>';
                    }
                })
                .catch(() => {
                    detailContent.innerHTML = '<div class="alert alert-danger">Error loading item details.</div>';
                });
        });
        document.getElementById('itemDetailModal').style.display = 'flex';
    }
});
document.getElementById('closeModal').onclick = function() {
    document.getElementById('editModal').style.display = 'none';
};
document.getElementById('editForm').addEventListener('submit', function(e) {
    e.preventDefault();
    ajaxWithLoading(async () => {
        const id = document.getElementById('edit-id').value;
        const formData = new FormData(e.target);
        // Add CSRF token from the main form (or from a hidden input in the modal)
        let csrfToken = document.querySelector('#editForm input[name="csrf_token"]');
        if (!csrfToken) {
            // Try to get from the main form as fallback
            csrfToken = document.querySelector('#itemForm input[name="csrf_token"]');
        }
        if (csrfToken) {
            formData.append('csrf_token', csrfToken.value);
        }
        const response = await fetch(`/edit/${id}`, {
            method: 'POST',
            body: formData,
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        if (response.ok) {
            const html = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const newRows = doc.querySelectorAll('#itemTable tr');
            const table = document.getElementById('itemTable');
            while (table.rows.length > 1) table.deleteRow(1);
            for (let i = 1; i < newRows.length; i++) {
                table.appendChild(newRows[i].cloneNode(true));
            }
            document.getElementById('editModal').style.display = 'none';
            showNotification('Item updated!');
        } else {
            showNotification('Failed to update item.', '#dc3545');
        }
    });
});
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        document.getElementById('editModal').style.display = 'none';
    }
});
// Dark mode toggle
const darkModeKey = 'dataEntryDarkMode';
function setDarkMode(enabled) {
    document.body.classList.toggle('dark-mode', enabled);
    localStorage.setItem(darkModeKey, enabled ? '1' : '0');
    const toggleBtn = document.getElementById('toggleDarkMode');
    if (toggleBtn) {
        toggleBtn.innerHTML = enabled ? '<i class="fa fa-sun"></i> Light Mode' : '<i class="fa fa-moon"></i> Dark Mode';
    }
}
const toggleDarkModeBtn = document.getElementById('toggleDarkMode');
if (toggleDarkModeBtn) {
    toggleDarkModeBtn.onclick = function() {
        setDarkMode(!document.body.classList.contains('dark-mode'));
    };
}
if (localStorage.getItem(darkModeKey) === '1') setDarkMode(true);

// Bulk Delete logic
$('#select-all').on('change', function() {
    $('.item-checkbox').prop('checked', this.checked);
    $('#bulk-delete-btn').prop('disabled', $('.item-checkbox:checked').length === 0);
});
$(document).on('change', '.item-checkbox', function() {
    $('#bulk-delete-btn').prop('disabled', $('.item-checkbox:checked').length === 0);
    if (!this.checked) {
        $('#select-all').prop('checked', false);
    } else if ($('.item-checkbox:checked').length === $('.item-checkbox').length) {
        $('#select-all').prop('checked', true);
    }
});
$('#bulk-delete-form').on('submit', function(e) {
    e.preventDefault();
    const checked = $('.item-checkbox:checked');
    if (checked.length === 0) return;
    if (!confirm('Are you sure you want to delete the selected items?')) return;
    const ids = checked.map(function() { return this.value; }).get();
    // Add CSRF token to AJAX request
    const csrfToken = $("input[name='csrf_token']").val();
    $.ajax({
        url: '/bulk_delete',
        method: 'POST',
        data: { item_ids: ids, csrf_token: csrfToken },
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        traditional: true, // Ensure arrays are sent as repeated fields
        success: function(resp) {
            location.reload();
        },
        error: function(xhr) {
            alert('Bulk delete failed.');
        }
    });
});
