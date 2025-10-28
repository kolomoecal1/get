import smbus
import time

class MCP3021:
    def __init__(self, dynamic_range, address=0x4D, bus_num=1, verbose=False):
        self.bus = smbus.SMBus(bus_num)
        self.verbose = verbose
        self.dynamic_range = dynamic_range
        self.address = address
    
    def deinit(self):
        self.bus.close()
    
    def get_number(self):
        data = self.bus.read_word_data(self.address, 0)
        value = ((data & 0xFF) << 8) | ((data >> 8) & 0xFF)
        value = (value >> 2) & 0x3FF 
        
        if self.verbose:
            print(f"Принятые данные: 0x{data:04X}, преобразованное значение: {value}")
        
        return value
    
    def get_voltage(self):
        number = self.get_number()
        return (number / 1023.0) * self.dynamic_range

if __name__ == "__main__":
    try:
        adc = MCP3021(5.18, verbose=True)
        
        while True:
            voltage = adc.get_voltage()
            print(f"Напряжение: {voltage:.3f} V")
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nПрограмма остановлена пользователем")
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        adc.deinit()