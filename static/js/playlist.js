window.onload = function() {

    document.getElementById('playlist-form').onsubmit = function() {
        var ok = true;
        // Set name
        var pname = document.getElementById('playlist_name');
        var fname = document.getElementById('name');
        if (pname.checkValidity()) {
            pname.classList.remove('invalid');
            pname.classList.add('valid');
        }
        else {
            pname.classList.remove('valid');
            pname.classList.add('invalid');
            ok = false;
        }
        fname.value = pname.value;

        // Set songs
        var selectedSongs = document.getElementById('selected-songs').children;
        var songs = document.getElementById('songs');
        var nSongs = selectedSongs.length;
        var songList = [];
        for (var i = 0; i < nSongs; i++) {
            songList.push(selectedSongs[i].getAttribute('data-filename'));
        };
        songs.value = songList.join(';;');
        return ok;
    }
    
    function initSortable(el) {
        var sortable = Sortable.create(el, {group: "songs"});
    }
    
    var el = document.getElementById('selected-songs');
    initSortable(el);
    el = document.getElementById('available-songs');
    initSortable(el);
    
}