document.querySelector('.menu-btn')?.addEventListener('click',()=>document.querySelector('.sidebar').classList.toggle('show'));
document.querySelector('#globalSearch')?.addEventListener('input', event => {
  const query = event.target.value.trim().toLowerCase();
  document.querySelectorAll('tbody tr, .activity, .notification').forEach(row => {
    row.hidden = Boolean(query) && !row.textContent.toLowerCase().includes(query);
  });
});
document.querySelectorAll('.attention > div').forEach((item, index) => {
  const destinations = ['/maintenance/', '/assets/?status=ALLOCATED', '/transfers/'];
  item.style.cursor = 'pointer';
  item.addEventListener('click', () => { window.location.href = destinations[index]; });
});
