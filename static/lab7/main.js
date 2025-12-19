function fillFilmlist() {
    return fetch('/lab7/rest-api/films/')
        .then(function (data) {
            return data.json();
        })
        .then(function (films) {
            let tbody = document.getElementById('film-list');
            tbody.innerHTML = '';
            
            if (!films || films.length === 0) {
                let tr = document.createElement('tr');
                let td = document.createElement('td');
                td.colSpan = 4;
                td.innerText = 'Нет фильмов для отображения';
                td.style.textAlign = 'center';
                td.style.padding = '20px';
                tr.append(td);
                tbody.append(tr);
                return;
            }
            
            for(let i = 0; i < films.length; i++) {
                let tr = document.createElement('tr');
                
                // Русское название
                let tdTitleRus = document.createElement('td');
                tdTitleRus.innerText = films[i].title_ru;
                
                // Оригинальное название (курсивом и в скобках, если отличается от русского)
                let tdTitle = document.createElement('td');
                let originalTitle = films[i].title;
                
                if (originalTitle && originalTitle !== films[i].title_ru) {
                    let titleSpan = document.createElement('span');
                    titleSpan.className = 'original-title';
                    titleSpan.innerText = `(${originalTitle})`;
                    tdTitle.appendChild(titleSpan);
                } else {
                    tdTitle.innerText = '-';
                    tdTitle.style.color = '#999';
                }
                
                // Год
                let tdYear = document.createElement('td');
                tdYear.innerText = films[i].year;
                
                // Действия
                let tdActions = document.createElement('td');
                tdActions.style.whiteSpace = 'nowrap';

                let editButton = document.createElement('button');
                editButton.innerText = '✏️';
                editButton.title = 'Редактировать';
                editButton.onclick = function() {
                    editFilm(i);
                };

                let delButton = document.createElement('button');
                delButton.innerText = '🗑️';
                delButton.title = 'Удалить';
                delButton.onclick = function() {
                    deleteFilm(i, films[i].title_ru);
                };

                tdActions.append(editButton);
                tdActions.append(delButton);

                tr.append(tdTitleRus);
                tr.append(tdTitle);
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
                return fillFilmlist();
            } else {
                return response.json().then(function(error) {
                    console.error('Ошибка при удалении фильма:', error.error);
                    alert(`Ошибка: ${error.error}`);
                });
            }
        })
        .catch(function (error) {
            console.error('Ошибка:', error);
            alert('Ошибка сети при удалении фильма');
        });
}

function showModal() {
    document.querySelector('div.modal').style.display = 'block';
    // Очищаем все сообщения об ошибках
    document.querySelectorAll('.error-message').forEach(function(el) {
        el.innerText = '';
    });
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
        alert('Ошибка при загрузке данных фильма');
    });
}

function sendFilm() {
    const id = document.getElementById('id').value;
    const film = {
        title: document.getElementById('title').value.trim(),
        title_ru: document.getElementById('title.ru').value.trim(),
        year: document.getElementById('year').value.trim(),
        description: document.getElementById('description').value.trim()
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
    document.querySelectorAll('.error-message').forEach(function(el) {
        el.innerText = '';
    });
    
    fetch(url, {
        method: method,
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(film)
    })
    .then(function(resp) {
        if(resp.ok) {
            return fillFilmlist().then(function() {
                hideModal();
            });
        } else {
            return resp.json();
        }
    })
    .then(function(errors) {
        if(errors) {
            // Отображаем ошибки для соответствующих полей
            for(let field in errors) {
                let errorElement = document.getElementById(field + '.error');
                if(errorElement) {
                    errorElement.innerText = errors[field];
                } else {
                    console.error(`Ошибка для поля ${field}: ${errors[field]}`);
                }
            }
        }
    })
    .catch(function(error) {
        console.error('Ошибка:', error);
        alert('Ошибка сети при сохранении фильма');
    });
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    fillFilmlist();
    
    // Добавляем ID для кнопки добавления фильма
    document.querySelector('button[onclick="addFilm()"]').id = 'add-film-btn';
});