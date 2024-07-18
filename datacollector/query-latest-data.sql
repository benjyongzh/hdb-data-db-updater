SELECT DISTINCT ON (full_unit_name) * FROM
	(SELECT id, month, town, (
		SELECT street_name
		|| ' ' || block
		|| ' ' || flat_type
		|| ' ' || flat_model
		|| ' ' || storey_range
		|| ' ' || floor_area_sqm AS full_unit_name),
	resale_price FROM datacollector_resaletransaction
	ORDER BY full_unit_name, month, id DESC) 
orderedbyunitname;