document.addEventListener("DOMContentLoaded", () => {
    let timer;
    
    document
    .querySelector('.search-bar')
    .addEventListener('input', (e) => {
        e.preventDefault();
    
        clearTimeout(timer);
    
        let $ = (id) => {
            return document.querySelector(id);
        };
    
        let body = document.querySelectorAll("#page-container > #search-container ~ *");
        console.log(body)
    
        timer = setTimeout(function() {
            if ($('[name=search]').value.length > 1) {
                body.forEach(content => {
                    content.style.filter = 'blur(5px) opacity(0)';
                })
    
                $('#search-results').innerHTML = '';
                $('#search-results').style.opacity = '0';
    
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
                      $('#search-results').style.opacity = '1';
                        if (result.books != '') {
                            $('#search-results').innerHTML =
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
                                $('tbody').innerHTML +=
                                    '<tr class="table-row">' +
                                    '<td><a href="/catalog/book/' + book['id'] + '">' + book['title'] + '</a></td>' +
                                    '<td><a href="/catalog/author/' + book['author_id'] + '">' + book['author'] + 
                                  '</a></td>' + '</tr>';
                            })
                        } else {
                          $('#search-results').innerHTML = 'Aucun résultat';
                        }
                    })
                    .catch((error) => {
                        console.log(error.message)
                        alert(
                            'Erreur.'
                        );
                    });
            } else {
                body.forEach(content => {
                    content.style.filter = 'blur(0px) opacity(1)';
                })
                $('#search-results').innerHTML = '';
            }
        }, 600);
    });
});
