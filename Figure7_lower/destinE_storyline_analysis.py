import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import BoundaryNorm
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.patches as mpatches
import pandas as pd
import matplotlib.ticker as ticker
import matplotlib.dates as mdates

# ---------------------------
# Configuration
# ---------------------------

variables = ["Qrouted"]
cities = {
    # 'Valencia1': (39.55307262569832, -0.706896551724137),
    # 'Velencia1': (39.12558, -0.64545),
    'Valencia2': (39.18695, -0.41044),}
# ---------------------------
# Utility Functions
# ---------------------------
def open_dataset(path, start, end, lat_lon=None):
    """Load and optionally subset an xarray dataset by time and region."""
    ds = xr.open_dataset(path).sel(time=slice(start, end))
    if lat_lon:
        region = lat_lon[0]
        ds = ds.sel(
            lat=slice(region["lat_max"], region["lat_min"]),
            lon=slice(region["lon_min"], region["lon_max"])
        )
    return ds
cont_mrm = "/work/kelbling/ecflow_work/gloria_hourly_control/output/gloria_0p05deg/mrm_sim/2020/01/mRM_Fluxes_States.nc"
hist_mrm =  "/work/kelbling/ecflow_work/gloria_hourly_historical/output/gloria_0p05deg/mrm_sim/2020/01/mRM_Fluxes_States.nc"
t2k_mrm =   "/work/kelbling/ecflow_work/gloria_hourly_t2k/output/gloria_0p05deg/mrm_sim/2020/01/mRM_Fluxes_States.nc"
cont_hourly_mrm = open_dataset(cont_mrm,'2020-01-18', '2020-01-24')
hist_hourly_mrm = open_dataset(hist_mrm,'2020-01-18', '2020-01-24')
t2k_hourly_mrm = open_dataset(t2k_mrm,'2020-01-18', '2020-01-24')


# ---------------------------
# Time Series Plotting Function
# ---------------------------
def plot_timeseries(cities, variable, cont, hist, t2k, ylabel, save_as=None):
    fig, axes = plt.subplots(len(cities), 1, figsize=(7,10), sharex=True)
    fig.subplots_adjust(wspace=0.3, hspace=0.3)

    if len(cities) == 1:
        axes = [axes]

    end_date = pd.to_datetime('2020-01-25')
    # for select lat-lon 
    for ax, (city, (lat, lon)) in zip(axes, cities.items()):
    # Process control dataset
        control_event = cont[variable].sel(
            lat=lat, lon=lon, method='nearest'
        )

        # Process historical dataset
        historical_event = hist[variable].sel(
            lat=lat, lon=lon, method='nearest'
        )

        # Process future dataset
        future_event = t2k[variable].sel(
            lat=lat, lon=lon, method='nearest'
        )

        ax.plot(control_event['time'], control_event, 
                label="Counterfactual", linestyle="-", 
                color="#CA0020", linewidth=1.2)
        ax.plot(historical_event['time'], historical_event,
                 label="Actual", linestyle="-", 
                 color="#0571b0", linewidth=1.2)
        ax.plot(future_event['time'], future_event, 
                label="Future", linestyle="-", 
                color="#f4a582", linewidth=1.2)

        ax.set_title(box["city"], fontsize=16)
        if idx == 0:  # Custom scale for subplot (c)
            ax.set_ylim(0.7, 1.0)
        elif idx == 1:
            ax.set_ylim(0.55, 1.0)
        else:
            ax.set_ylim(0.90, 1.0)  # Default auto-scaling for others
        ax.tick_params(axis="both", which="major", labelsize=14)
        ax.grid(color='gray', linestyle='-', linewidth=0.5, alpha=0.7)
        
        # Format x-axis as YYYY-MM-DD
        ax.set_xticks(pd.date_range(start=control_event['time'].values[0], end=end_date, freq='1D'))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.tick_params(axis="x", rotation=90)

        ax.text(0.02, 1.05, f"({chr(97+4+idx)})", 
                transform=ax.transAxes, fontsize=18)

        if idx == 0:
            ax.legend(loc="upper left", fontsize=14, frameon=True)

    fig.supylabel(ylabel, fontsize=18)

    if save_as:
        plt.savefig(save_as, dpi=300, bbox_inches='tight')
    else:
        plt.show()


# ---------------------------
# Example Usage
# ---------------------------
# Set your paths and events here as needed

boundaries = np.arange(-20, 25, 5)  # ends at 5, includes step of 0.2
boundaries_dict = {
    "Q": np.linspace(-20, 20, 11),
    "Qrouted": np.linspace(-50,50,11),
    "aET": np.linspace(0, 1, 11),
    "SM_Lall": np.linspace(-0.3, 0.3, 11),

}

hist_hourly_mrm_dana_day0 = open_dataset("/mRM_Fluxes_States_2024_10_28_to_2024_10_28.nc", 
                                              )
hist_hourly_mrm_dana_day1 = open_dataset("/mRM_Fluxes_States_2024_10_29_to_2024_10_29.nc", )
hist_hourly_mrm_dana_day2 = open_dataset("/mRM_Fluxes_States_2024_10_30_to_2024_10_30.nc", )
hist_hourly_mrm_dana_day3 = open_dataset("/mRM_Fluxes_States_2024_10_31_to_2024_10_31.nc", )
hist_hourly_mrm_dana_day4 = open_dataset("/mRM_Fluxes_States_2024_11_01_to_2024_11_01.nc", )
hist_hourly_mrm_dana_day5 = open_dataset("/mRM_Fluxes_States_2024_11_02_to_2024_11_02.nc", )
hist_hourly_mrm_dana_day6 = open_dataset("/mRM_Fluxes_States_2024_11_03_to_2024_11_03.nc", )


hist = xr.concat([hist_hourly_mrm_dana_day0, 
                       hist_hourly_mrm_dana_day1,
                       hist_hourly_mrm_dana_day2, 
                       hist_hourly_mrm_dana_day3, 
                       hist_hourly_mrm_dana_day4,
                       hist_hourly_mrm_dana_day5,
                       hist_hourly_mrm_dana_day6,], dim ="time")

cont_hourly_mrm_dana_day0 = open_dataset("mRM_Fluxes_States_2024_10_28_to_2024_10_28.nc", )
cont_hourly_mrm_dana_day1 = open_dataset("mRM_Fluxes_States_2024_10_29_to_2024_10_29.nc", )
cont_hourly_mrm_dana_day2 = open_dataset("mRM_Fluxes_States_2024_10_30_to_2024_10_30.nc", )
cont_hourly_mrm_dana_day3 = open_dataset("mRM_Fluxes_States_2024_10_31_to_2024_10_31.nc", )
cont_hourly_mrm_dana_day4 = open_dataset("mRM_Fluxes_States_2024_11_01_to_2024_11_01.nc", )
cont_hourly_mrm_dana_day5 = open_dataset("mRM_Fluxes_States_2024_11_02_to_2024_11_02.nc", )
cont_hourly_mrm_dana_day6 = open_dataset("mRM_Fluxes_States_2024_11_03_to_2024_11_03.nc", )



cont = xr.concat([cont_hourly_mrm_dana_day0, 
                       cont_hourly_mrm_dana_day1, 
                       cont_hourly_mrm_dana_day2, 
                       cont_hourly_mrm_dana_day3,
                       cont_hourly_mrm_dana_day4,
                       cont_hourly_mrm_dana_day5,
                       cont_hourly_mrm_dana_day6,], dim ="time")



t2k_hourly_mrm_dana_day0 = open_dataset("/mRM_Fluxes_States_2024_10_28_to_2024_10_28.nc", )
t2k_hourly_mrm_dana_day1 = open_dataset("/mRM_Fluxes_States_2024_10_29_to_2024_10_29.nc", )
t2k_hourly_mrm_dana_day2 = open_dataset("/mRM_Fluxes_States_2024_10_30_to_2024_10_30.nc", )
t2k_hourly_mrm_dana_day3 = open_dataset("/mRM_Fluxes_States_2024_10_31_to_2024_10_31.nc", )
t2k_hourly_mrm_dana_day4 = open_dataset("/mRM_Fluxes_States_2024_11_01_to_2024_11_01.nc", )
t2k_hourly_mrm_dana_day5 = open_dataset("/mRM_Fluxes_States_2024_11_02_to_2024_11_02.nc", )
t2k_hourly_mrm_dana_day6 = open_dataset("/mRM_Fluxes_States_2024_11_03_to_2024_11_03.nc", )



t2k = xr.concat([t2k_hourly_mrm_dana_day0, 
                      t2k_hourly_mrm_dana_day1, 
                      t2k_hourly_mrm_dana_day2, 
                      t2k_hourly_mrm_dana_day3, 
                      t2k_hourly_mrm_dana_day4, 
                      t2k_hourly_mrm_dana_day5, 
                      t2k_hourly_mrm_dana_day6], dim ="time")

plot_timeseries(cities, 'Qrouted', cont, hist, t2k, 
                ylabel='Qrouted [m3 sec-1]',
                save_as="desitnE_timeseries.png")
