// tile/pager/static/pager/this/init.js
// Author: shmakovpn <shmakovpn@yandex.ru>
// date: 2019-12-26, 2020-02-10

// переводит приложение в режим наличия несохраненных изменений
// 2019-12-25
function setModifiedMode() {
    $('#save-changes').show();  // показываем кнопку "Сохранить"
    $('#cancel-changes').show();  // показываем кнопку "Отменить"
    modifiedMode = true;  // устанавливаем флаг наличие несохраненных изменений
}

// возвращает true в случае локальной версии
// 2020-05-20
function isLocal() {
    if($('#local-flag').length) {
        console.log('isLocal=true')
        return true;
    }
    console.log('isLocal=false')
    return false;
}

// возвращает словарь с данными о плитке el
// 2019-12-25,2020-02-06, 2020-02-10
function getTileData(el) {
    try {
        let data = $(el).data('_gridstack_node');
        let type = undefined;
        let url_pattern = undefined;
        if(data.el.hasClass('pageWidget')) {
            type = 'page';
        } else if(data.el.hasClass('linkWidget')) {
            type = 'link';
            url_pattern = $(el).find('.url_pattern').text();
        } else if(data.el.hasClass('stubWidget')) {
            type = 'stub';
        }
        let description = $(el).find('.tileDescription').text();
        let bgcolor = $(el).find('.tileBgcolor').text().replace('#', '');
        let borderRightWidth = parseInt($(el).find('.tileBorderRightWidth').text());
        if(Number.isNaN(borderRightWidth))borderRightWidth=1;
        let borderLeftWidth = parseInt($(el).find('.tileBorderLeftWidth').text());
        if(Number.isNaN(borderLeftWidth))borderLeftWidth=1;
        let borderTopWidth = parseInt($(el).find('.tileBorderTopWidth').text());
        if(Number.isNaN(borderTopWidth))borderTopWidth=1;
        let borderBottomWidth = parseInt($(el).find('.tileBorderBottomWidth').text());
        if(Number.isNaN(borderBottomWidth))borderBottomWidth=1;
        let borderRightColor = $(el).find('.tileBorderRightColor').text().replace('#', '');
        let borderLeftColor = $(el).find('.tileBorderLeftColor').text().replace('#', '');
        let borderTopColor = $(el).find('.tileBorderTopColor').text().replace('#', '');
        let borderBottomColor = $(el).find('.tileBorderBottomColor').text().replace('#', '');
        let titleFontSize = parseInt($(el).find('.tileTitleFontSize').text());
        if(Number.isNaN(titleFontSize))titleFontSize=12;
        let titleFontColor = $(el).find('.tileTitleFontColor').text().replace('#','');
        let owner = $(el).find('.tileOwner').text();
        return {
            x: data.x,
            y: data.y,
            width: data.width,
            height: data.height,
            id: data.id,
            new: data.id === undefined,
            type: type,
            title: $(el).find('.tileTitle').text(),
            url_pattern: url_pattern,
            path: $(el).find('.tilePath').text(),
            description: description,
            bgcolor: bgcolor,
            border_right_width: borderRightWidth,
            border_left_width: borderLeftWidth,
            border_top_width: borderTopWidth,
            border_bottom_width: borderBottomWidth,
            border_right_color: borderRightColor,
            border_left_color: borderLeftColor,
            border_top_color: borderTopColor,
            border_bottom_color: borderBottomColor,
            title_font_size: titleFontSize,
            title_font_color: titleFontColor,
            owner: owner
        };
    } catch (e) {
        console.log("An error has occurred in getTileData: "+e.toString());
        return undefined;
    }
}

// возвращает json-строку кратко описывающую основные свойства плитки
// 2019-12-25
function tileToString(el) {
    let data = getTileData(el);
    if(data !== undefined) {
        return JSON.stringify(data);
    }
    console.log("An error has occurred in tileToSting: could not retrieve data from element");
    return undefined;
}

// возвращает true для вновь добавленной плитки, и false для плитки загруженной из базы
// 2019-12-25
function isNewTile(el) {
    let data = getTileData(el);
    if(data !== undefined) {
        return data.new;
    }
    console.log("An error has occurred in isNewTile: could not retrieve data from element");
    return undefined;
}

// возвращает id плитки, если она была сохранена в базе, или undefined для новой плитки
// 2019-12-25
function getTileId(el) {
    let data = getTileData(el);
    if(data !== undefined) {
        return data.id;  // возвращает id плитки, если она была сохранена в базе, или undefined для новой плитки
    }
    console.log("An error has occurred in getTileData: could not retrieve data from element");
    return undefined;
}

// возвращает тип плитки, page или link
// 2019-12-25
function getTileType(el) {
    let data = getTileData(el);
    if(data !== undefined) {
        return data.type;
    }
    console.log("An error has occurred in getTileType: could not retrieve data from element");
    return undefined;
}

// возвращает путь к странице на которой находится плитка
// 2019-12-26
function getTilePath(el) {
    let data = getTileData(el);
    if(data !== undefined) {
        return data.path;
    }
    console.log("An error has occurred in getTilePath: could not retrieve data from element");
    return undefined;
}

// возвращает подробное описание плитки
// 2019-12-30
function getTileDescripiton(el) {
    let data = getTileData(el);
    if(data !== undefined) {
        return data.description;
    }
    console.log("An error has occurred in getTileDescription: could not retrieve data from element");
    return undefined;
}

// возвращает цвет фона плитки
// 2020-02-06
function getTileBgcolor(el) {
    let data = getTileData(el);
    if(data !== undefined) {
        return data.bgcolor;
    }
    console.log("An error has occurred in getTileBgcolor: could not retrieve data from element");
    return undefined;
}

// помещает плитку в массив плиток для удаления, если плитка не новая (т.е. была загружена из базы)
// проверяет что плитка ранее не добавлена в массив для удаления плиток
// возвращает true если плитка была помещена в массив плиток для удаления
// 2019-12-25
function pushTileToDelete(el) {
    if(isNewTile(el) === false) {
        for(let i in tilesToDeleteArr) {
            if(getTileType(el)===tilesToDeleteArr[i].type && getTileId(el)===tilesToDeleteArr[i].id) {
                return false;
            }
        }
        tilesToDeleteArr.push({
            id: getTileId(el),
            type: getTileType(el),
            path: getTilePath(el),
        });
        return true;
    }
    return false;
}

// массив плиток для удаления
// 2019-12-25
let tilesToDeleteArr = [];

// jQuery объект элемента #advanced-grid
// 2019-12-25
let gridStackObj = undefined;

// jQuery объект текущей выбранной плитки
// служит для сохранения объекта плитки для редактирования ее параметров в диалоговых окнах
// 2019-12-26
let selectedTile = undefined;

// флаг наличие не сохраненных изменений
// 2019-12-26
let modifiedMode = false;

// обработчик собития "сохранить изменения"
// 2019-12-25
function onSaveChanges(event) {
    event.preventDefault();
    // массив информации о всех плитках
    let data = {
        'insert': [],
        'update': [],
        'delete': tilesToDeleteArr,
    };
    $('#advanced-grid > .grid-stack-item').map(function (i, el) {
        if(isNewTile(el)) {
            data.insert.push(getTileData(el));
        } else {
            data.update.push(getTileData(el));
        }
    });

    // console.log(data);

    $.ajax({
        //url
        cache: false,
        type: 'POST',
        contentType : 'application/json; charset=utf-8',
        headers: {'X-CSRFToken': $('main input[name=csrfmiddlewaretoken]').val()},
        dateType: 'text',
        data: JSON.stringify(data),
        error: function (jqXHR, textStatus, errorThrown) {
            console.log('onSaveChanges ajax error');
            console.log(jqXHR);
            console.log(textStatus);
            console.log(errorThrown);
            alert('Ошибка сохранения ajax error: '+textStatus)
        },
        success: function (data, textStatus, jqXHR) {
            try {
                let responseJSON = JSON.parse(data);
                if(responseJSON.success === true) {
                    location.reload();  // перезагружаем страницу после успешного сохранения
                } else {
                    console.log('onSaveChanges success === false');
                    alert('Ошибка сохранения: '+responseJSON.error);
                }
            } catch (e) {
                console.log('onSaveChanges ajax error: data could not be parsed as JSON');
                alert('Ошибка сохранения: ответ сервера не может быть обработан как JSON');
            }
        }
    });
}

// обработчик события "отменить изменения"
// 2019-12-25
function onCancelChanges(event) {
    event.preventDefault();
    if(confirm('Несохраненные изменения будут утеряны!')){location.reload();}
}

// открывает диалоговое окно редактирования плитки страницы
// 2019-12-25
function showPageEditDialog(tile) {
    selectedTile = $(tile);  // запоминаем текущую выбранную плитку
    let title = selectedTile.find('.tileTitle').text();  // берем текст заголовка из плитки
    let description = selectedTile.find('.tileDescription').text();  // берем текст подробного описания из плитки
    let bgcolor = selectedTile.find('.tileBgcolor').text();  // берем цвет фона плитки из плитки
    let borderRightWidth = parseInt(selectedTile.find('.tileBorderRightWidth').text());  // берем ширину правой границы рамки из плитки
    if(Number.isNaN(borderRightWidth))borderRightWidth=1;
    let borderLeftWidth = parseInt(selectedTile.find('.tileBorderLeftWidth').text());  // берем ширину левой границы рамки из плитки
    if(Number.isNaN(borderLeftWidth))borderLeftWidth=1;
    let borderTopWidth = parseInt(selectedTile.find('.tileBorderTopWidth').text());  // берем ширину верхней границы рамки из плитки
    if(Number.isNaN(borderTopWidth))borderTopWidth=1;
    let borderBottomWidth = parseInt(selectedTile.find('.tileBorderBottomWidth').text());  // берем ширину нижней границы рамки из плитки
    if(Number.isNaN(borderBottomWidth))borderBottomWidth=1;
    let titleFontSize = parseInt(selectedTile.find('.tileTitleFontSize').text());  // берем размер шрифта заголовка плитки из плитки
    if(Number.isNaN(titleFontSize))titleFontSize=12;
    let borderRightColor = selectedTile.find('.tileBorderRightColor').text();  // берем цвет правой границы рамки из плитки
    let borderLeftColor = selectedTile.find('.tileBorderLeftColor').text();  // берем цвет левой границы рамки из плитки
    let borderTopColor = selectedTile.find('.tileBorderTopColor').text();  // берем цвет верхней границы рамки из плитки
    let borderBottomColor = selectedTile.find('.tileBorderBottomColor').text();  // берем цвет нижней границы рамки из плитки
    let titleFontColor = selectedTile.find('.tileTitleFontColor').text();  // берем цвет заголовка плитки из плитки
    $('#editPageForm-title').val(title);  // помещаем текст заголовка плитки в поле диалогового окна
    $('#editPageForm-description').val(description);  // помещаем текст подробного описания плитки в поле диалогового окна
    if(bgcolor==='') {
        $('#editPageForm-bgcolor').val('#6cad84');  // если для плитки цвет не указан, устанавливаем цвет по умолчанию
    } else {
        $('#editPageForm-bgcolor').val('#'+bgcolor.replace('#',''));
    }
    $('#editPageForm-border-right-width').val(borderRightWidth);
    $('#editPageForm-border-left-width').val(borderLeftWidth);
    $('#editPageForm-border-top-width').val(borderTopWidth);
    $('#editPageForm-border-bottom-width').val(borderBottomWidth);
    $('#editPageForm-title-font-size').val(titleFontSize);
    if(borderRightColor==='') {
        $('#editPageForm-border-right-color').val('#000000');  // если цвет правой границы плитки не указан, устанавливаем значение по умолчанию
    } else {
        $('#editPageForm-border-right-color').val('#'+borderRightColor.replace('#',''));
    }
    if(borderLeftColor==='') {
        $('#editPageForm-border-left-color').val('#000000');  // если цвет левой границы плитки не указан, устанавливаем значение по умолчанию
    } else {
        $('#editPageForm-border-left-color').val('#'+borderLeftColor.replace('#',''));
    }
    if(borderTopColor==='') {
        $('#editPageForm-border-top-color').val('#000000');  // если цвет верхней границы плитки не указан, устанавливаем значение по умолчанию
    } else {
        $('#editPageForm-border-top-color').val('#'+borderTopColor.replace('#',''));
    }
    if(borderBottomColor==='') {
        $('#editPageForm-border-bottom-color').val('#000000');  // если цвет нижней границы плитки не указан, устанавливаем значение по умолчанию
    } else {
        $('#editPageForm-border-bottom-color').val('#'+borderBottomColor.replace('#',''));
    }
    if(titleFontColor==='') {
        $('#editPageForm-title-font-color').val('#ffffff');  // если цвет заголовка плитки не указан, устанавливаем значение по умолчанию
    } else {
        $('#editPageForm-title-font-color').val('#'+titleFontColor.replace('#',''));
    }

    $('#editPageFormCommitBtn').off('click');  // удаляем обработчик клика кнопки "применить" диалогового окна (если таковой был)
    // дабавляем новый обработчик клика кнопки "применить" диалогового окна
    $('#editPageFormCommitBtn').click(function (event) {
        let newTitle = $('#editPageForm-title').val();  // берем текст заголовка из диалогового окна
        let newDescription = $('#editPageForm-description').val();  // берем текст подробного описания из плитки
        let newBgcolor = $('#editPageForm-bgcolor').val().replace('#','');  // берем цвет фона плитки из диалогового окна
        let newBorderRightWidth = parseInt($('#editPageForm-border-right-width').val());  // берем ширину правой границы плитки из диалогового окна
        if(Number.isNaN(newBorderRightWidth)) {
            event.preventDefault();  // отменяем действие по умолчанию
            alert('Введено некорректное значение ширины правой границы');
            return;
        }
        let newBorderLeftWidth = parseInt($('#editPageForm-border-left-width').val());  // берем ширину левой границы плитки из диалогового окна
        if(Number.isNaN(newBorderLeftWidth)) {
            event.preventDefault();  // отменяем действие по умолчанию
            alert('Введено некорректное значение ширины левой границы');
            return;
        }
        let newBorderTopWidth = parseInt($('#editPageForm-border-top-width').val());  // берем ширину верхней границы плитки из диалогового окна
        if(Number.isNaN(newBorderTopWidth)) {
            event.preventDefault();  // отменяем действие по умолчанию
            alert('Введено некорректное значение ширины верхней границы');
            return;
        }
        let newBorderBottomWidth = parseInt($('#editPageForm-border-bottom-width').val());  // берем ширину нижней границы плитки из диалогового окна
        if(Number.isNaN(newBorderBottomWidth)) {
            event.preventDefault();  // отменяем действие по умолчанию
            alert('Введено некорректное значение ширины нижней границы');
            return;
        }
        let newTitleFontSize = parseInt($('#editPageForm-title-font-size').val());  // берем размер шрифта заголовка плитки из диалогового окна
        if(Number.isNaN(newTitleFontSize)) {
            event.preventDefault();  // отменяем действие по умолчанию
            alert('Введено некорректное размера шрифта');
            return;
        }
        let newBorderRightColor = $('#editPageForm-border-right-color').val().replace('#','');  // берем цвет правой границы плитки из диалогового окна
        let newBorderLeftColor = $('#editPageForm-border-left-color').val().replace('#','');  // берем цвет левой границы плитки из диалогового окна
        let newBorderTopColor = $('#editPageForm-border-top-color').val().replace('#','');  // берем цвет верхней границы плитки из диалогового окна
        let newBorderBottomColor = $('#editPageForm-border-bottom-color').val().replace('#','');  // берем цвет нижней границы плитки из диалогового окна
        let newTitleFontColor = $('#editPageForm-title-font-color').val().replace('#','');  // берем цвет заголовка плитки из диалогового окна

        if((title !== newTitle) || (description !== newDescription) || (bgcolor !== newBgcolor)
            || (borderRightWidth !== newBorderRightWidth)
            || (borderLeftWidth !== newBorderLeftWidth)
            || (borderTopWidth !== newBorderTopWidth)
            || (borderBottomWidth !== newBorderBottomWidth)
            || (borderRightColor !== newBorderRightColor)
            || (borderLeftColor !== newBorderLeftColor)
            || (borderTopColor !== newBorderTopColor)
            || (borderBottomColor !== newBorderBottomColor)
            || (titleFontSize !== newTitleFontSize)
            || (titleFontColor !== newTitleFontColor)) {
            setModifiedMode();  // активируем в меню кнопки "сохранить" и "отменить"
            selectedTile.find('.tileTitle').text(newTitle);  // меняем заголовок в плитке
            selectedTile.find('.tileDescription').text(newDescription);  // меняем текст подробного описания в плитке
            selectedTile.find('.tileBgcolor').text(newBgcolor);  // меняем цвет фона плитки в плитке
            selectedTile.css('background-color', '#'+newBgcolor);  // перекрашиваем плитку в новый цвет
            selectedTile.find('.tileBorderRightWidth').text(newBorderRightWidth);  // меняем ширину правой границы в плитке
            selectedTile.find('.tileBorderLeftWidth').text(newBorderLeftWidth);  // меняем ширину левой границы в плитке
            selectedTile.find('.tileBorderTopWidth').text(newBorderTopWidth);  // меняем ширину верхней границы в плитке
            selectedTile.find('.tileBorderBottomWidth').text(newBorderBottomWidth);  // меняем ширину нижней границы в плитке
            selectedTile.find('.tileTitleFontSize').text(newTitleFontSize);  // меняем размер шрифта заголовка плитки в плитке
            selectedTile.find('.tileBorderRightColor').text(newBorderRightColor);  // меняем цвет правой границы в плитке
            selectedTile.find('.tileBorderLeftColor').text(newBorderLeftColor);  // меняем цвет левой границы в плитке
            selectedTile.find('.tileBorderTopColor').text(newBorderTopColor);  // меняем цвет верхней границы в плитке
            selectedTile.find('.tileBorderBottomColor').text(newBorderBottomColor);  // меняем цвет нижней границы в плитке
            selectedTile.find('.tileTitleFontColor').text(newTitleFontColor);  // меняем цвет шрифта заголовка плитки в плитке
            selectedTile.css('border-right-width', newBorderRightWidth+'px');  // обновляем ширину правой границы в плитке
            selectedTile.css('border-left-width', newBorderLeftWidth+'px');  // обновляем ширину левой границы в плитке
            selectedTile.css('border-top-width', newBorderTopWidth+'px');  // обновляем ширину верхней границы в плитке
            selectedTile.css('border-bottom-width', newBorderBottomWidth+'px');  // обвновляем ширину нижней границе в плитке
            selectedTile.find('.tileTitle').css('font-size', newTitleFontSize+'px');  // обновляем размер шрифта в плитке
            selectedTile.css('border-right-color','#'+newBorderRightColor);  // перекрашиваем правую границу плитки в новый цвет
            selectedTile.css('border-left-color','#'+newBorderLeftColor);  // перекрашиваем левую границу плитки в новый цвет
            selectedTile.css('border-top-color','#'+newBorderTopColor);  // перекрашиваем верхнюю границу плитки в новый цвет
            selectedTile.css('border-bottom-color','#'+newBorderBottomColor);  // перекрашиваем нижнюю границу плитки в новый цвет
            selectedTile.find('.tileTitle').css('color','#'+newTitleFontColor);  // перекрашиваем заголовок плитки в новый цвет
        }
        $('#editPageForm').modal('hide');  // закрываем диалоговое окно
    });
    $('#editPageForm').modal();  // показываем диалоговое коно редактирования страницы
}

// открывает диалоговое окно редактирования плитки ссылки
// 2019-12-25
function showLinkEditDialog(tile) {
    selectedTile = $(tile);  // запоминаем текущую выбранную плитку
    let title = selectedTile.find('.tileTitle').text();  // берем текст заголовка из плитки
    let description = selectedTile.find('.tileDescription').text();  // берем текст подробного описания из плитки
    let bgcolor = selectedTile.find('.tileBgcolor').text();  // берем цвет фона плитки из плитки
    let borderRightWidth = parseInt(selectedTile.find('.tileBorderRightWidth').text());  // берем ширину правой границы рамки из плитки
    if(Number.isNaN(borderRightWidth))borderRightWidth=1;
    let borderLeftWidth = parseInt(selectedTile.find('.tileBorderLeftWidth').text());  // берем ширину левой границы рамки из плитки
    if(Number.isNaN(borderLeftWidth))borderLeftWidth=1;
    let borderTopWidth = parseInt(selectedTile.find('.tileBorderTopWidth').text());  // берем ширину верхней границы рамки из плитки
    if(Number.isNaN(borderTopWidth))borderTopWidth=1;
    let borderBottomWidth = parseInt(selectedTile.find('.tileBorderBottomWidth').text());  // берем ширину нижней границы рамки из плитки
    if(Number.isNaN(borderBottomWidth))borderBottomWidth=1;
    let titleFontSize = parseInt(selectedTile.find('.tileTitleFontSize').text());  // берем размер шрифта заголовка плитки из плитки
    if(Number.isNaN(titleFontSize))titleFontSize=12;
    let borderRightColor = selectedTile.find('.tileBorderRightColor').text();  // берем цвет правой границы рамки из плитки
    let borderLeftColor = selectedTile.find('.tileBorderLeftColor').text();  // берем цвет левой границы рамки из плитки
    let borderTopColor = selectedTile.find('.tileBorderTopColor').text();  // берем цвет верхней границы рамки из плитки
    let borderBottomColor = selectedTile.find('.tileBorderBottomColor').text();  // берем цвет нижней границы рамки из плитки
    let titleFontColor = selectedTile.find('.tileTitleFontColor').text();  // берем цвет заголовка плитки из плитки
    let urlPattern = selectedTile.find('.url_pattern').text();  // берем адрес ссылки из плитки
    let owner = selectedTile.find('.tileOwner').text();  // берем ответственного за наличие справки в АСФО из плтики
    $('#editLinkForm-title').val(title);  // помещаем текст заголовка плитки в поле диалогового окна
    $('#editLinkForm-description').val(description);  // помещаем текст подробного описания плитки в поле диалогового окна
    if(bgcolor==='') {
        $('#editLinkForm-bgcolor').val('#6f42c1');  // если для плитки цвет не указан, устанавливаем цвет по умолчанию
    } else {
        $('#editLinkForm-bgcolor').val('#'+bgcolor.replace('#',''));
    }
    $('#editLinkForm-border-right-width').val(borderRightWidth);
    $('#editLinkForm-border-left-width').val(borderLeftWidth);
    $('#editLinkForm-border-top-width').val(borderTopWidth);
    $('#editLinkForm-border-bottom-width').val(borderBottomWidth);
    $('#editLinkForm-title-font-size').val(titleFontSize);
    if(borderRightColor==='') {
        $('#editLinkForm-border-right-color').val('#000000');  // если цвет правой границы плитки не указан, устанавливаем значение по умолчанию
    } else {
        $('#editLinkForm-border-right-color').val('#'+borderRightColor.replace('#',''));
    }
    if(borderLeftColor==='') {
        $('#editLinkForm-border-left-color').val('#000000');  // если цвет левой границы плитки не указан, устанавливаем значение по умолчанию
    } else {
        $('#editLinkForm-border-left-color').val('#'+borderLeftColor.replace('#',''));
    }
    if(borderTopColor==='') {
        $('#editLinkForm-border-top-color').val('#000000');  // если цвет верхней границы плитки не указан, устанавливаем значение по умолчанию
    } else {
        $('#editLinkForm-border-top-color').val('#'+borderTopColor.replace('#',''));
    }
    if(borderBottomColor==='') {
        $('#editLinkForm-border-bottom-color').val('#000000');  // если цвет нижней границы плитки не указан, устанавливаем значение по умолчанию
    } else {
        $('#editLinkForm-border-bottom-color').val('#'+borderBottomColor.replace('#',''));
    }
    if(titleFontColor==='') {
        $('#editLinkForm-title-font-color').val('#ffffff');  // если цвет заголовка плитки не указан, устанавливаем значение по умолчанию
    } else {
        $('#editLinkForm-title-font-color').val('#'+titleFontColor.replace('#',''));
    }
    $('#editLinkForm-url').val(urlPattern);  // помещаем адрес ссылки плитки в поле диалогового окна
    $('#editLinkForm-owner').val(owner);  // помещаем отвественного за наличие плитки в АСФО в поле диалогового окна
    $('#editLinkFormCommitBtn').off('click');  // удаляем обработчик клика кнопки "применить" диалогового окна (если таковой был)
    // дабавляем новый обработчик клика кнопки "применить" диалогового окна
    $('#editLinkFormCommitBtn').click(function (event) {
        let newTitle = $('#editLinkForm-title').val();  // берем текст заголовка из диалогового окна
        let newDescription = $('#editLinkForm-description').val();  // берем текст подробного описания из плитки
        let newBgcolor = $('#editLinkForm-bgcolor').val().replace('#','');  // берем цвет фона плитки из диалогового окна
        let newBorderRightWidth = parseInt($('#editLinkForm-border-right-width').val());  // берем ширину правой границы плитки из диалогового окна
        if(Number.isNaN(newBorderRightWidth)) {
            event.preventDefault();  // отменяем действие по умолчанию
            alert('Введено некорректное значение ширины правой границы');
            return;
        }
        let newBorderLeftWidth = parseInt($('#editLinkForm-border-left-width').val());  // берем ширину левой границы плитки из диалогового окна
        if(Number.isNaN(newBorderLeftWidth)) {
            event.preventDefault();  // отменяем действие по умолчанию
            alert('Введено некорректное значение ширины левой границы');
            return;
        }
        let newBorderTopWidth = parseInt($('#editLinkForm-border-top-width').val());  // берем ширину верхней границы плитки из диалогового окна
        if(Number.isNaN(newBorderTopWidth)) {
            event.preventDefault();  // отменяем действие по умолчанию
            alert('Введено некорректное значение ширины верхней границы');
            return;
        }
        let newBorderBottomWidth = parseInt($('#editLinkForm-border-bottom-width').val());  // берем ширину нижней границы плитки из диалогового окна
        if(Number.isNaN(newBorderBottomWidth)) {
            event.preventDefault();  // отменяем действие по умолчанию
            alert('Введено некорректное значение ширины нижней границы');
            return;
        }
        let newTitleFontSize = parseInt($('#editLinkForm-title-font-size').val());  // берем размер шрифта заголовка плитки из диалогового окна
        if(Number.isNaN(newTitleFontSize)) {
            event.preventDefault();  // отменяем действие по умолчанию
            alert('Введено некорректное размера шрифта');
            return;
        }
        let newBorderRightColor = $('#editLinkForm-border-right-color').val().replace('#','');  // берем цвет правой границы плитки из диалогового окна
        let newBorderLeftColor = $('#editLinkForm-border-left-color').val().replace('#','');  // берем цвет левой границы плитки из диалогового окна
        let newBorderTopColor = $('#editLinkForm-border-top-color').val().replace('#','');  // берем цвет верхней границы плитки из диалогового окна
        let newBorderBottomColor = $('#editLinkForm-border-bottom-color').val().replace('#','');  // берем цвет нижней границы плитки из диалогового окна
        let newTitleFontColor = $('#editLinkForm-title-font-color').val().replace('#','');  // берем цвет заголовка плитки из диалогового окна
        let newUrlPattern = $('#editLinkForm-url').val();  // берем адрес ссылки из диалогового окна
        let newOwner = $('#editLinkForm-owner').val();  // берем ответственного за наличие плитки в АСФО из диалогового окна
        if((title !== newTitle) || (urlPattern !== newUrlPattern) || (description !== newDescription)
            || (bgcolor !== newBgcolor)
            || (borderRightWidth !== newBorderRightWidth)
            || (borderLeftWidth !== newBorderLeftWidth)
            || (borderTopWidth !== newBorderTopWidth)
            || (borderBottomWidth !== newBorderBottomWidth)
            || (borderRightColor !== newBorderRightColor)
            || (borderLeftColor !== newBorderLeftColor)
            || (borderTopColor !== newBorderTopColor)
            || (borderBottomColor !== newBorderBottomColor)
            || (titleFontSize !== newTitleFontSize)
            || (titleFontColor !== newTitleFontColor)
            || (owner !== newOwner) ) {
            setModifiedMode();  // активируем в меню кнопки "сохранить" и "отменить"
            selectedTile.find('.tileTitle').text(newTitle);  // меняем заголовок в плитке
            selectedTile.find('.tileDescription').text(newDescription);  // меняем текст подробного описания в плитке
            selectedTile.find('.tileBgcolor').text(newBgcolor);  // меняем цвет фона плитки в плитке
            selectedTile.css('background-color', '#'+newBgcolor);  // перекрашиваем плитку в новый цвет
            selectedTile.find('.tileBorderRightWidth').text(newBorderRightWidth);  // меняем ширину правой границы в плитке
            selectedTile.find('.tileBorderLeftWidth').text(newBorderLeftWidth);  // меняем ширину левой границы в плитке
            selectedTile.find('.tileBorderTopWidth').text(newBorderTopWidth);  // меняем ширину верхней границы в плитке
            selectedTile.find('.tileBorderBottomWidth').text(newBorderBottomWidth);  // меняем ширину нижней границы в плитке
            selectedTile.find('.tileTitleFontSize').text(newTitleFontSize);  // меняем размер шрифта заголовка плитки в плитке
            selectedTile.find('.tileBorderRightColor').text(newBorderRightColor);  // меняем цвет правой границы в плитке
            selectedTile.find('.tileBorderLeftColor').text(newBorderLeftColor);  // меняем цвет левой границы в плитке
            selectedTile.find('.tileBorderTopColor').text(newBorderTopColor);  // меняем цвет верхней границы в плитке
            selectedTile.find('.tileBorderBottomColor').text(newBorderBottomColor);  // меняем цвет нижней границы в плитке
            selectedTile.find('.tileTitleFontColor').text(newTitleFontColor);  // меняем цвет шрифта заголовка плитки в плитке
            selectedTile.css('border-right-width', newBorderRightWidth+'px');  // обновляем ширину правой границы в плитке
            selectedTile.css('border-left-width', newBorderLeftWidth+'px');  // обновляем ширину левой границы в плитке
            selectedTile.css('border-top-width', newBorderTopWidth+'px');  // обновляем ширину верхней границы в плитке
            selectedTile.css('border-bottom-width', newBorderBottomWidth+'px');  // обвновляем ширину нижней границе в плитке
            selectedTile.find('.tileTitle').css('font-size', newTitleFontSize+'px');  // обновляем размер шрифта в плитке
            selectedTile.css('border-right-color','#'+newBorderRightColor);  // перекрашиваем правую границу плитки в новый цвет
            selectedTile.css('border-left-color','#'+newBorderLeftColor);  // перекрашиваем левую границу плитки в новый цвет
            selectedTile.css('border-top-color','#'+newBorderTopColor);  // перекрашиваем верхнюю границу плитки в новый цвет
            selectedTile.css('border-bottom-color','#'+newBorderBottomColor);  // перекрашиваем нижнюю границу плитки в новый цвет
            selectedTile.find('.tileTitle').css('color','#'+newTitleFontColor);  // перекрашиваем заголовок плитки в новый цвет
            selectedTile.find('.url_pattern').text(newUrlPattern);  // меняем адрес ссылки в плитке
            selectedTile.find('.tileOwner').text(newOwner);  // меняем ответственного за наличие справки в АСФО в плитке
        }
        $('#editLinkForm').modal('hide');  // закрываем диалоговое окно
    });
    $('#editLinkForm').modal();  // показываем диалоговое коно редактирования ссылки
}

// открывает диалоговое окно редактирования плитки заглушки
// 2020-02-11
function showStubEditDialog(tile) {
    selectedTile = $(tile);  // запоминаем текущую выбранную плитку
    let description = selectedTile.find('.tileDescription').text();  // берем текст подробного описания из плитки
    let bgcolor = selectedTile.find('.tileBgcolor').text();  // берем цвет фона плитки из плитки
    let borderRightWidth = parseInt(selectedTile.find('.tileBorderRightWidth').text());  // берем ширину правой границы рамки из плитки
    if(Number.isNaN(borderRightWidth))borderRightWidth=1;
    let borderLeftWidth = parseInt(selectedTile.find('.tileBorderLeftWidth').text());  // берем ширину левой границы рамки из плитки
    if(Number.isNaN(borderLeftWidth))borderLeftWidth=1;
    let borderTopWidth = parseInt(selectedTile.find('.tileBorderTopWidth').text());  // берем ширину верхней границы рамки из плитки
    if(Number.isNaN(borderTopWidth))borderTopWidth=1;
    let borderBottomWidth = parseInt(selectedTile.find('.tileBorderBottomWidth').text());  // берем ширину нижней границы рамки из плитки
    if(Number.isNaN(borderBottomWidth))borderBottomWidth=1;
    let borderRightColor = selectedTile.find('.tileBorderRightColor').text();  // берем цвет правой границы рамки из плитки
    let borderLeftColor = selectedTile.find('.tileBorderLeftColor').text();  // берем цвет левой границы рамки из плитки
    let borderTopColor = selectedTile.find('.tileBorderTopColor').text();  // берем цвет верхней границы рамки из плитки
    let borderBottomColor = selectedTile.find('.tileBorderBottomColor').text();  // берем цвет нижней границы рамки из плитки
    $('#editStubForm-description').val(description);  // помещаем текст подробного описания плитки в поле диалогового окна
    if(bgcolor==='') {
        $('#editStubForm-bgcolor').val('#008cba');  // если для плитки цвет не указан, устанавливаем цвет по умолчанию
    } else {
        $('#editStubForm-bgcolor').val('#'+bgcolor.replace('#',''));
    }
    $('#editStubForm-border-right-width').val(borderRightWidth);
    $('#editStubForm-border-left-width').val(borderLeftWidth);
    $('#editStubForm-border-top-width').val(borderTopWidth);
    $('#editStubForm-border-bottom-width').val(borderBottomWidth);
    if(borderRightColor==='') {
        $('#editStubForm-border-right-color').val('#000000');  // если цвет правой границы плитки не указан, устанавливаем значение по умолчанию
    } else {
        $('#editStubForm-border-right-color').val('#'+borderRightColor.replace('#',''));
    }
    if(borderLeftColor==='') {
        $('#editStubForm-border-left-color').val('#000000');  // если цвет левой границы плитки не указан, устанавливаем значение по умолчанию
    } else {
        $('#editStubForm-border-left-color').val('#'+borderLeftColor.replace('#',''));
    }
    if(borderTopColor==='') {
        $('#editStubForm-border-top-color').val('#000000');  // если цвет верхней границы плитки не указан, устанавливаем значение по умолчанию
    } else {
        $('#editStubForm-border-top-color').val('#'+borderTopColor.replace('#',''));
    }
    if(borderBottomColor==='') {
        $('#editStubForm-border-bottom-color').val('#000000');  // если цвет нижней границы плитки не указан, устанавливаем значение по умолчанию
    } else {
        $('#editStubForm-border-bottom-color').val('#'+borderBottomColor.replace('#',''));
    }
    $('#editStubFormCommitBtn').off('click');  // удаляем обработчик клика кнопки "применить" диалогового окна (если таковой был)
    // дабавляем новый обработчик клика кнопки "применить" диалогового окна
    $('#editStubFormCommitBtn').click(function (event) {
        let newDescription = $('#editStubForm-description').val();  // берем текст подробного описания из плитки
        let newBgcolor = $('#editStubForm-bgcolor').val().replace('#','');  // берем цвет фона плитки из диалогового окна
        let newBorderRightWidth = parseInt($('#editStubForm-border-right-width').val());  // берем ширину правой границы плитки из диалогового окна
        if(Number.isNaN(newBorderRightWidth)) {
            event.preventDefault();  // отменяем действие по умолчанию
            alert('Введено некорректное значение ширины правой границы');
            return;
        }
        let newBorderLeftWidth = parseInt($('#editStubForm-border-left-width').val());  // берем ширину левой границы плитки из диалогового окна
        if(Number.isNaN(newBorderLeftWidth)) {
            event.preventDefault();  // отменяем действие по умолчанию
            alert('Введено некорректное значение ширины левой границы');
            return;
        }
        let newBorderTopWidth = parseInt($('#editStubForm-border-top-width').val());  // берем ширину верхней границы плитки из диалогового окна
        if(Number.isNaN(newBorderTopWidth)) {
            event.preventDefault();  // отменяем действие по умолчанию
            alert('Введено некорректное значение ширины верхней границы');
            return;
        }
        let newBorderBottomWidth = parseInt($('#editStubForm-border-bottom-width').val());  // берем ширину нижней границы плитки из диалогового окна
        if(Number.isNaN(newBorderBottomWidth)) {
            event.preventDefault();  // отменяем действие по умолчанию
            alert('Введено некорректное значение ширины нижней границы');
            return;
        }
        let newBorderRightColor = $('#editStubForm-border-right-color').val().replace('#','');  // берем цвет правой границы плитки из диалогового окна
        let newBorderLeftColor = $('#editStubForm-border-left-color').val().replace('#','');  // берем цвет левой границы плитки из диалогового окна
        let newBorderTopColor = $('#editStubForm-border-top-color').val().replace('#','');  // берем цвет верхней границы плитки из диалогового окна
        let newBorderBottomColor = $('#editStubForm-border-bottom-color').val().replace('#','');  // берем цвет нижней границы плитки из диалогового окна
        if((description !== newDescription)
            || (bgcolor !== newBgcolor)
            || (borderRightWidth !== newBorderRightWidth)
            || (borderLeftWidth !== newBorderLeftWidth)
            || (borderTopWidth !== newBorderTopWidth)
            || (borderBottomWidth !== newBorderBottomWidth)
            || (borderRightColor !== newBorderRightColor)
            || (borderLeftColor !== newBorderLeftColor)
            || (borderTopColor !== newBorderTopColor)
            || (borderBottomColor !== newBorderBottomColor)) {
            setModifiedMode();  // активируем в меню кнопки "сохранить" и "отменить"
            selectedTile.find('.tileDescription').text(newDescription);  // меняем текст подробного описания в плитке
            selectedTile.find('.tileBgcolor').text(newBgcolor);  // меняем цвет фона плитки в плитке
            selectedTile.css('background-color', '#'+newBgcolor);  // перекрашиваем плитку в новый цвет
            selectedTile.find('.tileBorderRightWidth').text(newBorderRightWidth);  // меняем ширину правой границы в плитке
            selectedTile.find('.tileBorderLeftWidth').text(newBorderLeftWidth);  // меняем ширину левой границы в плитке
            selectedTile.find('.tileBorderTopWidth').text(newBorderTopWidth);  // меняем ширину верхней границы в плитке
            selectedTile.find('.tileBorderBottomWidth').text(newBorderBottomWidth);  // меняем ширину нижней границы в плитке
            selectedTile.find('.tileBorderRightColor').text(newBorderRightColor);  // меняем цвет правой границы в плитке
            selectedTile.find('.tileBorderLeftColor').text(newBorderLeftColor);  // меняем цвет левой границы в плитке
            selectedTile.find('.tileBorderTopColor').text(newBorderTopColor);  // меняем цвет верхней границы в плитке
            selectedTile.find('.tileBorderBottomColor').text(newBorderBottomColor);  // меняем цвет нижней границы в плитке
            selectedTile.css('border-right-width', newBorderRightWidth+'px');  // обновляем ширину правой границы в плитке
            selectedTile.css('border-left-width', newBorderLeftWidth+'px');  // обновляем ширину левой границы в плитке
            selectedTile.css('border-top-width', newBorderTopWidth+'px');  // обновляем ширину верхней границы в плитке
            selectedTile.css('border-bottom-width', newBorderBottomWidth+'px');  // обвновляем ширину нижней границе в плитке
            selectedTile.css('border-right-color','#'+newBorderRightColor);  // перекрашиваем правую границу плитки в новый цвет
            selectedTile.css('border-left-color','#'+newBorderLeftColor);  // перекрашиваем левую границу плитки в новый цвет
            selectedTile.css('border-top-color','#'+newBorderTopColor);  // перекрашиваем верхнюю границу плитки в новый цвет
            selectedTile.css('border-bottom-color','#'+newBorderBottomColor);  // перекрашиваем нижнюю границу плитки в новый цвет
        }
        $('#editStubForm').modal('hide');  // закрываем диалоговое окно
    });
    $('#editStubForm').modal();  // показываем диалоговое коно редактирования ссылки
}

// обработчик влючения режима редактирования
// 2019-12-26, 2020-02-11
function onEnableEditMode(event) {
    //event.preventDefault();
    $('#edit-mode').addClass('navbar-edit-active');
    $('#edit-mode a').off('click');  // уберем обработчик события click с кнопки "правка"
    $('#edit-mode a').click(onDisableEditMode);  // добавим обработчик события click на кнопку "правка" (отключить режим правки)
    $('#dashboardActions').addClass('d-md-block');  // восстанавливаем правило css правило display block !important
    $('#dashboardActions').show();  // показываем панель добавления удаления плиток
    $('#tile-description').show();  // показываем поля с подробным описанием плиток
    $('#dashboardMain').css('flex', '0 0 83.3333333333%');  // делаем дашбор не на весь экран по ширине
    $('#dashboardMain').css('max-width', '83.3333333333%');  // делаем дашбор не на весь экран по ширине
    $('#advanced-grid').data('gridstack').enable();  // отключаем возможность перетаскивания и изменения размеров плиток
    // добавление обработчика двойного клика по плитке
    $('#advanced-grid .pageWidget').dblclick(function (event) {
        showPageEditDialog(this);
    });
    $('#advanced-grid .linkWidget').dblclick(function (event) {
        showLinkEditDialog(this);
    });
    $('#advanced-grid .stubWidget').dblclick(function (event) {
        showStubEditDialog(this);
    });
    // удаление обработчика клика по плитке (отключение перехода на url)
    $('#advanced-grid .pageWidget').off('click');
    $('#advanced-grid .linkWidget').off('click');
    $('#advanced-grid .stubWidget').off('click');
}

// обработчик отключения режима редактирования
// 2019-12-26
function onDisableEditMode(event) {
    //event.preventDefault();
    $('#edit-mode').removeClass('navbar-edit-active');
    $('#edit-mode a').off('click');  // уберем обработчик события click с кнопки "правка"
    $('#edit-mode a').click(onEnableEditMode);  // добавим обработчик события click на кнопку "правка" (включить режим правки)
    $('#dashboardActions').removeClass('d-md-block');  // удаляем css правило display block !important
    $('#dashboardActions').hide();  // скрываем панель добавления/удаления плиток
    $('#tile-description').hide();  // скрываем поля с подробным описанием плиток
    $('#dashboardMain').css('flex', '0 0 100%');  // делаем дашбор на весь экран по ширине
    $('#dashboardMain').css('max-width', '100%');  // делаем дашбор на весь экран по ширине
    $('#advanced-grid').data('gridstack').disable();  // отключаем возможность перетаскивания и изменения размеров плиток
    // отключение обработчика двойного клика по плитке
    $('#advanced-grid .pageWidget').off('dblclick');
    $('#advanced-grid .linkWidget').off('dblclick');
    $('#advanced-grid .stubWidget').off('dblclick');
    // добавление обработчика клика по плитке (включение перехода на url)
    $('#advanced-grid .pageWidget').click(function (event) {
        if(modifiedMode) {
            alert('Есть несохраненные изменения на странице. Необходимо выполнить сохранение прежде чем осущствлять переход!');
            return;
        }
        let tile = $(this);

        tile.addClass('tileClicked');
        $('#advanced-grid').hide().show(0);  // 2020-04-09
        setTimeout(function () {
            $('.tileClicked').removeClass('tileClicked');
        }, 1000);

        let profile_name = location.href.match(/[^\/]*$/)[0];
        let href_without_profile_name = location.href.replace(/[^\/]*$/, '');
        let href_without_path = href_without_profile_name.replace(/(\d+\/)*$/, '');
        let path_str = '';
        if(getTilePath(tile) !== '') {
            path_str = getTilePath(tile) + '/';
        }
        location.href = href_without_path + path_str + getTileId(tile) + '/' + profile_name;
    });
    $('#advanced-grid .linkWidget').click(function (event) {
        if(modifiedMode) {
            alert('Есть несохраненные изменения на странице. Необходимо выполнить сохранение прежде чем осущствлять переход!');
            return;
        }

        let tile = $(this);
        tile.addClass('tileClicked');
        $('#advanced-grid').hide().show(0);  // 2020-04-09
        setTimeout(function () {
            $('.tileClicked').removeClass('tileClicked');
        }, 1000);

        setTimeout(function(){
            let url = getTileData(tile).url_pattern;
            if(url === '') {
                alert('Пустая ссылка!');
                return;
            }
            if(!/^http/i.test(url)) {
                url = 'http://' + url;
            }
            url = url.replace(/\{dd\}/g, getDay());
            url = url.replace(/\{mm\}/g, getMonth());
            url = url.replace(/\{yy\}/g, getShortYear());
            url = url.replace(/\{yyyy\}/g, getFullYear());
            // проверим, что ссылка url способна открываться, прежде чем ее открыть
            if(/asfo(-\d+)?\.krw\.oao\.rzd/i.test(url)) {
                if(!isLocal()) {
                    $.ajax({
                        url: url,
                        cache: false,
                        type: 'HEAD',
                        async: false,
                        error: function (jqXHR, textStatus, errorThrown) {
                            alert('Страница недоступна');
                            // console.log(jqXHR);
                            // console.log(textStatus);
                            // console.log(errorThrown);
                        },
                        success: function (data, textStatus, jqXHR) {
                            console.log('asfo page is available url=' + url);
                            window.open(url, '_blank');
                        }
                    });
                } else {
                    let local_url = url.replace(/^.*asfo(-\d+)?\.krw\.oao\.rzd\//i, $('#local-flag').text()+'plitki_common/');
                    console.log('local_url='+local_url);
                    window.open(local_url, '_blank');
                }
            } else {
                window.open(url, '_blank');
            }
        },100);

    });
    $('#advanced-grid .stubWidget').click(function (event) {
        // клик на заглушке, не выполняем никаких действий
    });
    $('#advanced-grid .pageWidget').mousedown(function (event) {
        let tile = $(this);
        tile.addClass('tileClicked');
        setTimeout(function () {
            $('.tileClicked').removeClass('tileClicked');
        }, 1000);
    });
    $('#advanced-grid .linkWidget').mousedown(function (event) {
        let tile = $(this);
        tile.addClass('tileClicked');
        setTimeout(function () {
            $('.tileClicked').removeClass('tileClicked');
        }, 1000);
    });

    // подгоняем высоту плиток, чтобы все они вмещались на экран по вертикали
    let maxGsHeight = 0;  //
    let windowHeight = window.innerHeight;  // высота фрейма
    windowHeight -= 60;  // высота фрейма без меню навигации
    windowHeight -= 10;  // оставляем снизу немного свободного пространства
    if($('.breadcrumb').length > 0) windowHeight -= 20;  // высота фрейма без breadcrumb
    $('#advanced-grid > .grid-stack-item').map(function (i, el) {
        let tileData = getTileData(el);
        let absoluteTileHeight = tileData.y + tileData.height;
        if(absoluteTileHeight > maxGsHeight)maxGsHeight = absoluteTileHeight;
    });
    if(windowHeight < maxGsHeight*60) {
        let tileHeight = windowHeight/maxGsHeight;  // новая расчетная высота плитки высотой data-gs-height=1 в px (по умолчанию 60px)
        let grid = gridStackObj.data('gridstack');
        grid.cellHeight(tileHeight);
    }
}

// обработчик клика на кнопке "Настройки"
// 2019-12-27
function onSettingsBtn(event) {
    //event.preventDefault();
    /*date = $('#calendar').val();
    console.log('date='+date);
    console.log('year='+getFullYear());
    console.log('year sh='+getShortYear());
    console.log('month='+getMonth());
    console.log('day='+getDay());*/
    location.href = '/settings/';
}

// возвращает год из календаря напр 2019
// 2019-12-27
function getFullYear() {
    return $('#calendar').val().slice(0,4);
}

// возвращает год из календаря напр 19
// 2019-12-27
function getShortYear() {
    return $('#calendar').val().slice(2,4);
}

// возвращает месяц из календаря напр 12
// 2019-12-27
function getMonth() {
    return $('#calendar').val().slice(5,7);
}

// возвращает день из календаря напри 01
// 2019-12-27
function getDay() {
    return $('#calendar').val().slice(8,10);
}

// обработчик document ready
$(function() {
    // инициализируем календарь
    let date = new Date();
    date.setDate(date.getDate()-1);  // устанавливаем дату на прошедший день
    $('#calendar').val(date.toJSON().slice(0,10));

    $('#settings-btn a').click(onSettingsBtn);  // добавим обработчик события кнопки "Настройки"
    $('#cancel-changes a').click(onCancelChanges);  // добавим обработчик события кнопки "Отменить"
    $('#save-changes a').click(onSaveChanges);  // добавим обработчик события кнопки "Сохранить"
    $('#edit-mode a').click(onEnableEditMode);  // добавим обработчик события кнопки "Правка (включить)"

    gridStackObj = $('#advanced-grid');  // инициализируем jQuery-объект #advanced-grid

    // инициализируем панель для плиток
    gridStackObj.gridstack({
        alwaysShowResizeHandle: /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
            navigator.userAgent
        ),
        resizable: {
            handles: 'e, se, s, sw, w'
        },
        removable: '#trash',
        removeTimeout: 100,
        acceptWidgets: '.newWidget'
    });

    // обработчик добавления элемента(ов) на панель для плиток
    gridStackObj.on('added', function(event, items) {
        setModifiedMode();  // активируем в меню кнопки "сохранить" и "отменить"
        for (let i = 0; i < items.length; i++) {
            let tile = items[i].el;
            if(getTileType(tile) === 'page') {
                tile.dblclick(function (event) {
                    showPageEditDialog(this);
                });
            } else if(getTileType(tile) === 'link') {
                tile.dblclick(function (event) {
                    showLinkEditDialog(this);
                });
            } else if(getTileType(tile) === 'stub') {
                tile.dblclick(function (event) {
                    showStubEditDialog(this);
                });
            }
            $(tile).on('mouseover', function (event) {
                $('#tileDescription').text($(tile).find('.tileDescription').text());
            });
            $(tile).on('mouseout', function (event) {
                $('#tileDescription').text('');
            });
        }
    });

    // обработчик удаления элемента(ов) на панель для плиток
    gridStackObj.on('removed', function(event, items) {
        setModifiedMode();  // активируем в меню кнопки "сохранить" и "отменить"
        for (let i = 0; i < items.length; i++) {
            pushTileToDelete(items[i].el);  // помещаем плитку в массив удаленных плиток
        }
    });

    // обработчик изменения элемента(ов) на панель для плиток
    gridStackObj.on('change', function(event, items) {
        setModifiedMode();  // активируем в меню кнопки "сохранить" и "отменить"
    });
    
    $('#advanced-grid .pageWidget').on('mouseover', function (event) {
        $('#tileDescription').text($(this).find('.tileDescription').text());
    });
    $('#advanced-grid .linkWidget').on('mouseover', function (event) {
        $('#tileDescription').text($(this).find('.tileDescription').text());
    });
    $('#advanced-grid .stubWidget').on('mouseover', function (event) {
        $('#tileDescription').text($(this).find('.tileDescription').text());
    });
    $('#advanced-grid .pageWidget').on('mouseout', function (event) {
        $('#tileDescription').text('');
    });
    $('#advanced-grid .linkWidget').on('mouseout', function (event) {
        $('#tileDescription').text('');
    });
    $('#advanced-grid .stubWidget').on('mouseout', function (event) {
        $('#tileDescription').text('');
    });

    // инициализируем элементы для добавления новых плиток
    $('.newWidget').draggable({
        revert: 'invalid',
        scroll: false,
        appendTo: 'body',
        helper: 'clone'
    });

    // устанавливаем минимальное расстояние по вертикали между плитками
    let grid = gridStackObj.data('gridstack');
    grid.verticalMargin(0.001);  // little hack устанавливаем минимальное расстояние по вертикали между плитками

    // отключим режим редактирования
    onDisableEditMode(null);

    // настройка панели навигации
    $('.nav-item').on('click', function(event) {
        $('.nav-item').removeClass('active');
        let target = $(event.currentTarget);
        if (target.hasClass('nav-item-highlight')) {
            target.addClass('active');
        }
    });
});
