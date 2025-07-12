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
        $('tbody').style.opacity = '1';
        result.books.forEach(book => {
            $('tbody').innerHTML +=
              '<tr class="table-row">' +
                '<td><a href="/catalog/book/' + book['id'] + '">' + book['title'] + '</a></td>' +
                '<td><a href="/catalog/author/' + book['author_id'] + '">' + book['author'] + '</a></td>' +
              '</tr>';
          })
      })
      .catch((error) => {
        console.log(error)
        alert(
          'Erreur.'
        )
      })
  	})
  });