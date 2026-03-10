def estilo_tabla_js():
    JS = """
    export default function(component) {
        const { data, setTriggerValue, parentElement } = component;

        parentElement.innerHTML = '';

        const newElement = document.createElement('div');
        parentElement.appendChild(newElement);
        newElement.innerHTML = data;

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

        // ── MAPEO DE ASESORES ─────────────────────────────────────────────────
        const asesorMap = {
            'HUGO ENRIQUE PÉREZ RAMÍREZ':     'HUGO PÉREZ',
            'JOSÉ ALVARO MARTÍNEZ ESPEJEL':   'ALVARO MARTÍNEZ',
            'CARLOS ORTIZ':                   'CARLOS ORTIZ',
            'MAURICIO GUTIÉRREZ PÉREZ PALMA': 'MAURICIO GUTIÉRREZ'
        };

        const asesorColIndex = headers.findIndex(h => h.textContent.trim() === 'ASESOR');
        if (asesorColIndex !== -1) {
            allRows.forEach(row => {
                const cell = row.cells[asesorColIndex];
                if (cell) {
                    const fullName = cell.textContent.trim();
                    if (asesorMap[fullName]) cell.textContent = asesorMap[fullName];
                }
            });
        }

        // ── APPLY FILTERS ─────────────────────────────────────────────────────
        function applyFilters() {
            allRows.forEach(row => {
                const visible = Object.entries(activeFilters).every(([colIndex, selectedValues]) => {
                    if (selectedValues.size === 0) return true;
                    const cellText = row.cells[colIndex]?.textContent.trim() ?? '';
                    return selectedValues.has(cellText);
                });
                row.style.display = visible ? '' : 'none';
            });
        }

        // ── APPLY SORT ────────────────────────────────────────────────────────
        function applySort(colIndex) {
            const visibleRows = allRows.filter(r => r.style.display !== 'none');

            visibleRows.sort((a, b) => {
                const aText = a.cells[colIndex]?.textContent.trim().toLowerCase() ?? '';
                const bText = b.cells[colIndex]?.textContent.trim().toLowerCase() ?? '';
                const aNum  = parseFloat(aText.replace(/[$,]/g, ''));
                const bNum  = parseFloat(bText.replace(/[$,]/g, ''));
                const isNumeric = !isNaN(aNum) && !isNaN(bNum);

                return sortState.asc
                    ? (isNumeric ? aNum - bNum : aText.localeCompare(bText))
                    : (isNumeric ? bNum - aNum : bText.localeCompare(aText));
            });

            const hiddenRows = allRows.filter(r => r.style.display === 'none');
            [...visibleRows, ...hiddenRows].forEach(row => tbody.appendChild(row));

            headers.forEach(h => {
                const span = h.querySelector('.sort-indicator');
                if (span) span.textContent = '';
            });
            const indicator = headers[colIndex].querySelector('.sort-indicator');
            if (indicator) indicator.textContent = sortState.asc ? ' ▲' : ' ▼';
        }

        // ── UPDATE BUTTON APPEARANCE ──────────────────────────────────────────
        function updateFilterBtn(btn, colIndex, uniqueValues, checkboxes) {
            const selectedCount = checkboxes.filter(c => c.checked).length;
            const total         = uniqueValues.length;
            const isFiltered    = selectedCount < total;

            if (isFiltered) {
                btn.style.background = '#FF6B35';
                btn.style.color      = 'white';
                btn.style.fontWeight = 'bold';
                btn.textContent      = `▾ ${selectedCount}/${total}`;
            } else {
                btn.style.background = 'rgba(255,255,255,0.2)';
                btn.style.color      = '';
                btn.style.fontWeight = '';
                btn.textContent      = '▾';
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
                allRows.map(row => row.cells[colIndex]?.textContent.trim() ?? '')
            )].sort();

            const wrapper = document.createElement('div');
            wrapper.style.cssText = 'position:relative; display:inline-block; margin-left:6px;';

            const btn = document.createElement('span');
            btn.textContent = '▾';
            btn.classList.add('filter-btn');
            btn.style.cssText = `
                cursor:pointer; font-size:12px; padding:2px 6px;
                border-radius:4px; background:rgba(255,255,255,0.2);
                transition: background 0.2s, color 0.2s;
            `;

            const topDoc   = getTopDocument();
            const dropdown = topDoc.createElement('div');
            dropdown.classList.add('st-filter-dropdown');
            dropdown.style.cssText = `
                display:none; position:fixed;
                background:white; border:1px solid #ccc; border-radius:6px;
                box-shadow:0 6px 20px rgba(0,0,0,0.18); padding:8px;
                z-index:999999; min-width:190px; max-height:240px; overflow-y:auto;
                font-family: sans-serif;
            `;

            const dropHeader = topDoc.createElement('div');
            dropHeader.style.cssText = 'display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;';

            const dropTitle = topDoc.createElement('span');
            dropTitle.style.cssText = 'font-size:11px; color:#888; font-weight:bold; text-transform:uppercase;';
            dropTitle.textContent = 'Filtrar';

            const btnGroup = topDoc.createElement('div');
            btnGroup.style.cssText = 'display:flex; gap:4px;';

            const btnTodos = topDoc.createElement('button');
            btnTodos.textContent = 'Todos';
            btnTodos.style.cssText = `
                font-size:10px; padding:2px 6px; border:1px solid #4CAF50;
                border-radius:3px; background:white; color:#4CAF50; cursor:pointer;
            `;

            const btnNinguno = topDoc.createElement('button');
            btnNinguno.textContent = 'Ninguno';
            btnNinguno.style.cssText = `
                font-size:10px; padding:2px 6px; border:1px solid #f44336;
                border-radius:3px; background:white; color:#f44336; cursor:pointer;
            `;

            btnGroup.append(btnTodos, btnNinguno);
            dropHeader.append(dropTitle, btnGroup);
            dropdown.appendChild(dropHeader);

            const hr = topDoc.createElement('hr');
            hr.style.margin = '4px 0 6px 0';
            dropdown.appendChild(hr);

            const checkboxes = [];
            uniqueValues.forEach(val => {
                const label = topDoc.createElement('label');
                label.style.cssText = `
                    display:flex; align-items:center; gap:8px; padding:5px 4px;
                    cursor:pointer; color:#333; border-radius:4px; transition:background 0.1s;
                `;
                label.onmouseenter = () => label.style.background = '#f5f5f5';
                label.onmouseleave = () => label.style.background = '';

                const cb = topDoc.createElement('input');
                cb.type    = 'checkbox';
                cb.value   = val;
                cb.checked = true;
                cb.style.cssText = 'accent-color:#2196F3; width:14px; height:14px; flex-shrink:0;';
                checkboxes.push(cb);

                const text = topDoc.createElement('span');
                text.style.fontSize = '12px';

                const statusColors = {
                    'PERDIDO':    '#E74C3C',
                    'GANADO':     '#2ECC71',
                    'EN PROCESO': '#FFA500'
                };
                if (statusColors[val]) {
                    text.innerHTML = `<span style="background:${statusColors[val]};color:white;
                        padding:1px 7px;border-radius:3px;font-size:11px;">${val}</span>`;
                } else {
                    text.textContent = val || '(vacío)';
                }

                cb.addEventListener('change', () => {
                    const selected = checkboxes.filter(c => c.checked).map(c => c.value);
                    activeFilters[colIndex] = selected.length === uniqueValues.length
                        ? new Set() : new Set(selected);
                    updateFilterBtn(btn, colIndex, uniqueValues, checkboxes);
                    applyFilters();
                    if (sortState.col !== null) applySort(sortState.col);
                });

                label.append(cb, text);
                dropdown.appendChild(label);
            });

            btnTodos.addEventListener('click', e => {
                e.stopPropagation();
                checkboxes.forEach(cb => cb.checked = true);
                activeFilters[colIndex] = new Set();
                updateFilterBtn(btn, colIndex, uniqueValues, checkboxes);
                applyFilters();
                if (sortState.col !== null) applySort(sortState.col);
            });

            btnNinguno.addEventListener('click', e => {
                e.stopPropagation();
                checkboxes.forEach(cb => cb.checked = false);
                activeFilters[colIndex] = new Set(['__ninguno__']);
                updateFilterBtn(btn, colIndex, uniqueValues, checkboxes);
                applyFilters();
                if (sortState.col !== null) applySort(sortState.col);
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
            indicator.style.fontSize = '11px';
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
                applySort(colIndex);
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