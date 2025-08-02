# requirements: streamlit, numpy-stl, numpy
import streamlit as st
from stl import mesh
import numpy as np
import tempfile

# List of popular printers and their power usage (Watts)
PRINTER_MODELS = [
    # Bambu Lab
    {'name': 'Bambu Lab X1 Carbon', 'watts': 140, 'vol': '256×256×256'},
    {'name': 'Bambu Lab P1S', 'watts': 150, 'vol': '256×256×256'},
    {'name': 'Bambu Lab P1P', 'watts': 130, 'vol': '256×256×256'},
    {'name': 'Bambu Lab A1', 'watts': 100, 'vol': '256×256×256'},
    {'name': 'Bambu Lab A1 Mini', 'watts': 75, 'vol': '180×180×180'},
    {'name': 'Bambu Lab H2D', 'watts': 250, 'vol': 'Variable'},
    # Other popular printers
    {'name': 'Creality Ender 3 (V2/Pro)', 'watts': 150, 'vol': '220×220×250'},
    {'name': 'Prusa i3 MK3S+', 'watts': 120, 'vol': '250×210×210'},
    {'name': 'Anycubic Kobra', 'watts': 100, 'vol': '220×220×250'},
    {'name': 'Artillery Sidewinder X2', 'watts': 160, 'vol': '300×300×400'},
    {'name': 'Qidi X-Max', 'watts': 200, 'vol': '300×250×300'},
    {'name': 'MakerBot Replicator+', 'watts': 110, 'vol': '295×195×165'},
]

def get_printer_default_watt(printer_name):
    for p in PRINTER_MODELS:
        if p['name'] == printer_name:
            return p['watts']
    return 100  # Default if not found

def manual_calculator():
    st.header('Manual 3D Print Cost Calculator')

    filament_type = st.selectbox("Filament type", ["PLA", "ABS", "PETG", "Nylon", "Other"])
    filament_weight = st.number_input("Filament used (grams)", min_value=0.0)
    filament_cost_kg = st.number_input("Filament cost per kg", min_value=0.0)
    print_time = st.number_input("Print time (hours)", min_value=0.0)

    # Printer model selection and default wattage
    printer_names = [p['name'] for p in PRINTER_MODELS]
    selected_printer = st.selectbox("Select printer model", printer_names)
    default_watt = get_printer_default_watt(selected_printer)
    wattage = st.number_input("Printer power usage (watts)", min_value=10, max_value=3000,
                             value=default_watt)
    electricity_rate = st.number_input("Your electricity rate (per kWh)", min_value=0.0)

    if st.button("Calculate (Manual)"):
        filament_cost = (filament_weight / 1000) * filament_cost_kg
        electricity_kwh = (wattage / 1000) * print_time
        electricity_cost = electricity_kwh * electricity_rate
        total_cost = filament_cost + electricity_cost

        st.success(f"Estimated cost: {total_cost:.2f} (Filament: {filament_cost:.2f}, "
                   f"Electricity: {electricity_cost:.2f})")

def get_stl_volume(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_file_path = tmp_file.name
    stl_mesh = mesh.Mesh.from_file(tmp_file_path)
    volume_mm3, _, _ = stl_mesh.get_mass_properties()
    return volume_mm3

def stl_calculator():
    st.header('STL-based 3D Print Cost Estimator')
    uploaded_file = st.file_uploader("Upload STL file", type=["stl"])
    if uploaded_file is not None:
        st.write("This calculator estimates filament/cost based on STL model volume and your print parameters.")

        # Parameters for calculations
        layer_height = st.number_input("Layer height (mm)", min_value=0.05, max_value=1.0, value=0.2)
        infill = st.slider("Infill percentage", min_value=0, max_value=100, value=20)
        shell_count = st.number_input("Number of solid perimeters/shells", min_value=1, value=2)
        filament_density = st.number_input("Filament density (g/cm³)", value=1.24)
        filament_cost_kg = st.number_input("Filament cost per kg", min_value=0.0)

        print_time = st.number_input("Estimated print time (hours)", min_value=0.0)
        # Printer model selection and default wattage
        printer_names = [p['name'] for p in PRINTER_MODELS]
        selected_printer = st.selectbox("Select printer model", printer_names)
        default_watt = get_printer_default_watt(selected_printer)
        wattage = st.number_input("Printer power usage (watts)", min_value=10, max_value=3000,
                                 value=default_watt)
        electricity_rate = st.number_input("Your electricity rate (per kWh)", min_value=0.0)

        if st.button("Estimate Cost (from STL)"):
            volume_mm3 = get_stl_volume(uploaded_file)
            volume_cm3 = volume_mm3 / 1000.0
            shell_vol_factor = 1 + (shell_count * 0.05)  # crude shell estimate
            infill_ratio = infill / 100.0
            estimated_volume_cm3 = volume_cm3 * (infill_ratio + (1-infill_ratio)*0.25) * shell_vol_factor

            weight_g = estimated_volume_cm3 * filament_density
            filament_cost = (weight_g / 1000) * filament_cost_kg
            electricity_kwh = (wattage / 1000) * print_time
            electricity_cost = electricity_kwh * electricity_rate
            total_cost = filament_cost + electricity_cost

            st.info(f"Model Volume: {volume_cm3:.2f} cm³")
            st.info(f"Estimated filament used: {weight_g:.2f} grams")
            st.success(f"Estimated cost: {total_cost:.2f} (Filament: {filament_cost:.2f}, "
                       f"Electricity: {electricity_cost:.2f})")

def main():
    st.title("3D Printer Cost Calculator")
    option = st.radio("Select Calculation Mode", ["Manual Input", "STL File Upload"])
    if option == "Manual Input":
        manual_calculator()
    else:
        stl_calculator()

if __name__ == '__main__':
    main()
