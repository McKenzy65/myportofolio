(() => {
    'use strict';

    const section = document.getElementById('experience');
    if (!section) return;
    const listUrl = section.dataset.listUrl;
    const isAuthenticated = section.dataset.authenticated === 'true';
    const isOwner = section.dataset.owner === 'true';
    const canEdit = isOwner || section.dataset.editor === 'true';
    const list = document.getElementById('experience-list');
    const status = document.getElementById('experience-status');
    const search = document.getElementById('experience-search');
    const category = document.getElementById('experience-category');
    const retry = document.getElementById('experience-retry');
    const dialog = document.getElementById('experience-dialog');
    const form = document.getElementById('experience-form');
    const formFields = document.getElementById('experience-form-fields');
    const formStatus = document.getElementById('experience-form-status');
    const pending = new Set();
    const categories = {
        internship: 'Internship', research: 'Research', volunteer: 'Volunteer',
        'part-time': 'Part-Time', 'full-time': 'Full-Time', freelance: 'Freelance',
    };
    let listController;
    let detailController;
    let searchTimer;
    let editId = null;
    let isSaving = false;
    let originalEndDate = null;
    let originalLocalEndDate = '';

    function element(tag, className, text) {
        const node = document.createElement(tag);
        if (className) node.className = className;
        if (text !== undefined) node.textContent = String(text);
        return node;
    }

    function detailUrl(id) {
        return `${listUrl}${encodeURIComponent(id)}/`;
    }

    function formatError(data, code) {
        const labels = {title: 'Judul', description: 'Deskripsi', category: 'Kategori', thumbnail: 'URL gambar', ended_at: 'Tanggal selesai'};
        function messages(value) {
            if (typeof value === 'string') return [value];
            if (Array.isArray(value)) return value.flatMap(messages);
            if (value && typeof value === 'object') return Object.values(value).flatMap(messages);
            return [];
        }
        if (data && typeof data === 'object' && !Array.isArray(data)) {
            const errors = Object.entries(data).flatMap(([field, value]) =>
                messages(value).map(message => labels[field] ? `${labels[field]}: ${message}` : message)
            );
            if (errors.length) return errors.join(' ');
        }
        return messages(data).join(' ') || `Permintaan gagal (status ${code}).`;
    }

    async function request(url, method = 'GET', data, signal) {
        const headers = {'Accept': 'application/json'};
        if (method !== 'GET') {
            headers['Content-Type'] = 'application/json';
            headers['X-CSRFToken'] = document.querySelector('#experience-csrf [name="csrfmiddlewaretoken"]').value;
        }
        let response;
        try {
            response = await fetch(url, {
                method, headers, signal, credentials: 'same-origin',
                body: data === undefined ? undefined : JSON.stringify(data),
            });
        } catch (error) {
            if (error.name === 'AbortError') throw error;
            throw new Error(method === 'GET'
                ? 'Tidak dapat memuat pengalaman. Periksa koneksi lalu coba lagi.'
                : 'Hasil perubahan belum dapat dipastikan. Muat ulang daftar sebelum mencoba lagi.');
        }
        if (response.status === 204) return null;
        const result = await response.json().catch(() => null);
        if (!response.ok) throw new Error(formatError(result, response.status));
        if (!result || typeof result !== 'object') throw new Error('Respons server tidak valid. Muat ulang daftar untuk memeriksa hasilnya.');
        return result;
    }

    function actionButton(label, action, id, extraClass = '') {
        const button = element('button', `button button-secondary ${extraClass}`, label);
        button.type = 'button';
        button.dataset.action = action;
        button.dataset.id = id;
        button.disabled = pending.has(String(id));
        return button;
    }

    function render(items) {
        const fragment = document.createDocumentFragment();
        for (const item of items) {
            const row = element('li', 'exp-item');
            row.dataset.experienceId = item.id;
            const meta = element('div', 'exp-meta');
            const start = new Date(item.started_at);
            const end = item.ended_at ? new Date(item.ended_at) : null;
            const startYear = Number.isNaN(start.getTime()) ? '' : start.getFullYear();
            const endYear = end && !Number.isNaN(end.getTime()) ? end.getFullYear() : '';
            meta.append(element('span', 'exp-date', endYear ? `Selesai ${endYear}` : `Ditambahkan ${startYear}`));
            meta.append(element('span', 'exp-org', categories[item.category] || item.category));
            if (item.is_ongoing) meta.append(element('span', 'experience-ongoing', 'Masih berlangsung'));

            const body = element('div', 'exp-body');
            body.append(element('h3', '', item.title), element('p', '', item.description));
            if (item.thumbnail) {
                try {
                    const url = new URL(item.thumbnail);
                    if (['https:', 'http:'].includes(url.protocol)) {
                        const photo = element('img', 'experience-photo');
                        photo.src = url.href;
                        photo.alt = `Gambar ${item.title}`;
                        photo.loading = 'lazy';
                        photo.addEventListener('error', () => photo.remove(), {once: true});
                        body.append(photo);
                    }
                } catch (error) { /* Ignore legacy thumbnail values that are not valid URLs. */ }
            }
            const actions = element('div', 'experience-actions');
            if (isAuthenticated) {
                const star = actionButton(`${item.is_starred ? '★ Batalkan star' : '☆ Star'} (${item.star_count})`, 'star', item.id, 'experience-star');
                star.setAttribute('aria-pressed', String(Boolean(item.is_starred)));
                actions.append(star);
            } else {
                const login = element('a', '', `☆ ${item.star_count} star · Login untuk memberi star`);
                login.href = section.dataset.loginUrl;
                actions.append(login);
            }
            if (canEdit) actions.append(actionButton('Edit', 'edit', item.id));
            if (isOwner) actions.append(actionButton('Hapus', 'delete', item.id, 'button-danger'));
            body.append(actions);
            row.append(meta, body);
            fragment.append(row);
        }
        list.replaceChildren(fragment);
    }

    async function loadList() {
        if (listController) listController.abort();
        const controller = new AbortController();
        listController = controller;
        const url = new URL(listUrl, window.location.origin);
        if (search.value.trim()) url.searchParams.set('title', search.value.trim());
        if (category.value) url.searchParams.set('category', category.value);
        list.setAttribute('aria-busy', 'true');
        retry.hidden = true;
        status.textContent = 'Memuat pengalaman...';
        try {
            const items = await request(url, 'GET', undefined, controller.signal);
            if (controller.signal.aborted || controller !== listController) return;
            if (!Array.isArray(items)) throw new Error('Format daftar pengalaman tidak valid.');
            render(items);
            status.textContent = items.length
                ? `${items.length} pengalaman ditampilkan.`
                : (search.value.trim() || category.value ? 'Tidak ada pengalaman yang cocok dengan pencarian atau kategori ini.' : 'Belum ada data pengalaman di database.');
        } catch (error) {
            if (error.name === 'AbortError' || controller.signal.aborted || controller !== listController) return;
            list.replaceChildren();
            status.textContent = error.message;
            retry.hidden = false;
            showToast('Gagal memuat pengalaman', error.message, 'error');
        } finally {
            if (controller === listController) list.setAttribute('aria-busy', 'false');
        }
    }

    function setPending(id, busy) {
        const key = String(id);
        if (busy) pending.add(key); else pending.delete(key);
        for (const button of list.querySelectorAll('button[data-id]')) {
            if (button.dataset.id === key) {
                button.disabled = busy;
                button.setAttribute('aria-busy', String(busy));
            }
        }
    }

    function localDateValue(value) {
        if (!value) return '';
        const date = new Date(value);
        if (Number.isNaN(date.getTime())) return '';
        const pad = number => String(number).padStart(2, '0');
        return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
    }

    async function openForm(id = null) {
        if (!dialog || isSaving) return;
        if (detailController) detailController.abort();
        const controller = new AbortController();
        detailController = controller;
        editId = id;
        originalEndDate = null;
        originalLocalEndDate = '';
        form.reset();
        document.getElementById('experience-dialog-title').textContent = id ? 'Edit pengalaman' : 'Tambah pengalaman';
        formStatus.textContent = id ? 'Memuat detail pengalaman...' : '';
        formFields.disabled = Boolean(id);
        dialog.showModal();
        dialog.scrollTop = 0;
        if (!id) { form.elements.title.focus(); return; }
        try {
            const item = await request(detailUrl(id), 'GET', undefined, controller.signal);
            if (controller.signal.aborted || !dialog.open || controller !== detailController) return;
            form.elements.title.value = item.title;
            form.elements.description.value = item.description;
            form.elements.category.value = item.category;
            form.elements.thumbnail.value = item.thumbnail || '';
            originalEndDate = item.ended_at;
            originalLocalEndDate = localDateValue(item.ended_at);
            form.elements.ended_at.value = originalLocalEndDate;
            formStatus.textContent = '';
            formFields.disabled = false;
            form.elements.title.focus();
        } catch (error) {
            if (error.name === 'AbortError' || controller.signal.aborted || controller !== detailController) return;
            dialog.close();
            showToast('Gagal membuka pengalaman', error.message, 'error');
        }
    }

    async function saveForm(event) {
        event.preventDefault();
        if (isSaving || !form.reportValidity()) return;
        const currentId = editId;
        if (currentId && pending.has(String(currentId))) return;
        const endValue = form.elements.ended_at.value;
        const payload = {
            title: form.elements.title.value,
            description: form.elements.description.value,
            category: form.elements.category.value,
            thumbnail: form.elements.thumbnail.value,
            ended_at: endValue === originalLocalEndDate ? originalEndDate : (endValue ? new Date(endValue).toISOString() : null),
        };
        isSaving = true;
        if (currentId) setPending(currentId, true);
        formFields.disabled = true;
        dialog.querySelector('.experience-close').disabled = true;
        formStatus.textContent = 'Menyimpan pengalaman...';
        form.setAttribute('aria-busy', 'true');
        try {
            await request(currentId ? detailUrl(currentId) : listUrl, currentId ? 'PATCH' : 'POST', payload);
            dialog.close();
            showToast('Berhasil', currentId ? 'Pengalaman berhasil diperbarui.' : 'Pengalaman berhasil ditambahkan.', 'success');
            await loadList();
        } catch (error) {
            formStatus.textContent = error.message;
            showToast('Gagal menyimpan pengalaman', error.message, 'error');
        } finally {
            isSaving = false;
            formFields.disabled = false;
            dialog.querySelector('.experience-close').disabled = false;
            form.removeAttribute('aria-busy');
            if (currentId) setPending(currentId, false);
        }
    }

    list.addEventListener('click', async event => {
        const button = event.target.closest('button[data-action]');
        if (!button || !list.contains(button)) return;
        const {action, id} = button.dataset;
        if (pending.has(id)) return;
        if (action === 'edit') { await openForm(id); return; }
        if (action === 'delete' && !window.confirm('Hapus pengalaman ini? Tindakan ini tidak dapat dibatalkan.')) return;
        setPending(id, true);
        try {
            if (action === 'star') {
                const item = await request(`${detailUrl(id)}star/`, 'POST');
                showToast('Berhasil', item.is_starred ? 'Pengalaman ditambahkan ke favorit.' : 'Star pengalaman dibatalkan.', 'success');
            } else if (action === 'delete') {
                await request(detailUrl(id), 'DELETE');
                showToast('Berhasil', 'Pengalaman berhasil dihapus.', 'success');
            }
            await loadList();
        } catch (error) {
            showToast('Perubahan gagal', error.message, 'error');
        } finally {
            setPending(id, false);
        }
    });

    search.addEventListener('input', () => {
        clearTimeout(searchTimer);
        if (listController) listController.abort();
        searchTimer = setTimeout(loadList, 300);
    });
    document.getElementById('experience-search-form').addEventListener('submit', event => {
        event.preventDefault(); clearTimeout(searchTimer); loadList();
    });
    category.addEventListener('change', () => { clearTimeout(searchTimer); loadList(); });
    document.getElementById('experience-reset').addEventListener('click', () => {
        clearTimeout(searchTimer); search.value = ''; category.value = ''; loadList();
    });
    retry.addEventListener('click', loadList);
    const add = document.getElementById('experience-add');
    if (add) add.addEventListener('click', () => openForm());
    if (dialog) {
        form.addEventListener('submit', saveForm);
        dialog.addEventListener('cancel', event => { if (isSaving) event.preventDefault(); });
        dialog.addEventListener('close', () => {
            if (detailController) detailController.abort();
            editId = null;
        });
        for (const button of dialog.querySelectorAll('[data-close-experience]')) {
            button.addEventListener('click', () => { if (!isSaving) dialog.close(); });
        }
    }
    loadList();
})();
