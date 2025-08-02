# Install dependencies before running:
# pip install streamlit numpy-stl

import streamlit as st
from stl import mesh
import numpy as np

def manual_calculator():
    st.header('Manual 3D Print Cost Calculator')
    filament_type = st.selectbox("Filament type", ["PLA", "ABS", "PETG", "Nylon", "Other"])
    filament_weight = st.number_input("Filament used (grams)", min_value=0.0)
    filament_cost_kg = st.number_input("Filament cost per kg", min_value=0.0)
    print_time = st.number_input("Print time (hours)", min_value=0.0)
    electricity_cost = st.number_input("Electricity cost per hour (optional)", min_value=0.0, value=0.0)

    if st.button("Calculate (Manual)"):
        filament_cost = (filament_weight / 1000) * filament_cost_kg
        total_electricity = print_time * electricity_cost
        total_cost = filament_cost + total_electricity

        st.success(f"Estimated cost: {total_cost:.2f} (Filament: {filament_cost:.2f}, Electricity: {total_electricity:.2f})")

def stl_calculator():
    st.header('STL-based 3D Print Cost Estimator')

    uploaded_file = st.file_uploader("Upload STL file", type=["stl"])
    if uploaded_file is not None:
        st.write("Note: This method estimates filament use/weight based on model volume and selected print parameters. For exact slicing/print time, integrate with a slicer.")

        # Slicing parameters
        layer_height = st.number_input("Layer height (mm)", min_value=0.05, max_value=1.0, value=0.2)
        infill = st.slider("Infill percentage", min_value=0, max_value=100, value=20)
        shell_count = st.number_input("Number of solid perimeters/shells", min_value=1, value=2)
        filament_density = st.number_input("Filament density (g/cm³)", value=1.24) # PLA default
        filament_cost_kg = st.number_input("Filament cost per kg", min_value=0.0)
        print_time = st.number_input("Estimated print time (hours)", min_value=0.0)
        electricity_cost = st.number_input("Electricity cost per hour (optional)", min_value=0.0, value=0.0)

        if st.button("Estimate (from STL)"):
            # Process STL for volume
            stl_mesh = mesh.Mesh.from_file(uploaded_file)
            volume, _, _ = stl_mesh.get_mass_properties()
            volume_cm3 = volume / 1000  # convert mm^3 to cm^3

            # Basic estimate: infill reduces total plastic used, shells add back some
            shell_vol_factor = 1 + (shell_count * 0.05)   # crude addition for shell walls
            infill_ratio = infill / 100.0
            total_volume_cm3 = volume_cm3 * (infill_ratio + (1-infill_ratio)*0.25) * shell_vol_factor

            weight_g = total_volume_cm3 * filament_density
            filament_cost = (weight_g / 1000) * filament_cost_kg
            total_electricity = print_time * electricity_cost
            total_cost = filament_cost + total_electricity

            st.info(f"Model Volume: {volume_cm3:.2f} cm³")
            st.info(f"Estimated filament used: {weight_g:.2f} grams")
            st.success(f"Estimated cost: {total_cost:.2f} (Filament: {filament_cost:.2f}, Electricity: {total_electricity:.2f})")

def main():
    st.title("3D Printer Cost Calculator")
    option = st.radio("Select Calculation Mode", ["Manual Input", "STL File Upload"])
    if option == "Manual Input":
        manual_calculator()
    else:
        stl_calculator()

if __name__ == '__main__':
    main()
