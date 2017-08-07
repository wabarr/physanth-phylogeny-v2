function cleanUp(){
    $('#people-search-results').html("");
    $('.results_on_deck').html("");
    $('select').prop('selectedIndex', 0);
    $('select').material_select();
    $("#endyear").val("");
    $("#startyear").val("");
    $("#id_search_by_name_text").val("");
}