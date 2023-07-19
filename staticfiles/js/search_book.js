document
	.querySelector('.search-bar')
	.addEventListener('input', (e) => {
		e.preventDefault();

		let $ = (id) => {
			return document.querySelector(id);
		};

    $('.search-results').innerHTML = '';
    $('.search-results').style.opacity = '0';

		let formData = new FormData();
		formData.append('book', $("[name=search]").value);

		let csrfTokenValue = document.querySelector('[name=csrfmiddlewaretoken]').value;

		const request = new Request('/catalog/', {
			method: 'POST',
			body: formData,
			headers: {
				'X-CSRFToken': csrfTokenValue
			}
		});
		fetch(request)
			.then(response => response.json())
			.then(result => {
        if(result.books != '') {
          $('.search-results').style.opacity = '1';
          $('.search-results').innerHTML =
          `<table class="table table-striped">
            <thead>
              <tr class="table-row">
                <th scope="col">Titre</th>
                <th scope="col">Auteur</th>
              </tr>
            </thead>
            <tbody class="table-body">
            </tbody>
          </table>`
        
          result.books.forEach(book => {
            $('.table-body').innerHTML +=
              '<tr class="table-row">' +
                '<td><a href="/catalog/book/' + book['id'] + '">' + book['title'] + '</a></td>' +
                '<td><a href="/catalog/author/' + book['author_id'] + '">' + book['author'] + '</a></td>' +
              '</tr>';
          })
        }
			})
			.catch((error) => {
				console.log(error.message)
				alert(
					'Erreur.'
				);
			});
	});