import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import xarray as xr
import matplotlib as mpl
from matplotlib.colors import ListedColormap
import cartopy.feature as cfeature


def create_orographic_plot_with_cartopy(data, lat, lon,
                                        title="Orographic Plot",
                                        colorbar_label="Discharge [m3/sec]"):
    """
    Creates an orographic plot with only the data projected, without any terrain or additional features.
    
    Parameters:
        data (2D array): The data array to plot.
        lat (1D array): Latitude values.
        lon (1D array): Longitude values.
        title (str): The title of the plot.
        colorbar_label (str): Label for the colorbar.
    """
    # Define contour levels with exponential scaling
    num_levels = 11
    # levels = np.linspace(-5, 3, num_levels)
    levels = np.linspace(1, 11, num_levels)
    levels = np.exp(levels)  # Exponential scaling
    levels = (levels / np.amax(levels))*1e5 # Normalize to a scale of 1e4

    # Create a discrete colormap
    cmap = plt.cm.BuPu
    discrete_cmap = ListedColormap(cmap(np.linspace(0, 1, 11)))
    norm = mpl.colors.BoundaryNorm(levels, levels.shape[0])
         
    fig, ax = plt.subplots(
        figsize=(5,3),
        subplot_kw={"projection":ccrs.Orthographic(central_longitude=-25.0, 
                                                    central_latitude=50.0)})
    
    # Add features
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':',linewidth=0.02)
    # ax.add_feature(cfeature.LAND, facecolor="grey", zorder=0)
    ax.add_feature(cfeature.OCEAN, facecolor="darkgrey", zorder=1)

    # Plot the data
    mesh = ax.contourf(
         lon, lat, data,
        levels=levels,
        norm=norm,
        cmap=discrete_cmap,
        transform=ccrs.PlateCarree()  # Use PlateCarree for latitude-longitude dat
    )

    # Add a colorbar
    cbar = plt.colorbar(mesh, ax=ax, orientation="vertical", shrink=0.7, pad=0.05, location="left")
    cbar.set_label(colorbar_label)
    cbar.set_ticks(levels)
    cbar.set_ticklabels([f"{val:.1e}" for val in levels] ) # Scientific notation for clarity

    # Add title
    # ax.set_title(title, fontsize=16)

    # Show the plot

    plt.savefig(f"orographic_plot_discharge_spain.png", dpi=300)
    plt.tight_layout()
    plt.show()

# Load and process your data
data = xr.open_dataset("/work/lealroja/Q_global_hist/mRM_Fluxes_States_2024_10_31_to_2024_10_31.nc")
flowacc = xr.open_dataarray("mRM_ulysses_6min_fAcc.nc")
# Calculate mean over time and mask low flow accumulation values
data1_array = data.mean('time')['Qrouted'].values
data1_array[flowacc.transpose() < 1000 ] = np.nan
# Extract latitude, longitude, and data values
lat = data.lat.values
lon = data.lon.values
data_values = data1_array

# Call the function to create the plot
create_orographic_plot_with_cartopy(data_values, lat, lon)
