document.querySelectorAll('.search-filter').forEach(filter => {
  filter.addEventListener('click', (e) => {
    e.preventDefault();

    let $ = (id) => {
      return document.querySelector(id);
    };

    $('tbody').innerHTML = '';
    $('tbody').style.opacity = '0';

    let formData = new FormData();
    formData.append('filter', filter.innerHTML);

    let csrfTokenValue = document.querySelector('[name=csrfmiddlewaretoken]').value;

    const request = new Request('/catalog/books/', {
      method: 'POST',
      body: formData,
      headers: {
        'X-CSRFToken': csrfTokenValue
      }
    })
    fetch(request)
      .then(response => response.json())
      .then(result => {
        console.log(result)
        $('tbody').style.opacity = '1';
      })
      .catch((error) => {
        console.log(error)
        alert(
          'Erreur.'
        )
      })
  	})
  });