TimelapseQuantifyFluoresence

Scripts to extract pixel values from masked cytoplasm/nuclei.
Workflow:

Create pickle file / make movie
01DownsizedMovie


Mark gonad:
method a) Use 02aMarkGonad
method b) Mark positions in ImageJ, Create excel with POI positions, then use 02bLoadGonadPosFromText to Update pickle file 
	

Crop and correct images
03CropImages	


Mark cells
04MarkCells


Outline ROIs
05OutlineCells
	

Calculate
06ComputeFluouresence
