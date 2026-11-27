(() => {
  const navs = document.querySelectorAll('.nav');

  navs.forEach((nav, index) => {
    const links = nav.querySelector('.nav-links');
    const brand = nav.querySelector('.brand');
    if (!links || !brand) return;

    const toggle = document.createElement('button');
    const menuId = links.id || `main-navigation-${index + 1}`;
    links.id = menuId;
    toggle.className = 'menu-toggle';
    toggle.type = 'button';
    toggle.setAttribute('aria-label', 'Open navigation menu');
    toggle.setAttribute('aria-controls', menuId);
    toggle.setAttribute('aria-expanded', 'false');
    toggle.innerHTML = '<span class="menu-toggle-icon" aria-hidden="true"></span>';
    nav.append(toggle);

    const closeMenu = () => {
      nav.classList.remove('is-menu-open');
      toggle.setAttribute('aria-expanded', 'false');
      toggle.setAttribute('aria-label', 'Open navigation menu');
    };

    const updateLayout = () => {
      // Measure the unmodified horizontal nav. This responds to the actual
      // available space, including the differing number of links per page.
      nav.classList.remove('nav-menu-collapsed');
      closeMenu();
      const style = getComputedStyle(nav);
      const available =
        nav.clientWidth - parseFloat(style.paddingLeft) - parseFloat(style.paddingRight);
      const required = brand.getBoundingClientRect().width + links.scrollWidth + 52;
      if (required > available) nav.classList.add('nav-menu-collapsed');
    };

    toggle.addEventListener('click', () => {
      const open = !nav.classList.contains('is-menu-open');
      nav.classList.toggle('is-menu-open', open);
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? 'Close navigation menu' : 'Open navigation menu');
    });

    links.addEventListener('click', (event) => {
      if (event.target.closest('a')) closeMenu();
    });

    document.addEventListener('click', (event) => {
      if (!nav.contains(event.target)) closeMenu();
    });

    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') closeMenu();
    });

    if ('ResizeObserver' in window) {
      new ResizeObserver(updateLayout).observe(nav);
    }
    window.addEventListener('resize', updateLayout);
    updateLayout();
  });
})();
