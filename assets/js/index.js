const bag = document.querySelector('.bag'),
  toast = document.querySelector('.toast');
let timer;
bag.addEventListener('click', () => {
  toast.classList.add('show');
  clearTimeout(timer);
  timer = setTimeout(() => toast.classList.remove('show'), 2600);
});
document.querySelectorAll('a[href="collections.html"]').forEach((link) =>
  link.addEventListener('click', () => {
    link.blur();
  }),
);
