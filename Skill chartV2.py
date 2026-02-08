import os
import gspread
import pandas as pd
from google.oauth2 import service_account
import matplotlib.pyplot as plt
import numpy as np

# path setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Auth
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = service_account.Credentials.from_service_account_file(
    os.path.join(BASE_DIR, "EXP_chart.json"), scopes=SCOPES
)
client = gspread.authorize(creds)

# Open spreadsheet
spreadsheet = client.open_by_key("1Mt7rbBPdQtlDWfsiExPumAPrRdzp_LZBFlfc0v6V3UM")
responses_sheet = spreadsheet.worksheet("Stats")
rows = responses_sheet.get_all_values()

# Create DataFrame
df = pd.DataFrame(rows[1:], columns=rows[0])

# Clean data
df["EXP"] = pd.to_numeric(df["EXP"], errors="coerce").fillna(0)

# Dashboard Math (Fixed filter name to match spreadsheet)
Total_Level = df[df["Abilities"] == "Total Level"]["EXP"].sum()
Debuff_Level = df[df["Abilities"] == "Debuffs"]["EXP"].sum()

Abilities_summary = df.groupby(["Abilities", "Skills"])["EXP"].sum()
print("\nEXP Summary:\n", Abilities_summary)

# Time Series
df["Date"] = pd.to_datetime(df["Date"])
df.set_index("Date", inplace=True)

monthly_Debuff = df[df["Abilities"] == "Debuffs"]["EXP"].resample("MS").sum()
print("\nMonthly Debuff Total:\n", monthly_Debuff)

# --- RADAR CHART LOGIC & VISUAL ADJUSTMENTS (Fixed filter name and style) ---
# Filter by 'Total Level' to plot main skills
debuff_data = df[df["Abilities"] == "Total Level"].groupby("Skills")["EXP"].sum()
labels = debuff_data.index.tolist()
values = debuff_data.values.tolist()

if len(values) > 0:
	# Close the loop for the radar chart
	values += values[:1]
	num_vars = len(labels)
	angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
	angles += angles[:1]

	fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
	ax.set_theta_zero_location('N')  # Start "Power" at the top
	ax.plot(angles, values, color="red", linewidth=2, linestyle="solid")
	ax.fill(angles, values, color="#FFA500", alpha=0.4)  # Orange/Yellow fill
	plt.xticks(angles[:-1], labels, color="grey", size=10)
	ax.set_yticklabels([])  # Hide radial number labels
	ax.spines['polar'].set_visible(False)  # Hide the outer boundary circle

	plt.title("Skill Proficiencies", size=15, y=1.1)
	plt.show()

print(f"Total Level: {Total_Level}")
print(f"Total Debuffs: {Debuff_Level}")
