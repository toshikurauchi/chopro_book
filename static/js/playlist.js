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

    function sort() {
        var sortableList = $('#available-songs');
        var listitems = $('li', sortableList);
    
        listitems.sort(function (a, b) {
    
            return ($(a).text().toUpperCase() > $(b).text().toUpperCase())  ? 1 : -1;
        });
        sortableList.append(listitems);    
    }

    $('.toggle-song').click(function() {
        let listId = this.parentElement.parentElement.id;
        sort();
        let otherId = 'selected-songs';
        if (listId == 'selected-songs') otherId = 'available-songs';        
        $('#' + otherId).append($(this.parentElement));
    });
    
    var sortableSelected = Sortable.create(document.getElementById('selected-songs'), {group: "songs" });
    var sortableAvailable = Sortable.create(document.getElementById('available-songs'), {group: "songs" });
    
}