SELECT DISTINCT ON (street_name, block, flat_type, flat_model, storey_range, floor_area_sqm) * FROM
	(SELECT * FROM datacollector_resaletransaction
	ORDER BY street_name, block, flat_type, flat_model, storey_range, floor_area_sqm, month, id DESC)
orderedbyunitname;