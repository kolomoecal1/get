import smbus
import time
import save_to_gr


class MCP3021:
    def __init__(self, dynamic_range, verbose=False):
        self.bus = smbus.SMBus(1)
        self.dynamic_range = dynamic_range
        self.address = 0x4D
        self.verbose = verbose

    def deinit(self):
        self.bus.close()

    def get_number(self):
        data = self.bus.read_word_data(self.address, 0)
        lower_data_byte = data >> 8
        upper_data_byte = data & 0xFF
        number = (upper_data_byte << 6) | (lower_data_byte >> 2)
        if self.verbose:
            print(f"Принятые данные: {data}, Старший байт: {upper_data_byte:x}, Младший байт: {lower_data_byte:x}, Число: {number}")
        return number

    def get_voltage(self):
        number = self.get_number()
        # MCP3021 - 10-битный АЦП (1024 уровня)
        voltage = (number / 1023.0) * self.dynamic_range
        return voltage

if __name__ == "__main__":
    # Динамический диапазон АЦП (напряжение на контакте PWR блока AUX)
    dynamic_range = 5.2  # Вольт

    filename = 'data10-bit.txt'
    with open(filename, 'w', encoding='utf-8') as file:
        pass




    
    adc = None
    try:
        adc = MCP3021(dynamic_range)
        while True:
            voltage = adc.get_voltage()
            print(f"Измеренное напряжение: {voltage:.3f} В")
            save_to_gr.write_to_txt_simple(voltage, filename)
            time.sleep(1)
    finally:
        if adc:
            adc.deinit()
