function fillFilmlist() {
    fetch('/lab7/rest-api/films/')
        .then(function (data) {
            return data.json();
        })
        .then(function (films) {
            console.log('Получены фильмы:', films); // Для отладки
            let tbody = document.getElementById('film-list');
            tbody.innerHTML = '';
            
            if (!films || films.length === 0) {
                console.log('Список фильмов пуст');
                return;
            }
            
            for(let i = 0; i < films.length; i++) {
                let tr = document.createElement('tr');
                let tdTitle = document.createElement('td');
                let tdTitleRus = document.createElement('td');
                let tdYear = document.createElement('td');
                let tdActions = document.createElement('td');

                // Исправленная строка:
                tdTitle.innerText = films[i].title == films[i].title_ru ? '' : films[i].title;
                tdTitleRus.innerText = films[i].title_ru;
                tdYear.innerText = films[i].year;

                let editButton = document.createElement('button');
                editButton.innerText = 'редактировать';

                let delButton = document.createElement('button');
                delButton.innerText = 'удалить';
                delButton.onclick = function() {
                    deleteFilm(i, films[i].title_ru);
                };

                tdActions.append(editButton);
                tdActions.append(delButton);

                tr.append(tdTitle);
                tr.append(tdTitleRus);
                tr.append(tdYear);
                tr.append(tdActions);

                tbody.append(tr);
            }
        })
        .catch(function (error) {
            console.error('Ошибка при загрузке фильмов:', error);
        });
}

function deleteFilm(id, title) {
    if(!confirm(`Вы точно хотите удалить фильм "${title}"?`))
        return;

    fetch(`/lab7/rest-api/films/${id}`, {method: 'DELETE'})
        .then(function (response) {
            if (response.status === 204) {
                fillFilmList();
            } else {
                console.error('Ошибка при удалении фильма');
            }
        })
        .catch(function (error) {
            console.error('Ошибка:', error);
        });
}

function showModal() {
    document.querySelector('div.modal').style.display = 'block';
}

function hideModal() {
    document.querySelector('div.modal').style.display = 'none';
}

function cancel() {
    hideModal();
}

function addFilm() {
    document.getElementById('id').value = "";
    document.getElementById('title').value = "";
    document.getElementById('title.ru').value = "";
    document.getElementById('year').value = "";
    document.getElementById('description').value = "";
    showModal();
}

function sendFilm() {
    const film = {
        title: document.getElementById('title').value,
        title_ru: document.getElementById('title.ru').value,
        year: document.getElementById('year').value,
        description: document.getElementById('description').value
    };

    const url = '/lab7/rest-api/films/';
    const method = 'POST';

    fetch(url, {
        method: method,
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(film)
    })
    .then(function(response) {
        if (response.ok) {
            fillFilmList();
            hideModal();
        } else {
            console.error('Ошибка при сохранении фильма');
        }
    })
    .catch(function(error) {
        console.error('Ошибка:', error);
    });
}