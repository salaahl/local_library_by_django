document
	.querySelector('.search-bar')
	.addEventListener('input', (e) => {
		e.preventDefault();

		let $ = (id) => {
			return document.querySelector(id);
		};

    $('.search-results').innerHTML = '';

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
        if(result != '') {
          $('.search-results').innerHTML =
          `<table class="table table-striped">
            <thead>
              <tr>
                <th scope="col">N°</th>
                <th scope="col">Titre</th>
                <th scope="col">Auteur</th>
              </tr>
            </thead>
            <tbody class="table-body">
            </tbody>
          </table>`
        }
        
        result.books.forEach(book => {
          $('.table-body').innerHTML +=
            '<tr>' +
              '<th scope="row">' + book['id'] + '</th>' +
              '<td><a href="#">' + book['title'] + '</a></td>' +
              '<td><a href="#">' + book['author'] + '</a></td>' +
            '</tr>'
        })
			})
			.catch((error) => {
				console.log(error.message)
				alert(
					'Erreur.'
				);
			});
	});