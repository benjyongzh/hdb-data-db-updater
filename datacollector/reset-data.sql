DELETE FROM datacollector_resaletransaction WHERE id > 0;
ALTER SEQUENCE datacollector_resaletransaction_id_seq RESTART WITH 1;

SELECT * FROM datacollector_resaletransaction;