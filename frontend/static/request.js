(() => {
  const form = document.querySelector('#request-form');
  if (!form) return;
  const selected = [];
  const body = document.querySelector('#selected-body');
  const hidden = document.querySelector('#hidden-items');
  function render() {
    body.replaceChildren();
    hidden.replaceChildren();
    if (!selected.length) {
      const tr = body.insertRow();
      tr.insertCell().colSpan = 4;
      tr.cells[0].textContent = 'No items added yet.';
      tr.className = 'empty-state';
      return;
    }
    selected.forEach(({type, name, qty}, index) => {
      const tr = body.insertRow();
      [type, name, qty].forEach(value => { tr.insertCell().textContent = value; });
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'btn small secondary';
      button.textContent = 'Remove';
      button.addEventListener('click', () => { selected.splice(index, 1); render(); });
      tr.insertCell().append(button);
      for (const [key, value] of Object.entries({item_types: type, item_names: name, item_quantities: qty})) {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = key;
        input.value = value;
        hidden.append(input);
      }
    });
  }
  document.querySelector('#search-results').addEventListener('click', event => {
    const button = event.target.closest('.add-item');
    if (!button) return;
    const item = button.closest('.result-item');
    const {type, name} = item.dataset;
    const qty = Number.parseInt(item.querySelector('.item-qty').value, 10);
    if (!Number.isInteger(qty) || qty < 1) return;
    const existing = selected.find(entry => entry.type === type && entry.name === name);
    if (existing) existing.qty += qty;
    else selected.push({type, name, qty});
    render();
  });
  form.addEventListener('submit', event => {
    if (selected.length) return;
    event.preventDefault();
    alert('Add at least one component or tool before submitting.');
  });
})();
