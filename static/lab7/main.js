function fillFilmlist() {
    return fetch('/lab7/rest-api/films/')
        .then(function (data) {
            return data.json();
        })
        .then(function (films) {
            console.log('Получены фильмы:', films);
            let tbody = document.getElementById('film-list');
            tbody.innerHTML = '';
            
            if (!films || films.length === 0) {
                console.log('Список фильмов пуст');
                let tr = document.createElement('tr');
                let td = document.createElement('td');
                td.colSpan = 4;
                td.innerText = 'Нет фильмов для отображения';
                tr.append(td);
                tbody.append(tr);
                return;
            }
            
            for(let i = 0; i < films.length; i++) {
                let tr = document.createElement('tr');
                let tdTitle = document.createElement('td');
                let tdTitleRus = document.createElement('td');
                let tdYear = document.createElement('td');
                let tdActions = document.createElement('td');

                tdTitle.innerText = films[i].title == films[i].title_ru ? '' : films[i].title;
                tdTitleRus.innerText = films[i].title_ru;
                tdYear.innerText = films[i].year;

                let editButton = document.createElement('button');
                editButton.innerText = 'редактировать';
                editButton.onclick = function() {
                    editFilm(i);
                };

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
                return fillFilmlist();  // Исправлено: возвращаем Promise
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
    // Очищаем сообщение об ошибке при открытии модального окна
    document.getElementById('description.error').innerText = '';
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

function editFilm(id) {
    fetch(`/lab7/rest-api/films/${id}`)
    .then(function (data) {
        return data.json();
    })
    .then(function (film) {
        document.getElementById('id').value = id;
        document.getElementById('title').value = film.title;
        document.getElementById('title.ru').value = film.title_ru;
        document.getElementById('year').value = film.year;
        document.getElementById('description').value = film.description;
        showModal();
    })
    .catch(function(error) {
        console.error('Ошибка при загрузке фильма:', error);
    });
}

function sendFilm() {
    const id = document.getElementById('id').value;
    const film = {
        title: document.getElementById('title').value,
        title_ru: document.getElementById('title.ru').value,
        year: document.getElementById('year').value,
        description: document.getElementById('description').value
    };
    
    let url, method;
    
    if (id === '') {
        // Добавление нового фильма
        url = '/lab7/rest-api/films/';
        method = 'POST';
    } else {
        // Редактирование существующего фильма
        url = `/lab7/rest-api/films/${id}`;
        method = 'PUT';
    }
    
    // Очищаем предыдущие ошибки
    document.getElementById('description.error').innerText = '';
    
    fetch(url, {
        method: method,
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(film)
    })
    .then(function(resp) {
        if(resp.ok) {
            // Возвращаем Promise, который выполнится после обновления списка
            return fillFilmlist().then(function() {
                hideModal();
            });
        } else {
            return resp.json();
        }
    })
    .then(function(errors) {
        if(errors && errors.description) {
            document.getElementById('description.error').innerText = errors.description;
        }
    })
    .catch(function(error) {
        console.error('Ошибка:', error);
    });
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    fillFilmlist();
});