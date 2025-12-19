// Глобальные переменные
let currentFilms = [];

// Функция для обновления счетчика символов
function updateDescriptionCounter() {
    const textarea = document.getElementById('description');
    const charCounter = document.getElementById('char-counter');
    const length = textarea.value.length;
    
    charCounter.textContent = `${length}/2000 символов`;
    
    if (length > 2000) {
        charCounter.classList.add('warning');
        charCounter.innerHTML = `<span style="color: #e74c3c;">${length}/2000 символов (превышено!)</span>`;
    } else if (length > 1900) {
        charCounter.classList.add('warning');
        charCounter.innerHTML = `<span style="color: #f39c12;">${length}/2000 символов</span>`;
    } else {
        charCounter.classList.remove('warning');
    }
}

// Функция для загрузки и отображения списка фильмов
function fillFilmlist() {
    fetch('/lab7/rest-api/films/')
        .then(function(data) {
            if (!data.ok) {
                throw new Error('Ошибка сети');
            }
            return data.json();
        })
        .then(function(films) {
            currentFilms = films;
            let tbody = document.getElementById('film-list');
            let emptyMessage = document.getElementById('empty-message');
            
            // Очищаем таблицу
            tbody.innerHTML = '';
            
            if (!films || films.length === 0) {
                // Показываем сообщение об отсутствии фильмов
                tbody.style.display = 'none';
                emptyMessage.style.display = 'block';
                return;
            }
            
            // Скрываем сообщение об отсутствии фильмов
            tbody.style.display = '';
            emptyMessage.style.display = 'none';
            
            // Заполняем таблицу
            for(let i = 0; i < films.length; i++) {
                let tr = document.createElement('tr');
                
                // Русское название
                let tdTitleRus = document.createElement('td');
                tdTitleRus.textContent = films[i].title_ru;
                
                // Оригинальное название
                let tdTitle = document.createElement('td');
                let originalTitle = films[i].title;
                
                if (originalTitle && originalTitle !== films[i].title_ru) {
                    let titleSpan = document.createElement('span');
                    titleSpan.className = 'original-title';
                    titleSpan.textContent = originalTitle;
                    tdTitle.appendChild(titleSpan);
                } else {
                    tdTitle.textContent = '—';
                    tdTitle.style.color = '#999';
                }
                
                // Год
                let tdYear = document.createElement('td');
                tdYear.textContent = films[i].year;
                
                // Действия
                let tdActions = document.createElement('td');
                
                let actionButtons = document.createElement('div');
                actionButtons.className = 'action-buttons';
                
                let editButton = document.createElement('button');
                editButton.className = 'edit-btn';
                editButton.textContent = '✏️ Редактировать';
                editButton.onclick = (function(id) {
                    return function() {
                        editFilm(id);
                    };
                })(films[i].id);
                
                let delButton = document.createElement('button');
                delButton.className = 'delete-btn';
                delButton.textContent = '🗑️ Удалить';
                delButton.onclick = (function(id, title) {
                    return function() {
                        deleteFilm(id, title);
                    };
                })(films[i].id, films[i].title_ru);
                
                actionButtons.appendChild(editButton);
                actionButtons.appendChild(delButton);
                tdActions.appendChild(actionButtons);
                
                tr.appendChild(tdTitleRus);
                tr.appendChild(tdTitle);
                tr.appendChild(tdYear);
                tr.appendChild(tdActions);
                
                tbody.appendChild(tr);
            }
        })
        .catch(function(error) {
            console.error('Ошибка при загрузке фильмов:', error);
            showError('Не удалось загрузить список фильмов. Пожалуйста, обновите страницу.');
        });
}

// Функция для отображения ошибок
function showError(message) {
    alert(message);
}

// Функция удаления фильма
function deleteFilm(id, title) {
    if (!confirm(`Вы точно хотите удалить фильм "${title}"?`)) {
        return;
    }
    
    // Показываем индикатор загрузки
    const deleteBtn = event.target;
    const originalText = deleteBtn.textContent;
    deleteBtn.textContent = 'Удаление...';
    deleteBtn.disabled = true;
    
    fetch(`/lab7/rest-api/films/${id}`, {
        method: 'DELETE'
    })
    .then(function(response) {
        if (response.status === 204) {
            // Успешное удаление
            showSuccess('Фильм успешно удален!');
            return fillFilmlist();
        } else if (response.status === 404) {
            return response.json().then(function(error) {
                throw new Error(error.error || 'Фильм не найден');
            });
        } else {
            throw new Error('Ошибка при удалении фильма');
        }
    })
    .then(function() {
        // Скрываем индикатор загрузки
        deleteBtn.textContent = originalText;
        deleteBtn.disabled = false;
    })
    .catch(function(error) {
        console.error('Ошибка при удалении фильма:', error);
        showError(`Ошибка при удалении: ${error.message}`);
        // Восстанавливаем кнопку
        deleteBtn.textContent = originalText;
        deleteBtn.disabled = false;
    });
}

// Функция для отображения успешных сообщений
function showSuccess(message) {
    // Можно заменить на более красивый toast-уведомление
    alert(message);
}

// Функции для работы с модальным окном
function showModal() {
    document.getElementById('film-modal').style.display = 'block';
    // Очищаем все сообщения об ошибках
    document.querySelectorAll('.error-message').forEach(function(el) {
        el.textContent = '';
    });
}

function hideModal() {
    document.getElementById('film-modal').style.display = 'none';
}

function cancel() {
    hideModal();
    resetForm();
}

function resetForm() {
    document.getElementById('film-form').reset();
    document.getElementById('id').value = '';
    document.getElementById('modal-title').textContent = 'Добавить фильм';
    document.getElementById('save-btn').textContent = 'Сохранить';
    updateDescriptionCounter();
}

// Функция добавления нового фильма
function addFilm() {
    resetForm();
    showModal();
}

// Функция редактирования фильма
function editFilm(id) {
    // Показываем индикатор загрузки
    const modalTitle = document.getElementById('modal-title');
    modalTitle.textContent = 'Загрузка...';
    
    fetch(`/lab7/rest-api/films/${id}`)
    .then(function(response) {
        if (!response.ok) {
            throw new Error('Ошибка загрузки фильма');
        }
        return response.json();
    })
    .then(function(film) {
        document.getElementById('id').value = film.id;
        document.getElementById('title.ru').value = film.title_ru;
        document.getElementById('title').value = film.title;
        document.getElementById('year').value = film.year;
        document.getElementById('description').value = film.description;
        
        // Обновляем UI
        document.getElementById('modal-title').textContent = 'Редактировать фильм';
        document.getElementById('save-btn').textContent = 'Обновить';
        updateDescriptionCounter();
        
        showModal();
    })
    .catch(function(error) {
        console.error('Ошибка при загрузке фильма:', error);
        showError('Не удалось загрузить данные фильма. Пожалуйста, попробуйте еще раз.');
    });
}

// Функция отправки формы
function sendFilm() {
    const id = document.getElementById('id').value;
    const film = {
        title: document.getElementById('title').value.trim(),
        title_ru: document.getElementById('title.ru').value.trim(),
        year: document.getElementById('year').value.trim(),
        description: document.getElementById('description').value.trim()
    };
    
    // Быстрая валидация на клиенте
    if (!film.title_ru) {
        showError('Пожалуйста, введите название фильма на русском');
        document.getElementById('title.ru').focus();
        return;
    }
    
    if (!film.year) {
        showError('Пожалуйста, введите год выпуска');
        document.getElementById('year').focus();
        return;
    }
    
    if (!film.description) {
        showError('Пожалуйста, введите описание фильма');
        document.getElementById('description').focus();
        return;
    }
    
    if (film.description.length > 2000) {
        showError('Описание не должно превышать 2000 символов');
        document.getElementById('description').focus();
        return;
    }
    
    let url, method;
    
    if (!id) {
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
        el.textContent = '';
    });
    
    // Показываем индикатор загрузки
    const saveBtn = document.getElementById('save-btn');
    const originalText = saveBtn.textContent;
    saveBtn.textContent = 'Сохранение...';
    saveBtn.disabled = true;
    
    fetch(url, {
        method: method,
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(film)
    })
    .then(function(response) {
        if (response.ok) {
            return response.json();
        } else {
            return response.json().then(function(errors) {
                throw errors;
            });
        }
    })
    .then(function(result) {
        if (method === 'POST') {
            showSuccess('Фильм успешно добавлен!');
        } else {
            showSuccess('Фильм успешно обновлен!');
        }
        
        // Закрываем модальное окно и обновляем список
        hideModal();
        resetForm();
        return fillFilmlist();
    })
    .then(function() {
        // Восстанавливаем кнопку
        saveBtn.textContent = originalText;
        saveBtn.disabled = false;
    })
    .catch(function(errors) {
        if (typeof errors === 'object' && errors !== null) {
            // Отображаем ошибки валидации
            for (let field in errors) {
                let errorElement = document.getElementById(field + '.error');
                if (errorElement) {
                    errorElement.textContent = errors[field];
                }
            }
        } else {
            showError('Произошла ошибка при сохранении фильма. Пожалуйста, попробуйте еще раз.');
        }
        
        // Восстанавливаем кнопку
        saveBtn.textContent = originalText;
        saveBtn.disabled = false;
    });
}

// Обработка нажатия Escape для закрытия модального окна
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        cancel();
    }
});

// Обработка клика вне модального окна для его закрытия
window.addEventListener('click', function(event) {
    const modal = document.getElementById('film-modal');
    if (event.target === modal) {
        cancel();
    }
});