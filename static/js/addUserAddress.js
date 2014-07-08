function insertNewRow(){
		$('#mainTable tr:last').after('
		<tr>
		<td>{{ address.street }}</td>
		<td>{{ address.city }}</td>
		<td>{{ address.state }}</td>
		<td>{{ address.zip_code }}</td>
		<td>{{ address.phone }}</td>
		<td>{{ address.unit_number }}</td>
		<td>{{ address.company }}</td>
		<td>{{ address.cross_streets }}</td>
		<td style="display: none;"> {{address.location_id}}</td>
		<td>
		<button type="button" class="btn btn-default btn-sm">
		<span class="glyphicon glyphicon-remove"></span>
		</button>
		</td>
		</tr>
		');
}