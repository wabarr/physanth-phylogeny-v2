function cleanUp(){
    $('#people-search-results').html("");
    $('.results_on_deck').html("");
    $('select').prop('selectedIndex', 0);
    $('select').material_select();
    $("#query").html("")
}