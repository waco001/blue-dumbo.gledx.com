/* global $ */
/* this is an example for validation and change events */
$.fn.numericInputExample = function () {
	'use strict';
	var element = $(this),
	footer = element.find('tfoot tr'),
	dataRows = element.find('tbody tr'),
	addRow = element.find('tbody tr .addTable'),
	initialTotal = function () { };
	element.find('td').on('change', function (evt) {
		var cell = $(this),
		column = cell.index(),
		total = 0,
		currentText, currentRow, currentrownum = 0;

		element.find('tbody tr').each(function () {
			var row = $(this);
			currentRow = row;
			currentText = row.children().eq(column).text();
					$("#alertMessage").text(''); //Reset message
		$("#successMessage").text(''); //Reset message

		if (column === 4 && currentText.length != 10) {
			$("#alertMessage").text('Please enter a valid 10 digit telephone number (ex. 5555555555)');
			$('.alert').show();
			return false; // changes can be rejected
		} else {
			$('.alert').hide();
			//footer.children().eq(column).text(total);
		}
		if (column === 3 && currentText.length != 5) {
			$("#alertMessage").text('Please enter a valid 5 digit area zip code (ex. 20220)');
			$('.alert').show();
			return false; // changes can be rejected
		} else {
			$('.alert').hide();
			//footer.children().eq(column).text(total);
		}
		$.post( window.userPostAddress, 
		{ 
			street: currentRow.children().eq(0).text(),
			city: currentRow.children().eq(1).text(),
			state: currentRow.children().eq(2).text(),
			zip_code: currentRow.children().eq(3).text(),
			phone: currentRow.children().eq(4).text(),
			unit_number: currentRow.children().eq(5).text(),
			company: currentRow.children().eq(6).text(),
			cross_streets: currentRow.children().eq(7).text(),
			location_id : currentRow.children().eq(8).text()
		}, function( data ) {
			var json = $.parseJSON(data);
			$("#successMessage").text(json.message[0].user_msg);
			$('#successMessage').show();
		});
	});
}).on('validate', function (evt, value) {
	var cell = $(this),
	column = cell.index();
	if (column === 4 && isNaN(parseFloat(value)) === true && isFinite(value) === false) {
		return false;
	}
	if (column === 3 && isNaN(parseFloat(value)) === true && isFinite(value) === false) {
		return false;
	}
});
initialTotal();
return this;
};
