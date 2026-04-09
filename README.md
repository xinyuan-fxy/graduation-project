# Smart Sensors for a Guitar Protection Environmental Monitoring System

**Author:** Xinyuan Feng  
**Degree:** BEng Robotics — Heriot-Watt University  
**Supervisor:** Dr. Theodoros Georgiou

---

## Project Overview

Acoustic guitars made from solid wood are highly susceptible to environmental damage caused by fluctuations in humidity, temperature, and light exposure. This project builds a low-cost, offline environmental monitoring system using a **BBC Micro:bit V2** and a **Kitronik Air Quality Board** to continuously log temperature, humidity, and light data across six indoor locations, then performs statistical analysis to identify the safest storage spot for a guitar.

**Safe storage thresholds (manufacturer recommendation):**
- Humidity: **40 – 60% RH**
- Temperature: **below 30 °C**
- Light: no direct sunlight

---

## Repository Structure

```
graduation-project/
│
├── code/
│   ├── microbit-main.hex       # Firmware to flash onto the Micro:bit
│   └── generate_charts.py      # Python script to visualise and analyse data
│
├── data5/                      # Sensor readings sampled every 5 seconds (~9.8 h)
│   ├── Hallway End/
│   ├── Hallway Middle/
│   ├── bedroom  far away from door/
│   ├── bedroom middle/
│   ├── kitchen  far away from door/
│   └── kitchen middle/
│
├── data30/                     # Sensor readings sampled every 30 seconds (~24 h)
│   ├── Hallway End/
│   ├── Hallway Middle/
│   ├── bedroom far/
│   ├── bedroom middle/
│   ├── kitchen  far away from door/
│   └── kitchen middle/
│
├── image/                      # Reference images and dissertation figures
├── image5/                     # Generated charts from data5 (output)
├── image30/                    # Generated charts from data30 (output)
├── comparison_chart.png        # Cross-phase comparison chart (output)
└── Xinyuan Feng Final Dissertation Document .docx
```

Each subfolder under `data5/` and `data30/` contains one CSV file with three sensor columns:

| Column | Description |
|--------|-------------|
| `Time (seconds)` | Elapsed time since logging started |
| `Temp` | Temperature in °C |
| `Humid` | Relative humidity in % |
| `Light` | Light intensity (0 – 255, read from Micro:bit LED matrix) |

---

## Part 1 — Hardware: Flashing the Micro:bit

### What you need

| Item | Details |
|------|---------|
| BBC Micro:bit V2 | The microcontroller |
| Kitronik Air Quality Board | Provides temperature and humidity sensors; Micro:bit slots in on top |
| USB-A to Micro-USB cable | For flashing firmware and extracting data |
| Small battery pack (optional) | Powers the device during field deployment |

### Steps

1. Connect the Micro:bit to your computer via USB.
2. It will appear as a removable drive called **MICROBIT**.
3. Copy `code/microbit-main.hex` onto that drive.
4. The Micro:bit reboots automatically — the firmware is now running.
5. The LED matrix will display a **happy face** when all conditions are within safe thresholds, or a **sad face** when humidity is outside 40–60 % or temperature exceeds 30 °C.

### Data collection

The firmware logs one reading per sampling interval to the Micro:bit's internal flash memory.

| Dataset | Sampling interval | Typical duration | Approx. data points |
|---------|-----------------|-----------------|---------------------|
| `data5`  | every **5 seconds** | ~9.8 hours | ~5 800 per location |
| `data30` | every **30 seconds** | ~24 hours | ~2 800 per location |

> **Note:** Only one Micro:bit was available, so each location was tested sequentially on different days.

### Extracting the data

1. After a monitoring session, reconnect the Micro:bit to your computer via USB.
2. Open the **MY_DATA.HTM** file that appears on the MICROBIT drive in a browser.
3. Download the data as a CSV file.
4. Place the CSV inside the matching subfolder under `data5/` or `data30/`, named after the location (e.g. `bedroom far/bedroom far.csv`).

---

## Part 2 — Software: Generating Charts and Statistics

### Requirements

- Python 3.8 or later
- The following packages:

```bash
pip install pandas matplotlib numpy scipy
```

### Running the script

```bash
cd graduation-project
python code/generate_charts.py
```

That's it. The script automatically finds every CSV under `data5/` and `data30/`, generates all charts, and saves them to the corresponding output directories.

### Outputs

#### Per dataset (`image5/` and `image30/`)

| File | Description |
|------|-------------|
| `linechart.png` | All 6 locations overlaid on one figure (3 subplots: Temp, Humidity, Light vs time in hours). Includes a red dashed line at 30 °C and a green shaded band for the 40–60 % humidity safe zone. |
| `barchart.png` | Mean ± standard deviation bar chart for all 6 locations. The optimal location (Bedroom Far) is highlighted with a border and an "Optimal Location" annotation arrow. |
| `stats_results.csv` | Full statistical results table (machine-readable). |
| `stats_table.png` | Same table rendered as an image — ready to paste into a report. Rows that are statistically significant (p < 0.05) are highlighted in orange. |

#### Project root

| File | Description |
|------|-------------|
| `comparison_chart.png` | Side-by-side grouped bar chart comparing Phase 1 (5 s) and Phase 2 (30 s) mean values for every location and metric. |

### What statistics are computed

| Test | Purpose |
|------|---------|
| **One-Way ANOVA** | Tests whether Temp, Humidity, or Light differs significantly across the 6 locations. |
| **Levene's Test** | Tests whether the *variance* of Temp and Humidity differs across locations (consistency check). |
| **Welch's t-test** | Pairwise comparison of Bedroom Far vs every other location for Temp and Humidity. |
| **Cohen's d** | Effect size — measures how *practically* meaningful the Bedroom Far advantage is. |

---

## Key Findings

- **Bedroom (Far from Door)** was identified as the most stable and safest storage location across both phases:
  - Lowest humidity variability (std ≈ 0.9 % in Phase 1, 1.6 % in Phase 2)
  - Stable temperature (~22–23 °C)
  - Zero light exposure
- **Kitchen locations** showed the highest environmental volatility and are unsuitable for guitar storage.
- **Hallway locations** were dangerously dry (mean humidity as low as 18 %).
- All tested locations fell **below** the 40 % lower humidity threshold — passive monitoring alone is insufficient; active humidification is also required.

---

## Reproducing the Full Experiment

1. Flash `code/microbit-main.hex` onto the Micro:bit.
2. Place the device (with Kitronik board attached) in the target location.
3. Leave it running for the desired duration (≈10 h for 5-second sampling, ≈24 h for 30-second sampling).
4. Extract the CSV from the Micro:bit and place it in the correct subfolder.
5. Run `python code/generate_charts.py` to regenerate all charts and statistics.
