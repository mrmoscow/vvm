import array
import time
import socket
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

#=====================================================================================
#This code is wroten by SFYen at 2025/05/13, by merge AllanVVM.py (sfyen) and allandev.py (Johnson)
#The code will ask input, and will output 3 files. (txt, phase png, ASD png)


# === Function to read phase from the phase detector ===
def VVM_MEAS():
    ip="192.168.1.204"
    sockGPIB = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    sockGPIB.settimeout(1.0)
    sockGPIB.connect((ip, 1234))
    sockGPIB.send(b"SENSE PHASE\n")
    sockGPIB.send(b"FORM POL\n")
    sockGPIB.send(b"MEAS? PHASE\n")
    sockGPIB.send(b"++read eoi\n")
    try:
        phase = sockGPIB.recv(8192)
        phase = phase.decode().rstrip('\r\n')
    except socket.timeout:
        phase = ""
    sockGPIB.send(b"SENSE BA\n")
    sockGPIB.send(b"FORM LIN\n")
    sockGPIB.send(b"MEAS? BA\n")
    sockGPIB.send(b"++read eoi\n")
    try:
        ba = sockGPIB.recv(8192)
        ba = ba.decode().rstrip('\r\n')
    except socket.timeout:
        ba = ""
    sockGPIB.close()
    return phase, ba


#==============================================================================
# === Main execution ===
if __name__ == '__main__':
    print("=== Phase Data Collection and Allan Deviation Plotter ===")
    tottime = int(input("Enter total measurement time (seconds): "))
    #numRepeats = int(input("Enter number of repeats: "))
    numRepeats=1
    LO = input("Enter LO frequency (GHz): ")
    #powerRF = input("Enter RF power level: ")
    data_filename = input("Enter output filename for phase data (.txt): ")
    #png_filename = input("Enter output filename for phase plot (.png): ")


    timenow = datetime.now().strftime("%d%m%y_%H%M%S")
    phase_list = []
    time_list = []

    sample_period = 0.5
    for j in range(1, numRepeats + 1):
        outfile = open(data_filename, "w")
        timecount = 0
        print("\nData collection start:..")
        #start_time = time.perf_counter()
        for i in range(tottime * 2):
            loop_start = time.perf_counter()
            phase, ba = VVM_MEAS()
            timestamp = time.strftime("%Y/%m/%d_%p_%I:%M:%S")
            outfile.write(f"{timestamp:30s} {timecount:8.1f} {phase:20s} {ba:20s}\n")
            print(f"{timestamp:30s} {timecount:8.1f} {phase:20s} {ba:20s}")
            time_list.append(timecount)
            try:
                phase_list.append(float(phase.replace('+', '').replace('E', 'e')))
            except ValueError:
                phase_list.append(0.0)
            timecount +=sample_period
            elapsed = time.perf_counter() - loop_start
            sleep_time = max(0, sample_period - elapsed)
            time.sleep(sleep_time)

        outfile.close()

    print("\nData collection complete. Generating plots...")



    # === Plot Phase vs Time ===
    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax1.plot(time_list, phase_list, 'b.', markersize=2)
    ax1.set_xlabel("Time (seconds)")
    ax1.set_ylabel("Phase (degrees)")
    ax1.set_title(f"Phase vs Time (LO = {LO} GHz)")
    ax1.grid(True)
    png_filename = data_filename.replace('.txt', '_Phase.png')
    plt.savefig(png_filename)
    #plt.show()

    # === Compute Allan Deviation ===
    f0 = float(LO) * 1e9
    phase_rad = np.deg2rad(phase_list)
    tau0 = 0.5
    N = len(phase_rad)
    taus, adev = [], []

    for m in range(1, N // 3):
        tau = m * tau0
        if tau > 300:
            break
        diffs = phase_rad[2*m:] - 2 * phase_rad[m:-m] + phase_rad[:-2*m]
        sigma2 = np.sum(diffs ** 2) / (2 * tau**2 * (N - 2*m))
        sigma = np.sqrt(sigma2) / (2 * np.pi * f0)
        taus.append(tau)
        adev.append(sigma)

    # Optional target tau
    target_tau = 100.0
    m_target = int(target_tau / tau0)
    if 2 * m_target < N:
        diffs_target = phase_rad[2*m_target:] - 2 * phase_rad[m_target:-m_target] + phase_rad[:-2*m_target]
        sigma2_target = np.sum(diffs_target ** 2) / (2 * target_tau**2 * (N - 2*m_target))
        sigma_target = np.sqrt(sigma2_target) / (2 * np.pi * f0)
        taus.append(target_tau)
        adev.append(sigma_target)

    taus, adev = zip(*sorted(zip(taus, adev)))

    # === Plot Allan Deviation ===
    fig2, ax2 = plt.subplots(figsize=(6, 7))
    ax2.loglog(taus, adev, 'r-')
    ax2.set_xlabel("T (sec)")
    ax2.set_ylabel("Allan deviation")
    ax2.set_title(f"Allan Deviation (LO = {LO} GHz)")
    ax2.grid(True, which='both')
    plt.tight_layout()
    asd_filename = data_filename.replace('.txt', '_ASD.png')
    plt.savefig(asd_filename)
    plt.show()
    print(f"\nSaved phase plot as: {png_filename}")
    print(f"Saved Allan deviation plot as: {asd_filename}")

