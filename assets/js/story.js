const bag = document.querySelector('.bag'),
  toast = document.querySelector('.toast');
let timer;
bag.addEventListener('click', () => {
  toast.classList.add('show');
  clearTimeout(timer);
  timer = setTimeout(() => toast.classList.remove('show'), 2500);
});
