var province_holder = document.createDocumentFragment();
var commune_holder = document.createDocumentFragment();

// store provinces
var all_provinces = document.querySelectorAll('#id_commune_1 option');
for (var i = 0; i < all_provinces.length; i++) {
    province_holder.appendChild(all_provinces[i]);
}

// store communes
var all_communes = document.querySelectorAll('#id_commune_2 option');
for (var i = 0; i < all_communes.length; i++) {
    commune_holder.appendChild(all_communes[i]);
}

var region_select = document.querySelector('#id_commune_0');
var province_select = document.querySelector('#id_commune_1');
var commune_select = document.querySelector('#id_commune_2');

region_select.onchange = function () {
    while (province_select.firstChild) {
        province_select.removeChild(province_select.firstChild);
    }

    var matches = province_holder.querySelectorAll('option[value^='+'"'+region_select.value+'"'+']');
    for (var i = 0; i < matches.length; i++) {
        province_select.appendChild(matches[i].cloneNode(true));
    }
    province_select.onchange();
}

province_select.onchange = function () {
    while (commune_select.firstChild) {
        commune_select.removeChild(commune_select.firstChild);
    }

    var matches = commune_holder.querySelectorAll('option[value^='+'"'+province_select.value+'"'+']');
    for (var i = 0; i < matches.length; i++) {
        commune_select.appendChild(matches[i].cloneNode(true));
    }
}
