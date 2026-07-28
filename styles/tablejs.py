def estilo_tabla_js():
    JS = """
    export default function(component) {
        const { data, setTriggerValue, parentElement } = component;

        parentElement.innerHTML = '';

        const newElement = document.createElement('div');
        parentElement.appendChild(newElement);
        newElement.innerHTML = data;

        let PAGE_SIZE = 15;
        let currentPage = 0;

        const FUNNEL_SVG = '<svg viewBox="0 0 16 16" fill="currentColor" style="width:11px;height:11px;display:block;"><path d="M1.5 1.5A.5.5 0 0 1 2 1h12a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-.128.334L10 8.692V13.5a.5.5 0 0 1-.342.474l-3 1A.5.5 0 0 1 6 14.5V8.692L1.628 3.834A.5.5 0 0 1 1.5 3.5z"/></svg>';

        // ── SCROLL HORIZONTAL: envolver la tabla en un div scrolleable ────────
        const table = newElement.querySelector('table');
        const scrollWrapper = document.createElement('div');
        scrollWrapper.style.cssText = `
            overflow-x: auto;
            overflow-y: visible;
            width: 100%;
            -webkit-overflow-scrolling: touch;
        `;
        table.parentNode.insertBefore(scrollWrapper, table);
        scrollWrapper.appendChild(table);

        // La tabla crece libremente — el scroll wrapper absorbe el ancho extra
        table.style.tableLayout = 'auto';
        table.style.minWidth    = '100%';
        table.style.width       = 'max-content';
        table.style.overflow    = 'visible';
        const thead = table.querySelector('thead');
        if (thead) thead.style.overflow = 'visible';

        const headers = Array.from(table.querySelectorAll('thead th'));
        const allRows = Array.from(table.querySelectorAll('tbody tr'));
        const tbody   = table.querySelector('tbody');

        const skipFilterColumns = ['Acción', 'Teléfono', 'Email'];
        const skipSortColumns   = ['Acción'];

        const activeFilters = {};
        let sortState = { col: null, asc: true };

        // Celdas con contenido enriquecido (avatares, badges) exponen el valor
        // real en data-value para que filtro/orden no lean el texto compuesto.
        function cellText(row, colIndex) {
            const cell = row.cells[colIndex];
            if (!cell) return '';
            return cell.dataset.value !== undefined ? cell.dataset.value : cell.textContent.trim();
        }

        // ── FILTRAR + ORDENAR (sobre TODAS las filas, no solo la página) ───────
        function getFilteredRows() {
            return allRows.filter(row =>
                Object.entries(activeFilters).every(([colIndex, selectedValues]) => {
                    if (selectedValues.size === 0) return true;
                    return selectedValues.has(cellText(row, colIndex));
                })
            );
        }

        function sortRows(rows) {
            if (sortState.col === null) return rows;
            const colIndex = sortState.col;
            return [...rows].sort((a, b) => {
                const aText = cellText(a, colIndex).toLowerCase();
                const bText = cellText(b, colIndex).toLowerCase();
                const aNum  = parseFloat(aText.replace(/[$,]/g, ''));
                const bNum  = parseFloat(bText.replace(/[$,]/g, ''));
                const isNumeric = !isNaN(aNum) && !isNaN(bNum);

                return sortState.asc
                    ? (isNumeric ? aNum - bNum : aText.localeCompare(bText))
                    : (isNumeric ? bNum - aNum : bText.localeCompare(aText));
            });
        }

        // ── PAGINADOR (opera sobre el resultado ya filtrado/ordenado) ─────────
        const pager = document.createElement('div');
        pager.style.cssText = `
            display:flex; align-items:center; justify-content:space-between; gap:16px;
            padding:12px 4px 2px 4px; font-family:'Inter',sans-serif;
            font-size:12.5px; color:#6c757d;
        `;
        const pagerInfo = document.createElement('span');

        const pagerControls = document.createElement('div');
        pagerControls.style.cssText = 'display:flex; align-items:center; gap:10px;';

        const pageSizeSelect = document.createElement('select');
        pageSizeSelect.style.cssText = `
            border:1px solid #ced4da; border-radius:6px; padding:4px 8px;
            font-size:12px; color:#495057; background:#fff; cursor:pointer;
        `;
        [15, 25, 50, 100].forEach(n => {
            const opt = document.createElement('option');
            opt.value = String(n);
            opt.textContent = `${n} filas`;
            if (n === PAGE_SIZE) opt.selected = true;
            pageSizeSelect.appendChild(opt);
        });
        pageSizeSelect.addEventListener('change', () => {
            PAGE_SIZE = parseInt(pageSizeSelect.value, 10);
            currentPage = 0;
            render();
        });

        const btnPrev = document.createElement('button');
        const btnNext = document.createElement('button');
        const pagerPageInfo = document.createElement('span');

        [btnPrev, btnNext].forEach(b => {
            b.style.cssText = `
                border:1px solid #ced4da; background:#fff; color:#495057; border-radius:6px;
                padding:4px 11px; font-size:12.5px; font-weight:500; transition:background .15s, border-color .15s;
            `;
            b.addEventListener('mouseenter', () => { if (!b.disabled) b.style.background = '#f1f3f5'; });
            b.addEventListener('mouseleave', () => { if (!b.disabled) b.style.background = '#fff'; });
        });
        btnPrev.textContent = '‹';
        btnNext.textContent = '›';
        pagerPageInfo.style.cssText = 'color:#495057; font-weight:500;';

        pagerControls.append(pageSizeSelect, btnPrev, pagerPageInfo, btnNext);
        pager.append(pagerInfo, pagerControls);
        scrollWrapper.parentNode.insertBefore(pager, scrollWrapper.nextSibling);

        btnPrev.addEventListener('click', () => { if (currentPage > 0) { currentPage--; render(); } });
        btnNext.addEventListener('click', () => { currentPage++; render(); });

        // ── RENDER: filtra → ordena → pagina → pinta ──────────────────────────
        function render() {
            const filtered = getFilteredRows();
            const sorted   = sortRows(filtered);
            const totalItems = sorted.length;
            const totalPages = Math.max(1, Math.ceil(totalItems / PAGE_SIZE));

            if (currentPage >= totalPages) currentPage = totalPages - 1;
            if (currentPage < 0) currentPage = 0;

            const start = currentPage * PAGE_SIZE;
            const pageRows = sorted.slice(start, start + PAGE_SIZE);
            const pageRowSet = new Set(pageRows);

            sorted.forEach(row => tbody.appendChild(row));
            allRows.forEach(row => { row.style.display = pageRowSet.has(row) ? '' : 'none'; });

            const rangeStart = totalItems === 0 ? 0 : start + 1;
            const rangeEnd   = Math.min(start + PAGE_SIZE, totalItems);
            pagerInfo.textContent = `${rangeStart}–${rangeEnd} de ${totalItems} registro${totalItems === 1 ? '' : 's'}`;
            pagerPageInfo.textContent = `${currentPage + 1}/${totalPages}`;

            btnPrev.disabled = currentPage === 0;
            btnNext.disabled = currentPage >= totalPages - 1;
            [btnPrev, btnNext].forEach(b => {
                b.style.opacity = b.disabled ? '0.5' : '1';
                b.style.cursor  = b.disabled ? 'default' : 'pointer';
            });

            headers.forEach((h, i) => {
                const span = h.querySelector('.sort-indicator');
                if (!span) return;
                if (sortState.col === i) {
                    span.textContent = sortState.asc ? '▲' : '▼';
                    span.style.opacity = '1';
                } else {
                    span.textContent = '⇅';
                    span.style.opacity = '.5';
                }
            });
        }

        // ── UPDATE BUTTON APPEARANCE ──────────────────────────────────────────
        function updateFilterBtn(btn, colIndex, uniqueValues, checkboxes) {
            const selectedCount = checkboxes.filter(c => c.checked).length;
            const total         = uniqueValues.length;
            const isFiltered    = selectedCount < total;

            if (isFiltered) {
                btn.style.background = '#0d6efd';
                btn.style.color      = 'white';
                btn.innerHTML = FUNNEL_SVG + `<span style="font-size:10px;font-weight:700;">${selectedCount}/${total}</span>`;
            } else {
                btn.style.background = 'rgba(0,0,0,0.06)';
                btn.style.color      = '';
                btn.innerHTML = FUNNEL_SVG;
            }
        }

        // ── HELPER: acceder al documento padre (fuera del iframe) ─────────────
        function getTopDocument() {
            try { return window.top.document; } catch(e) { return document; }
        }

        // ── BUILD DROPDOWN ────────────────────────────────────────────────────
        // Se adjunta al <body> del documento TOP para salir completamente
        // de los límites del iframe de Streamlit.
        function buildDropdown(th, colIndex) {
            const uniqueValues = [...new Set(
                allRows.map(row => cellText(row, colIndex))
            )].sort();

            const wrapper = document.createElement('div');
            wrapper.style.cssText = 'position:relative; display:inline-block; margin-left:6px;';

            const btn = document.createElement('span');
            btn.innerHTML = FUNNEL_SVG;
            btn.classList.add('filter-btn');
            btn.style.cssText = `
                cursor:pointer; display:inline-flex; align-items:center; gap:3px;
                padding:4px 6px; border-radius:5px; background:rgba(0,0,0,0.06);
                transition: background 0.2s, color 0.2s;
            `;

            const topDoc   = getTopDocument();
            const dropdown = topDoc.createElement('div');
            dropdown.classList.add('st-filter-dropdown');
            dropdown.style.cssText = `
                display:none; position:fixed;
                background:#fff; border:1px solid #dee2e6; border-radius:8px;
                box-shadow:0 8px 24px rgba(0,0,0,0.12); padding:10px;
                z-index:999999; min-width:190px; max-height:240px; overflow-y:auto;
                font-family:'Inter',sans-serif;
            `;

            const dropHeader = topDoc.createElement('div');
            dropHeader.style.cssText = 'display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;';

            const dropTitle = topDoc.createElement('span');
            dropTitle.style.cssText = 'font-size:10.5px; color:#6c757d; font-weight:600; text-transform:uppercase; letter-spacing:.04em;';
            dropTitle.textContent = 'Filtrar';

            const btnGroup = topDoc.createElement('div');
            btnGroup.style.cssText = 'display:flex; gap:4px;';

            const btnTodos = topDoc.createElement('button');
            btnTodos.textContent = 'Todos';
            btnTodos.style.cssText = `
                font-size:10px; padding:3px 7px; border:1px solid #a3cfbb;
                border-radius:5px; background:#d1e7dd; color:#0f5132; cursor:pointer; font-weight:500;
            `;

            const btnNinguno = topDoc.createElement('button');
            btnNinguno.textContent = 'Ninguno';
            btnNinguno.style.cssText = `
                font-size:10px; padding:3px 7px; border:1px solid #f1aeb5;
                border-radius:5px; background:#f8d7da; color:#842029; cursor:pointer; font-weight:500;
            `;

            btnGroup.append(btnTodos, btnNinguno);
            dropHeader.append(dropTitle, btnGroup);
            dropdown.appendChild(dropHeader);

            const hr = topDoc.createElement('hr');
            hr.style.cssText = 'margin:4px 0 6px 0; border:none; border-top:1px solid #e9ecef;';
            dropdown.appendChild(hr);

            const checkboxes = [];
            uniqueValues.forEach(val => {
                const label = topDoc.createElement('label');
                label.style.cssText = `
                    display:flex; align-items:center; gap:8px; padding:5px 4px;
                    cursor:pointer; color:#343a40; border-radius:5px; transition:background 0.1s;
                `;
                label.onmouseenter = () => label.style.background = '#f8f9fa';
                label.onmouseleave = () => label.style.background = '';

                const cb = topDoc.createElement('input');
                cb.type    = 'checkbox';
                cb.value   = val;
                cb.checked = true;
                cb.style.cssText = 'accent-color:#0d6efd; width:14px; height:14px; flex-shrink:0;';
                checkboxes.push(cb);

                const text = topDoc.createElement('span');
                text.style.fontSize = '12.5px';

                const statusColors = {
                    'PERDIDO':    { bg: '#f8d7da', fg: '#842029' },
                    'GANADO':     { bg: '#d1e7dd', fg: '#0f5132' },
                    'EN PROCESO': { bg: '#fff3cd', fg: '#664d03' }
                };
                if (statusColors[val]) {
                    const c = statusColors[val];
                    text.innerHTML = `<span style="background:${c.bg};color:${c.fg};
                        padding:2px 9px;border-radius:999px;font-size:11px;font-weight:600;">${val}</span>`;
                } else {
                    text.textContent = val || '(vacío)';
                }

                cb.addEventListener('change', () => {
                    const selected = checkboxes.filter(c => c.checked).map(c => c.value);
                    activeFilters[colIndex] = selected.length === uniqueValues.length
                        ? new Set() : new Set(selected);
                    updateFilterBtn(btn, colIndex, uniqueValues, checkboxes);
                    currentPage = 0;
                    render();
                });

                label.append(cb, text);
                dropdown.appendChild(label);
            });

            btnTodos.addEventListener('click', e => {
                e.stopPropagation();
                checkboxes.forEach(cb => cb.checked = true);
                activeFilters[colIndex] = new Set();
                updateFilterBtn(btn, colIndex, uniqueValues, checkboxes);
                currentPage = 0;
                render();
            });

            btnNinguno.addEventListener('click', e => {
                e.stopPropagation();
                checkboxes.forEach(cb => cb.checked = false);
                activeFilters[colIndex] = new Set(['__ninguno__']);
                updateFilterBtn(btn, colIndex, uniqueValues, checkboxes);
                currentPage = 0;
                render();
            });

            btn.addEventListener('click', e => {
                e.stopPropagation();
                const isOpen = dropdown.style.display === 'block';

                topDoc.querySelectorAll('.st-filter-dropdown').forEach(d => d.style.display = 'none');

                if (!isOpen) {
                    // Coordenadas del botón en el viewport del iframe
                    const btnRect = btn.getBoundingClientRect();

                    // Buscar el offset del iframe dentro del documento top
                    let iframeTop = 0, iframeLeft = 0;
                    try {
                        const iframes = Array.from(topDoc.querySelectorAll('iframe'));
                        for (const f of iframes) {
                            try {
                                if (f.contentWindow === window) {
                                    const fr   = f.getBoundingClientRect();
                                    iframeTop  = fr.top;
                                    iframeLeft = fr.left;
                                    break;
                                }
                            } catch(ex) {}
                        }
                    } catch(ex) {}

                    let top  = iframeTop  + btnRect.bottom;
                    let left = iframeLeft + btnRect.left;

                    dropdown.style.top     = top  + 'px';
                    dropdown.style.left    = left + 'px';
                    dropdown.style.display = 'block';

                    // Ajustar si se sale por la derecha
                    const ddRect   = dropdown.getBoundingClientRect();
                    const vpWidth  = topDoc.documentElement.clientWidth;
                    const vpHeight = topDoc.documentElement.clientHeight;

                    if (ddRect.right > vpWidth - 8) {
                        left = left - (ddRect.right - vpWidth + 8);
                        dropdown.style.left = left + 'px';
                    }
                    // Abrir hacia arriba si no hay espacio abajo
                    if (ddRect.bottom > vpHeight - 8) {
                        top = iframeTop + btnRect.top - ddRect.height;
                        dropdown.style.top = top + 'px';
                    }
                }
            });

            // Adjuntar al body del doc top — completamente fuera del iframe
            topDoc.body.appendChild(dropdown);
            wrapper.append(btn);
            th.appendChild(wrapper);
        }

        // ── BUILD SORT ────────────────────────────────────────────────────────
        function buildSort(th, colIndex) {
            const indicator = document.createElement('span');
            indicator.classList.add('sort-indicator');
            indicator.style.cssText = 'font-size:10px; margin-left:5px; opacity:.5;';
            indicator.textContent = '⇅';
            th.appendChild(indicator);

            th.style.cursor = 'pointer';
            th.addEventListener('click', e => {
                if (e.target.closest('.st-filter-dropdown')) return;
                if (e.target.tagName === 'INPUT') return;
                if (e.target.classList.contains('filter-btn')) return;

                if (sortState.col === colIndex) {
                    sortState.asc = !sortState.asc;
                } else {
                    sortState.col = colIndex;
                    sortState.asc = true;
                }
                render();
            });
        }

        // ── BUILD RESIZABLE ───────────────────────────────────────────────────
        // El scroll horizontal evita el solapamiento al redimensionar
        function buildResizable(th) {
            const handle = document.createElement('div');
            handle.style.cssText = `
                position:absolute; right:0; top:0;
                width:5px; height:100%;
                cursor:col-resize; user-select:none; z-index:10;
            `;
            th.style.position = 'relative';
            th.appendChild(handle);

            let startX, startWidth;

            handle.addEventListener('mousedown', e => {
                e.stopPropagation();
                e.preventDefault();
                startX     = e.pageX;
                startWidth = th.offsetWidth;
                handle.style.background = 'rgba(33,150,243,0.5)';

                const onMove = e => {
                    const newWidth = Math.max(60, startWidth + (e.pageX - startX));
                    th.style.width    = newWidth + 'px';
                    th.style.minWidth = newWidth + 'px';
                    // Dejar que la tabla crezca — el scroll wrapper se encarga del resto
                    table.style.width = 'max-content';
                };

                const onUp = () => {
                    handle.style.background = '';
                    document.removeEventListener('mousemove', onMove);
                    document.removeEventListener('mouseup', onUp);
                };

                document.addEventListener('mousemove', onMove);
                document.addEventListener('mouseup', onUp);
            });

            handle.addEventListener('mouseenter', () => handle.style.background = 'rgba(33,150,243,0.3)');
            handle.addEventListener('mouseleave', () => handle.style.background = '');
        }

        // ── INIT ──────────────────────────────────────────────────────────────
        headers.forEach((th, colIndex) => {
            th.style.whiteSpace = 'nowrap';
            if (!skipSortColumns.includes(th.textContent.trim()))   buildSort(th, colIndex);
            if (!skipFilterColumns.includes(th.textContent.trim())) buildDropdown(th, colIndex);
            buildResizable(th);
        });

        render();

        // Cerrar dropdowns al hacer click fuera (tanto en top doc como en iframe)
        const topDoc = getTopDocument();
        const closeAll = () => topDoc.querySelectorAll('.st-filter-dropdown').forEach(d => d.style.display = 'none');
        topDoc.addEventListener('click', closeAll);
        document.addEventListener('click', closeAll);

        // ── BOTONES DE ACCIÓN ─────────────────────────────────────────────────
        const links = newElement.querySelectorAll('a');
        links.forEach(link => {
            link.onclick = () => setTriggerValue('clicked', link.getAttribute('data-link'));
        });
    }
    """
    return JS
