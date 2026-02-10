This folder contains the script used to produce the OBSALL part of the scientific plot inserted in the schema proposed in Figure 4. These panels represent an example of observation-based posterior evaluation of climate simulations.

Contents:

1.) mean-map_short_2.py
	- The script to produce observation-based evaluation of ICON, IFS-FESOM and IFS-NEMO in one plot.
	- Run without arguments: python3 mean-map_short_2.py

2.) mean-map-model_results.pickle
	- Preprocessed data for the plots.
	
3.) requirements.in
	- A list of Python packages required for running mean-map_short_2.py
	
4.) plots
	- Output directory for the model evaluation plot.
	
5.) SYNOP/synop_station_list.txt
	- Coordinates of the SYNOP stations in the observed and simulated data sets.
