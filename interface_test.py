import json
import logging
import re
from pyats import aetest
from pyats.log.utils import banner
from genie.utils.diff import Diff
from rich.console import Console
from rich.table import Table

# ----------------
# Get logger for script
# ----------------

log = logging.getLogger(__name__)

# ----------------
# AE Test Setup
# ----------------
class common_setup(aetest.CommonSetup):
    """Common Setup section"""
# ----------------
# Connected to devices
# ----------------
    @aetest.subsection
    def connect_to_devices(self, testbed):
        """Connect to all the devices"""
        testbed.connect()
# ----------------
# Mark the loop for Input Discards
# ----------------
    @aetest.subsection
    def loop_mark(self, testbed):
        aetest.loop.mark(Test_Interfaces, device_name=testbed.devices)

# ----------------
# Test Case #1
# ----------------
class Test_Interfaces(aetest.Testcase):
    """Parse the pyATS Learn Interface Data"""

    @aetest.test
    def setup(self, testbed, device_name):
        """ Testcase Setup section """
        # connect to device
        self.device = testbed.devices[device_name]
        # Loop over devices in tested for testing
    
    @aetest.test
    def get_pre_test_interface_data(self):
        self.parsed_interfaces = self.device.learn("interface")

    @aetest.test
    def create_pre_test_files(self):
        # Create .JSON file
        with open(f'{self.device.alias}_pyATS_Learn_Interface.json', 'w') as f:
            f.write(json.dumps(self.parsed_interfaces.info, indent=4, sort_keys=True))
    
    @aetest.test
    def test_interface_input_errors(self):
        # Test for input errors
        in_errors_threshold = 0
        self.failed_interfaces = {}
        table = Table(title="Interface Input Errors")
        table.add_column("Device", style="cyan")
        table.add_column("Interface", style="blue")
        table.add_column("Input Threshold", style="magenta")
        table.add_column("Input Errors", style="magenta")
        table.add_column("Passed/Failed", style="green")
        for self.intf,value in self.parsed_interfaces.info.items():
            if 'in_errors' in value['counters']:
                counter = value['counters']['in_errors']
                if int(counter) > in_errors_threshold:
                    table.add_row(self.device.alias,self.intf,str(in_errors_threshold),str(counter),'Failed',style="red")
                    self.failed_interfaces[self.intf] = int(counter)
                    self.interface_name = self.intf
                    self.error_counter = self.failed_interfaces[self.intf]                        
                else:
                    table.add_row(self.device.alias,self.intf,str(in_errors_threshold),str(counter),'Passed',style="green")
        
        # display the table
        console = Console(record=True)
        with console.capture() as capture:
            console.print(table,justify="center")
        log.info(capture.get())

        # should we pass or fail?
        if self.failed_interfaces:
            self.failed('Some interfaces have input errors')
        else:
            self.passed('No interfaces have input errors')

    @aetest.test
    def test_interface_input_crc_errors(self):
        # Test for input crc errors
        in_crc_errors_threshold = 0
        self.failed_interfaces = {}
        table = Table(title="Interface Input CRC Errors")
        table.add_column("Device", style="cyan")
        table.add_column("Interface", style="blue")
        table.add_column("Input CRC Threshold", style="magenta")
        table.add_column("Input CRC Errors", style="magenta")
        table.add_column("Passed/Failed", style="green")
        for self.intf,value in self.parsed_interfaces.info.items():
            if 'in_crc_errors' in value['counters']:
                counter = value['counters']['in_crc_errors']
                if int(counter) > in_crc_errors_threshold:
                    table.add_row(self.device.alias,self.intf,str(in_crc_errors_threshold),str(counter),'Failed',style="red")
                    self.failed_interfaces[self.intf] = int(counter)
                    self.interface_name = self.intf
                    self.error_counter = self.failed_interfaces[self.intf]                        
                else:
                    table.add_row(self.device.alias,self.intf,str(in_crc_errors_threshold),str(counter),'Passed',style="green")
        # display the table
        console = Console(record=True)
        with console.capture() as capture:
            console.print(table,justify="center")
        log.info(capture.get())        
        
        # should we pass or fail?
        if self.failed_interfaces:
            self.failed('Some interfaces have input CRC errors')
        else:
            self.passed('No interfaces have input CRC errors')

    @aetest.test
    def test_interface_output_errors(self):
        # Test for output errors
        output_errors_threshold = 0
        self.failed_interfaces = {}
        table = Table(title="Interface Output Errors")
        table.add_column("Device", style="cyan")
        table.add_column("Interface", style="blue")
        table.add_column("Output Error Threshold", style="magenta")
        table.add_column("Output Errors", style="magenta")
        table.add_column("Passed/Failed", style="green")
        for self.intf,value in self.parsed_interfaces.info.items():
            if 'out_errors' in value['counters']:
                counter = value['counters']['out_errors']
                if int(counter) > output_errors_threshold:
                    table.add_row(self.device.alias,self.intf,str(output_errors_threshold),str(counter),'Failed',style="red")
                    self.failed_interfaces[self.intf] = int(counter)
                    self.interface_name = self.intf
                    self.error_counter = self.failed_interfaces[self.intf]                        
                else:
                    table.add_row(self.device.alias,self.intf,str(output_errors_threshold),str(counter),'Passed',style="green")

        # display the table
        console = Console(record=True)
        with console.capture() as capture:
            console.print(table,justify="center")
        log.info(capture.get())

        # should we pass or fail?
        if self.failed_interfaces:
            self.failed('Some interfaces have output lost carrier errors')
        else:
            self.passed('No interfaces have output lost carrier errors')

    @aetest.test
    def test_interface_full_duplex(self):
        # Test for Full Duplex        
        duplex_threshold = "full"
        self.failed_interfaces = {}
        table = Table(title="Interface Duplex Mode")
        table.add_column("Device", style="cyan")
        table.add_column("Interface", style="blue")
        table.add_column("Interface Duplex Mode Threshold", style="magenta")
        table.add_column("Interface Duplex Mode", style="magenta")
        table.add_column("Passed/Failed", style="green")
        for self.intf,value in self.parsed_interfaces.info.items():
            if 'duplex_mode' in value:
                counter = value['duplex_mode']
                if counter != duplex_threshold:
                    table.add_row(self.device.alias,self.intf,str(duplex_threshold),str(counter),'Failed',style="red")
                    self.failed_interfaces[self.intf] = int(counter)
                    self.interface_name = self.intf
                    self.error_counter = self.failed_interfaces[self.intf]                        
                else:
                    table.add_row(self.device.alias,self.intf,str(duplex_threshold),str(counter),'Passed',style="green")
        # display the table
        console = Console(record=True)
        with console.capture() as capture:
            console.print(table,justify="center")
        log.info(capture.get())

        # should we pass or fail?
        if self.failed_interfaces:
            self.failed('Some interfaces are half duplex')
        else:
            self.passed('All interfaces are full duplex')

    @aetest.test
    def test_interface_oper_status(self):
        # Test for Operational Status
        oper_status_threshold = "up"
        self.failed_interfaces = {}
        table = Table(title="Interface Operational Status")
        table.add_column("Device", style="cyan")
        table.add_column("Interface", style="blue")
        table.add_column("Interface Operational Status Threshold", style="magenta")
        table.add_column("Interface Operational Status", style="magenta")
        table.add_column("Passed/Failed", style="green")
        for self.intf,value in self.parsed_interfaces.info.items():
            if 'oper_status' in value:
                counter = value['oper_status']
                if counter != oper_status_threshold:
                    table.add_row(self.device.alias,self.intf,str(oper_status_threshold),str(counter),'Failed',style="red")
                    self.failed_interfaces[self.intf] = counter
                    self.interface_name = self.intf
                    self.error_counter = self.failed_interfaces[self.intf]                        
                else:
                    table.add_row(self.device.alias,self.intf,str(oper_status_threshold),str(counter),'Passed',style="green")        

        # display the table
        console = Console(record=True)
        with console.capture() as capture:
            console.print(table,justify="center")
        log.info(capture.get())

        # should we pass or fail?
        if self.failed_interfaces:
            self.failed('Some interfaces are operationally down')
        else:
            self.passed('All interfaces are operationally up')


class CommonCleanup(aetest.CommonCleanup):
    @aetest.subsection
    def disconnect_from_devices(self, testbed):
        testbed.disconnect()

# for running as its own executable
if __name__ == '__main__':
    aetest.main()