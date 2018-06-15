function initSortable(el) {
    var sortable = Sortable.create(el, {group: "songs"});
}

var el = document.getElementById('selected-songs');
initSortable(el);
el = document.getElementById('available-songs');
initSortable(el);
