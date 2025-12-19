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