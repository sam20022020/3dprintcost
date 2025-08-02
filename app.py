# requirements: streamlit, numpy-stl, numpy
import streamlit as st
from stl import mesh
import numpy as np
import tempfile

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
        st.write("This calculator estimates filament use/weight and cost based on STL model volume and your print parameters.")

        # Parameters for calculations
        layer_height = st.number_input("Layer height (mm)", min_value=0.05, max_value=1.0, value=0.2)
        infill = st.slider("Infill percentage", min_value=0, max_value=100, value=20)
        shell_count = st.number_input("Number of solid perimeters/shells", min_value=1, value=2)
        filament_density = st.number_input("Filament density (g/cm³)", value=1.24)
        filament_cost_kg = st.number_input("Filament cost per kg", min_value=0.0)
        print_time = st.number_input("Estimated print time (hours)", min_value=0.0)
        electricity_cost = st.number_input("Electricity cost per hour (optional)", min_value=0.0, value=0.0)

        if st.button("Estimate Cost (from STL)"):
            volume_mm3 = get_stl_volume(uploaded_file)
            volume_cm3 = volume_mm3 / 1000.0
            shell_vol_factor = 1 + (shell_count * 0.05)  # crude shell estimate
            infill_ratio = infill / 100.0
            estimated_volume_cm3 = volume_cm3 * (infill_ratio + (1-infill_ratio)*0.25) * shell_vol_factor

            weight_g = estimated_volume_cm3 * filament_density
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
