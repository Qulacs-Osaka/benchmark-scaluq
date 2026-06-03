set -eux

# Single-thread sweep (n <= 18) for all CPU libraries, complementing the
# multi-thread sweep in execall.sh. Results are written to f64_st.json in each
# library directory and plotted as dashed curves by plot.py.

cd scaluq/
./exec_st.sh f64
cd -
cd qulacs/
./exec_st.sh f64
cd -
cd qiskit-aer/
./exec_st.sh f64
cd -
