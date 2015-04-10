function split( val ) {
	return val.split( /,\s*/ );
}

function extractLast( term ) {
	return split( term ).pop();
}

$("#id_co_organizers")
// don't navigate away from the field on tab when selecting an item
.bind( "keydown", function( event ) {
	if ( event.keyCode === $.ui.keyCode.TAB &&
		$( this ).data( "ui-autocomplete" ).menu.active ) {
		event.preventDefault();
	}
})
.autocomplete({
	source: function(request, response) {
		source_list = {{user_list|safe}};
		new_term = extractLast( request.term );
		var re = $.ui.autocomplete.escapeRegex(new_term);
		var matcher = new RegExp( re, "i" );
		var matches = $.grep( source_list, function(item,index){
			return matcher.test(item);
		})
		response(matches);
	},
	select: function( event, ui ) {
		var terms = split( this.value );
		// remove the current input
		terms.pop();
		// add the selected item
		terms.push( ui.item.value );
		// add placeholder to get the comma-and-space at the end
		terms.push( "" );
		this.value = terms.join( ", " );
		return false;
	},
	focus: function() {
		// prevent value inserted on focus
		return false;
	},
});

