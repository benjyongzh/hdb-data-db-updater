SELECT DISTINCT ON (street_name, block) block,street_name FROM datacollector_resaletransaction
	ORDER BY street_name, block;