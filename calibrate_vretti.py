import subprocess
import time

from printer_tspl import PrinterVretti420B

def main():
    printer = PrinterVretti420B()

    print("Calibrating label size...")
    print("Several labels should feed.")
    printer.calibrate(88.4, 5)

    input("Once it stops, roll back the label reel,\nclose the lid, and press enter...")

    printer.home()

    print("")
    print("One label should feed. This is wasted :-(")
    print("")

    printer.close()

    print("The label alignment should now be calibrated :-)")
    input("Press enter to exit")


if __name__ == "__main__":
    main()
