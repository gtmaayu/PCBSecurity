import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file into a DataFrame
df = pd.read_csv("../RecordedVideos/fittingParameters.csv")

# Create lists to store data for different Board Types
baseline_components = []
baseline_a_rise = []
microphone_components = []
microphone_a_rise = []

component_names = {
    'samd': "SAMD11",
    "atmega":"ATMega4809",
    "3v3reg": "Voltage Regulator",
    "buck": "Buck Converter",
    "usbesd": "USB Voltage Diode",
    "fullboard": "Full Board"
}

# Iterate over rows and separate data based on Board Type
for index, row in df.iterrows():
    if row['Board Type'] == 'baseline':
        baseline_components.append(component_names[row['Component']])
        baseline_a_rise.append(row['a_rise'])
    elif row['Board Type'] == 'microphone':
        microphone_components.append(component_names[row['Component']])
        microphone_a_rise.append(row['a_rise'])

# Create a scatter plot
plt.figure(figsize=(10, 6))
plt.scatter(baseline_components, baseline_a_rise, color='green', label='Baseline', alpha=0.5)
plt.scatter(microphone_components, microphone_a_rise, color='red', label='Microphone', alpha=0.5)

# Customize the plot
plt.xlabel('Component')
plt.ylabel('a_rise')
plt.legend()
plt.grid(True)

# Show plot
plt.tight_layout()
plt.show()
