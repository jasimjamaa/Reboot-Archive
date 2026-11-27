(() => {
  const root = document.querySelector('[data-listing-search]');
  if (!root) return;

  const grid = document.querySelector('.grid');
  const search = root.querySelector('.listing-search');
  const category = root.querySelector('[name=category]');
  const series = root.querySelector('[name=series]');
  const minPrice = root.querySelector('[name=min-price]');
  const maxPrice = root.querySelector('[name=max-price]');
  const minValue = root.querySelector('[name=min-value]');
  const maxValue = root.querySelector('[name=max-value]');
  const priceAllEnabled = root.querySelector('[name=price-all-enabled]');
  const minEnabled = root.querySelector('[name=min-enabled]');
  const maxEnabled = root.querySelector('[name=max-enabled]');
  const sort = root.querySelector('.listing-sort');
  const reset = root.querySelector('.listing-reset');
  const count = root.querySelector('.listing-count');
  const filter = root.querySelector('.listing-filter');
  const filterToggle = root.querySelector('.listing-filter-toggle');
  const filterPanel = root.querySelector('.listing-filter-panel');
  const status = root.dataset.listingStatus;
  const cards = [...grid.querySelectorAll('.card')];
  let listings = [];
  const categories = ['Desktop', 'Portable', 'Music', 'Accessories', 'Other'];
  const deviceSeries = ['iPhone', 'iPad', 'Mac', 'iPod', 'Other'];

  const text = (value) => String(value || '').toLowerCase();
  const productNumber = (id) => Number(String(id).replace(/\D/g, '')) || 0;
  const price = (item) => Number(item['Price (in GBP)']) || 0;
  const populate = (element, values, label) => {
    element.innerHTML =
      `<option value="">${label}</option>` +
      values.map((value) => `<option>${value}</option>`).join('');
  };
  const canonical = (value, options) =>
    options.find((option) => text(option) === text(value)) || 'Other';
  const setBounds = () => {
    const prices = listings.map(price).filter((value) => Number.isFinite(value));
    const low = 0;
    const highestPrice = prices.length ? Math.max(...prices) : 0;
    const high = highestPrice;
    [minPrice, maxPrice].forEach((input) => {
      input.min = low;
      input.max = high;
      input.step = '0.01';
    });
    minPrice.value = low;
    maxPrice.value = high;
    minValue.value = low;
    maxValue.value = high;
  };
  const updatePriceInputs = () => {
    priceAllEnabled.checked = minEnabled.checked && maxEnabled.checked;
    priceAllEnabled.indeterminate = minEnabled.checked !== maxEnabled.checked;
  };
  const syncPricePair = (bound, source) => {
    const slider = bound === 'min' ? minPrice : maxPrice;
    const value = bound === 'min' ? minValue : maxValue;
    if (source === 'slider') {
      value.value = slider.value;
      return;
    }
    const numeric = Number(value.value);
    if (!Number.isFinite(numeric)) return;
    const clamped = Math.min(Math.max(numeric, Number(slider.min)), Number(slider.max));
    slider.value = String(clamped);
    value.value = String(clamped);
  };
  const render = () => {
    const query = text(search.value);
    const matches = listings
      .filter((item) => {
        const haystack = [item.Title, item['Device Series'], item['Device Model']]
          .map(text)
          .join(' ');
        return (
          (!query || haystack.includes(query)) &&
          (!category.value || canonical(item.Category, categories) === category.value) &&
          (!series.value || canonical(item['Device Series'], deviceSeries) === series.value) &&
          (!minEnabled.checked || price(item) >= Number(minPrice.value)) &&
          (!maxEnabled.checked || price(item) <= Number(maxPrice.value))
        );
      })
      .sort((a, b) =>
        sort.value === 'price-asc'
          ? price(a) - price(b)
          : sort.value === 'price-desc'
            ? price(b) - price(a)
            : productNumber(a['Product ID']) - productNumber(b['Product ID']),
      );
    const ids = new Set(matches.map((item) => item['Product ID']));
    cards.forEach((card) => {
      card.hidden = !ids.has(card.dataset.productId);
    });
    matches.forEach((item) => {
      const card = cards.find((node) => node.dataset.productId === item['Product ID']);
      if (card) grid.append(card);
    });
    grid.querySelector('.listing-empty')?.remove();
    if (!matches.length) {
      const empty = document.createElement('p');
      empty.className = 'listing-empty';
      empty.textContent = 'No listings match those choices.';
      grid.append(empty);
    }
    count.textContent = `${matches.length} ${matches.length === 1 ? 'listing' : 'listings'}`;
  };
  const initialise = (catalogue) => {
    const cardIds = new Set(cards.map((card) => card.dataset.productId));
    listings = catalogue.Listings.filter(
      (item) => cardIds.has(item['Product ID']) && item.Status === status,
    );
    // Preserve visible cards if an older catalogue is served from cache.
    if (!listings.length)
      listings = cards.map((card) => ({
        'Product ID': card.dataset.productId,
        Title: card.textContent,
        Category: card.dataset.category || 'Other',
        'Device Series': '',
        'Device Model': '',
        'Price (in GBP)': 0,
        Status: status,
      }));
    populate(category, categories, 'All categories');
    populate(series, deviceSeries, 'All device series');
    const requestedCategory = new URLSearchParams(window.location.search).get('category');
    if (requestedCategory) category.value = canonical(requestedCategory, categories);
    setBounds();
    updatePriceInputs();
    render();
  };
  root.addEventListener('input', (event) => {
    if (event.target.matches('[name=min-price]')) syncPricePair('min', 'slider');
    if (event.target.matches('[name=max-price]')) syncPricePair('max', 'slider');
    if (event.target.matches('[name=min-value]')) syncPricePair('min', 'value');
    if (event.target.matches('[name=max-value]')) syncPricePair('max', 'value');
  });
  root.addEventListener('change', (event) => {
    if (event.target.matches('[name=min-price]')) syncPricePair('min', 'slider');
    if (event.target.matches('[name=max-price]')) syncPricePair('max', 'slider');
    if (event.target.matches('[name=min-value]')) syncPricePair('min', 'value');
    if (event.target.matches('[name=max-value]')) syncPricePair('max', 'value');
    if (event.target === priceAllEnabled) {
      minEnabled.checked = priceAllEnabled.checked;
      maxEnabled.checked = priceAllEnabled.checked;
    }
    if (event.target.matches('[name=min-enabled], [name=max-enabled], [name=price-all-enabled]'))
      updatePriceInputs();
    render();
  });
  const closeFilters = () => {
    filter.classList.remove('is-open');
    filterPanel.hidden = true;
    filterToggle.setAttribute('aria-expanded', 'false');
  };
  filterToggle.addEventListener('click', () => {
    const opening = filterPanel.hidden;
    filter.classList.toggle('is-open', opening);
    filterPanel.hidden = !opening;
    filterToggle.setAttribute('aria-expanded', String(opening));
  });
  document.addEventListener('click', (event) => {
    if (!filter.contains(event.target)) closeFilters();
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') closeFilters();
  });
  reset.addEventListener('click', () => {
    search.value = '';
    category.value = '';
    series.value = '';
    sort.value = 'product-id';
    minEnabled.checked = false;
    maxEnabled.checked = false;
    setBounds();
    updatePriceInputs();
    render();
    closeFilters();
  });
  fetch('inventory/catalog.json')
    .then((response) => (response.ok ? response.json() : Promise.reject()))
    .then(initialise)
    .catch(() => initialise({ Listings: [] }));
})();
