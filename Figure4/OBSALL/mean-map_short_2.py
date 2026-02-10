# Written by Juniper Tyree
# Edited by Lauri Tuppi
# Feb 2026

from pathlib import Path
from string import ascii_lowercase

import matplotlib as mpl
import numpy as np
import pandas as pd
from cartopy import crs as ccrs, feature as cfeature
from matplotlib import gridspec
from matplotlib import pyplot as plt
from matplotlib import colors as mcolors

import pickle

def plot_station_map(ax, station_stats: list[pd.DataFrame]):
    se_factor = 2 * np.sqrt(1 + 1 / len(station_stats))

    # add map features
    ax.add_feature(cfeature.COASTLINE, linewidth=0.7)
    ax.add_feature(cfeature.BORDERS, linestyle=":", linewidth=0.5)
    ax.set_global()

    # pick the bins for the colormap
    levels = (
        [-diff_range]
        + list(
            np.linspace(
                -diff_range / 2, diff_range / 2, diff_levels + (1 - diff_levels % 2) - 2
            )
        )
        + [diff_range]
    )
    cmap = plt.get_cmap("RdBu_r", len(levels) + 1)
    norm = mcolors.BoundaryNorm(boundaries=levels, ncolors=cmap.N, extend=diff_extend)

    mean_ann_mean_sim = sum(s["ann_mean_sim"] for s in station_stats) / len(
        station_stats
    )

    # significance mask (compare model values vs obs CI)
    sig_mask = (
        mean_ann_mean_sim
        < (
            station_stats[0]["ann_mean_obs"]
            - station_stats[0]["ann_se_obs"] * se_factor
        )
    ) | (
        mean_ann_mean_sim
        > (
            station_stats[0]["ann_mean_obs"]
            + station_stats[0]["ann_se_obs"] * se_factor
        )
    )

    # scatter plot the stations
    # non-significant (triangles)
    ax.scatter(
        station_list.loc[mean_ann_mean_sim.index][~sig_mask]["longitude"],
        station_list.loc[mean_ann_mean_sim.index][~sig_mask]["latitude"],
        c=mean_ann_mean_sim.loc[~sig_mask]
        - station_stats[0].loc[~sig_mask]["ann_mean_obs"],
        cmap=cmap,
        norm=norm,
        s=30,
        marker="^",
        transform=ccrs.PlateCarree(),
        edgecolors="grey",
        lw=0.5,
    )
    # significant (circles)
    sc = ax.scatter(
        station_list.loc[mean_ann_mean_sim.index][sig_mask]["longitude"],
        station_list.loc[mean_ann_mean_sim.index][sig_mask]["latitude"],
        c=mean_ann_mean_sim.loc[sig_mask]
        - station_stats[0].loc[sig_mask]["ann_mean_obs"],
        cmap=cmap,
        norm=norm,
        s=30,
        marker="o",
        transform=ccrs.PlateCarree(),
        edgecolors="grey",
        lw=0.5,
    )

    # create custom legend with black markers
    legend_elements = [
        mpl.lines.Line2D(
            [0],
            [0],
            marker="o",
            color="black",
            linestyle="",
            markersize=5,
            label="significant",
        ),
        mpl.lines.Line2D(
            [0],
            [0],
            marker="^",
            color="black",
            linestyle="",
            markersize=5,
            label="not significant",
        ),
    ]
    ax.legend(handles=legend_elements, loc="lower left")

    return sc

# variable id
variable = "2t"
# variable name
variable_name = "2m temperature"
# variable unit, can use LaTex
variable_unit = r"$\degree$C"
plots = Path("plots")

# output format
output_format = "png"

# dict of models (model ID -> display name) to compare with the observations
# icon-hist has wrongly encoded 2d values, so we exclude it

models = {
    **({"icon_hist_o25-1": "ICON"} if variable not in ["2dd"] else {}),
    "ifs-nemo_hist_o25-1": "IFS-NEMO",
    "ifs-fesom_hist_o25-1": "IFS-FESOM",
}

# dict of combined models (model ID -> list of individual model IDs)

combined_models = {
    **({"icon_hist_o25-1": ["icon_hist_o25-1"]} if variable not in ["2dd"] else {}),
    "ifs-nemo_hist_o25-1": ["ifs-nemo_hist_o25-1"],
    "ifs-fesom_hist_o25-1": ["ifs-fesom_hist_o25-1"],
}

# list of all individual model IDs
all_models = sorted(set([m for ms in combined_models.values() for m in ms]))

# paths to the station metadata files
station_list_path = Path("SYNOP") / "synop_station_list.txt"

station_list = (
    pd.read_csv(station_list_path, sep=r"\s+")
    .rename(
        {
            "station@hdr_integer": "id",
            "longitude@hdr:real": "longitude",
            "latitude@hdr:real": "latitude",
            "elevation@hdr:real": "elevation",
        },
        axis="columns",
    )[["id", "longitude", "latitude", "elevation"]]
    .set_index("id")
)
n_stations = len(station_list)

with open('mean-map-model_results.pickle', 'rb') as f:
    model_results = pickle.load(f)
    
diff_min = 0.0
diff_max = 0.0

for station_stats in model_results.values():
    diff_min = min(
        diff_min,
        (station_stats["ann_mean_sim"] - station_stats["ann_mean_obs"]).min(),
    )
    diff_max = max(
        diff_max,
        (station_stats["ann_mean_sim"] - station_stats["ann_mean_obs"]).max(),
    )

diff_abs = max(abs(diff_min), abs(diff_max))
diff_mag = 10 ** np.floor(np.log10(diff_abs) - 1)

diff_levels=16
#diff_levels = int(np.ceil(diff_abs / diff_mag))
#diff_range = diff_levels * diff_mag

diff_range = 7.0
#while diff_levels > 20:
#    diff_levels //= 2
#diff_levels = max(2, diff_levels)

diff_extend = {
    (True, True): "both",
    (True, False): "min",
    (False, True): "max",
    (False, False): "neither",
}[(diff_min < -diff_range, diff_max > diff_range)]

float(diff_min), float(diff_max), float(diff_range), diff_extend

# === Layout: 3 map rows + 1 bottom colorbar row ===
fig = plt.figure(figsize=(10, 12))
gs = gridspec.GridSpec(
    4, 1,
    height_ratios=[1, 1, 1, 0.12],   # bottom row is small for the colorbar
    hspace=0.25
)

print(models.items())
for i, (model, model_name) in enumerate(models.items()):
    a = ascii_lowercase[i]

    # Single-column gridspec: use gs[i] (not gs[i, 0])
    ax1 = fig.add_subplot(gs[i], projection=ccrs.Robinson())

    # compute the statistics for each individual model in a combined model,
    # then average the statistics
    mean_ann_bias = np.mean(
        [
            np.mean(model_results[m]["ann_mean_sim"] - model_results[m]["ann_mean_obs"])
            for m in combined_models[model]
        ]
    )
    mean_ann_abs_bias = np.mean(
        [
            np.mean(
                np.abs(
                    model_results[m]["ann_mean_sim"] - model_results[m]["ann_mean_obs"]
                )
            )
            for m in combined_models[model]
        ]
    )
    ann_bias_positive = np.mean(
        [
            np.mean(
                (model_results[m]["ann_mean_sim"] - model_results[m]["ann_mean_obs"])
                > 0
            )
            for m in combined_models[model]
        ]
    )

    ax1.set_title(
        f"{a}) {model_name} ({np.round(mean_ann_bias, 2)}, {np.round(mean_ann_abs_bias, 2)}, {int(np.round(ann_bias_positive * 100))}%)",
        loc="center",
    )

    sc = plot_station_map(ax1, [model_results[m] for m in combined_models[model]])

# --- Remove the old right-side colorbar axes (ax2). Keep only the bottom bar. ---
# ax2 = fig.add_subplot(gs[:, 1])  # <-- REMOVE THIS LINE

# --- Bottom colorbar (short) ---
cax = fig.add_subplot(gs[3])  # bottom row

#levels = (
#    [-diff_range]
#    + list(
#        np.linspace(
#            -diff_range / 2, diff_range / 2, diff_levels + (1 - diff_levels % 2) - 2
#        )
#    )
#    + [diff_range]
#)

diff_levels=16
levels = [-7.0, -3.5, -3.0, -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 7.0]
#print(diff_levels)
#print(levels)
cmap = plt.get_cmap("RdBu_r", len(levels) + 1)
norm = mcolors.BoundaryNorm(boundaries=levels, ncolors=cmap.N, extend=diff_extend)

cbar = fig.colorbar(
    sc,
    cax=cax,
    cmap=cmap,
    norm=norm,
    extend=diff_extend,
    boundaries=levels,
    ticks=levels,
    orientation="horizontal",
    label="2m Temperature Bias ($^{o}C$)",
)

# Add black boundary lines between tiles (horizontal colorbar -> vertical lines)
for boundary in levels:
    cbar.ax.vlines(boundary, *cbar.ax.get_ylim(), color="black", linewidth=0.7)

# Make the colorbar shorter than the panel width (optional fine-tuning)
# This centers a shortened bar; adjust 0.2 and 0.6 as needed
pos = cax.get_position()
cax.set_position([0.24, pos.y0, 0.51, pos.height])

plt.tight_layout()
# No horizontal space between subplots in a single-column layout needed
# plt.subplots_adjust(wspace=-0.2)  # optional to remove or keep without effect

plt.savefig(plots / f"map-mean-o25_1{variable}.{output_format}", dpi=300)
plt.show()
