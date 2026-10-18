document.addEventListener('change', event => { if (event.target.matches('[data-auto-submit]')) event.target.form?.requestSubmit(); });
