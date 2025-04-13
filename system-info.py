from distutils import core
from tkinter import ttk
import psutil
import platform
from datetime import datetime
import cpuinfo
import socket
import uuid
import re
import os
import subprocess
import winreg as reg
from datetime import datetime
from tkinter import *


class Windows:
    def __init__(self) -> None:
        self.infdb = {}

    def run(self):
        self.system_information()

    def infoTxT(self, text):
        self.info += "\n" + text

    def computersystem(self):
        sysdm = str(subprocess.check_output(
            "wmic computersystem get model,manufacturer,systemtype"))
        sysdm = sysdm.replace(r'\r', '')
        sysdm = sysdm.replace(r'\n', '')
        sysdm = sysdm.replace(r"b'Manufacturer", '')
        sysdm = sysdm.replace(r"Model", '')
        sysdm = sysdm.replace(r"SystemType", '')
        sysdm = sysdm.replace(r"'", '')
        sysdm = sysdm.replace(r"  ", ' ')
        sysdm = sysdm.strip()
        sysdm = re.sub(' +', ' ', sysdm)
        return sysdm

    def get_size(self, bytes, suffix="B"):
        """
        Scale bytes to its proper format
        e.g:
            1253656 => '1.20MB'
            1253656678 => '1.17GB'
        """
        factor = 1024
        for unit in ["", "K", "M", "G", "T", "P"]:
            if bytes < factor:
                return f"{bytes:.2f}{unit}{suffix}"
            bytes /= factor

    def mainBoard(self):
        board = str(subprocess.check_output(
            "wmic baseboard get product,Manufacturer,version,serialnumber"))
        board = board.replace(r'\r', '')
        board = board.replace(r'\n', '')
        board = board.replace(r"b'Manufacturer", '')
        board = board.replace(r"Product", '')
        board = board.replace(r"SerialNumber", '')
        board = board.replace(r"Version", '')
        board = board.replace(r"'", '')
        board = board.strip()
        board = board.split('  ')
        while '' in board:
            board.remove('')
        boardM = str(subprocess.check_output(
            "wmic csproduct get vendor, version"))
        boardM = boardM.replace(r'\r', '')
        boardM = boardM.replace(r'\n', '')
        boardM = boardM.replace(r"b'Vendor", '')
        boardM = boardM.replace(r"Version ", '')
        boardM = boardM.replace(r"'", '')
        boardM = boardM.replace(r"  ", ' ')
        boardM = boardM.strip()
        self.infdb["MainBoard Model"] = board[0]
        self.infdb["MainBoard Vendor"] = boardM
        self.infdb["MainBoard Product"] = board[1]
        self.infdb["MainBoard SerialNumber"] = board[2]
        self.infdb["MainBoard Version"] = board[3]

    def monitor(self):
        import win32api
        from win32com.client import GetObject
        try:
            objWMI = GetObject('winmgmts:\\\\.\\root\\WMI').InstancesOf(
                'WmiMonitorID')  # WmiMonitorConnectionParams
            monitors = []
            for i in range(len(objWMI)):
                monitor = str(objWMI[i].InstanceName)
                monitor = monitor.split('\\')
                monitors.append(monitor[1])
        except Exception as ex:
            monitors = []
            monitor = win32api.EnumDisplayDevices('\\\.\\DISPLAY1', 0)
            monitor = monitor.DeviceID
            monitor = monitor.split("\\")
            monitors.append(monitor[1])
        finally:
            return monitors

    def diskSpace(self):
        HDD = str(subprocess.check_output(
            'wmic diskdrive get model,serialNumber,size,status'))
        HDD = HDD.replace(r'\r', '')
        HDD = HDD.replace(r'\n', '')
        HDD = HDD.replace(r"b'Model", '')
        HDD = HDD.replace(r"Size", '')
        HDD = HDD.replace(r"SerialNumber", '')
        HDD = HDD.replace(r"Status", '')
        HDD = HDD.replace(r"'", '')
        HDD = HDD.strip()
        HDD = HDD.split('  ')
        while '' in HDD:
            HDD.remove('')
        HDDs = list()
        chunk_size = 4
        for i in range(0, len(HDD), chunk_size):
            HDDs.append(HDD[i:i+chunk_size])
        for i in range(len(HDDs)):
            HDDs[i][2] = f"{round(int(HDDs[i][2])/1024**3)} GB"
        for i in range(len(HDDs)):
            self.infdb[f"HDD Model[{i}]"] = f"{HDDs[i][0]}"
            self.infdb[f"HDD serialNumber[{i}]"] = f"{HDDs[i][1]}"
            self.infdb[f"HDD Space[{i}]"] = f"{HDDs[i][2]}"
            self.infdb[f"HDD status[{i}]"] = f"{HDDs[i][3]}"
        partitions = psutil.disk_partitions()
        for i, partition in enumerate(partitions):
            try:
                partname = str(partition.device).replace('\\', '')
                mountpoint = str(partition.mountpoint).replace('\\', '')
                if partname != "":
                    self.infdb[f"Partition[{i}]:"] = partname
                    PARTITION = partname
                else:
                    self.infdb[f"Partition[{i}]:"] = mountpoint
                    PARTITION = mountpoint
                self.infdb[f"File system type[{PARTITION}]"] = partition.fstype
                try:
                    partition_usage = psutil.disk_usage(partition.mountpoint)
                except PermissionError:
                    continue
                    # this can be catched due to the disk that
                    # isn't ready
                self.infdb[f"Total Size[{PARTITION}]"] = self.get_size(
                    partition_usage.total)
                self.infdb[f"Used[{PARTITION}]"] = self.get_size(
                    partition_usage.used)
                self.infdb[f"Free[{PARTITION}]"] = self.get_size(
                    partition_usage.free)
                self.infdb[f"Percentage[{PARTITION}]"] = partition_usage.percent
            except:
                continue
        # get IO statistics since boot
        disk_io = psutil.disk_io_counters()
        self.infdb["Total read"] = f"{self.get_size(disk_io.read_bytes)}"
        self.infdb["Total write"] = f"{self.get_size(disk_io.write_bytes)}"

    def dvdRom(self):
        try:
            dvdrom = str(subprocess.check_output(
                "wmic cdrom where mediatype!='unknown' get caption"))
            dvdrom = dvdrom.replace(r'\r', '')
            dvdrom = dvdrom.replace(r'\n', '')
            dvdrom = dvdrom.replace(r"b'Caption", '')
            dvdrom = dvdrom.replace(r"'", '')
            dvdrom = dvdrom.strip()
            if not 'b' == dvdrom:
                self.infdb["DvD Rom"] = dvdrom
            else:
                raise Exception('No Instance(s) Available.')
        except:
            self.infdb["DvD Rom"] = None

    def rmClear(self, cmd):
        cmd = cmd.replace(r'\r', '')
        cmd = cmd.replace(r'\n', '')
        cmd = cmd.replace(r"'", '')
        cmd = cmd.strip()
        cmds = cmd.split('  ')
        while '' in cmds:
            cmds.remove('')
        return cmds

    def ramManufacturer(self):
        RAMs = {}
        unknown = None
        mem = psutil.virtual_memory()
        RAMs["Memory Total"] = f"{self.get_size(mem.total)}"
        RAMs["Memory Available"] = f"{self.get_size(mem.available)}"
        RAMs["Memory Used"] = f"{self.get_size(mem.used)}"
        RAMs["Memory Percentage"] = f"{mem.percent}%"
        try:
            Capacity = str(subprocess.check_output(
                'wmic memorychip get Capacity'))
            Capacity = Capacity.replace(r"b'Capacity", '')
            Capacity = self.rmClear(Capacity)
            for i in range(len(Capacity)):
                Capacity[i] = f"{round(int(Capacity[i])/1024**3)}"
        except:
            Capacity = unknown
        try:
            Description = str(subprocess.check_output(
                'wmic memorychip get Description'))
            Description = Description.replace(r"b'Description", '')
            Description = self.rmClear(Description)
        except:
            Description = unknown
        try:
            DeviceLocator = str(subprocess.check_output(
                'wmic memorychip get DeviceLocator'))
            DeviceLocator = DeviceLocator.replace(r"b'DeviceLocator", '')
            DeviceLocator = self.rmClear(DeviceLocator)
        except:
            DeviceLocator = unknown
        try:
            Manufacturer = str(subprocess.check_output(
                'wmic memorychip get Manufacturer'))
            Manufacturer = Manufacturer.replace(r"b'Manufacturer", '')
            Manufacturer = self.rmClear(Manufacturer)
        except:
            Manufacturer = unknown
        try:
            MemoryType = str(subprocess.check_output(
                'wmic memorychip get MemoryType'))
            MemoryType = MemoryType.replace(r"b'MemoryType", '')
            MemoryType = self.rmClear(MemoryType)
        except:
            MemoryType = unknown
        try:
            Name = str(subprocess.check_output('wmic memorychip get Name'))
            Name = Name.replace(r"b'Name", '')
            Name = self.rmClear(Name)
        except:
            Name = unknown
        try:
            PartNumber = str(subprocess.check_output(
                'wmic memorychip get PartNumber'))
            PartNumber = PartNumber.replace(r"b'PartNumber", '')
            PartNumber = self.rmClear(PartNumber)
        except:
            PartNumber = unknown
        try:
            PositionInRow = str(subprocess.check_output(
                'wmic memorychip get PositionInRow'))
            PositionInRow = PositionInRow.replace(r"b'PositionInRow", '')
            PositionInRow = self.rmClear(PositionInRow)
        except:
            PositionInRow = unknown
        try:
            SerialNumber = str(subprocess.check_output(
                'wmic memorychip get SerialNumber'))
            SerialNumber = SerialNumber.replace(r"b'SerialNumber", '')
            SerialNumber = self.rmClear(SerialNumber)
        except:
            SerialNumber = unknown
        try:
            SMBIOSMemoryType = str(subprocess.check_output(
                'wmic memorychip get SMBIOSMemoryType'))
            SMBIOSMemoryType = SMBIOSMemoryType.replace(
                r"b'SMBIOSMemoryType", '')
            SMBIOSMemoryType = self.rmClear(SMBIOSMemoryType)
        except:
            SMBIOSMemoryType = unknown
        try:
            Speed = str(subprocess.check_output('wmic memorychip get Speed'))
            Speed = Speed.replace(r"b'Speed", '')
            Speed = self.rmClear(Speed)
        except:
            Speed = unknown
        try:
            Tag = str(subprocess.check_output(
                'wmic memorychip get Tag'))
            Tag = Tag.replace(r"b'Tag", '')
            Tag = self.rmClear(Tag)
        except:
            Tag = unknown
        try:
            TotalWidth = str(subprocess.check_output(
                'wmic memorychip get TotalWidth'))
            TotalWidth = TotalWidth.replace(r"b'TotalWidth", '')
            TotalWidth = self.rmClear(TotalWidth)
        except:
            TotalWidth = unknown
        try:
            TypeDetail = str(subprocess.check_output(
                'wmic memorychip get TypeDetail'))
            TypeDetail = TypeDetail.replace(r"b'TypeDetail", '')
            TypeDetail = self.rmClear(TypeDetail)
        except:
            TypeDetail = unknown
        RAMs_exp = []
        for i in range(len(Capacity)):
            DDR = None
            RAM = {}
            if SMBIOSMemoryType:
                for i in range(len(SMBIOSMemoryType)):
                    if int(SMBIOSMemoryType[i]) == 20:
                        DDR = "DDR1"
                    elif int(SMBIOSMemoryType[i]) == 21:
                        DDR = "DDR2"
                    elif int(SMBIOSMemoryType[i]) == 22:
                        DDR = "DDR2 FB-DIMM"
                    elif int(SMBIOSMemoryType[i]) == 24:
                        DDR = "DDR3"
                    elif int(SMBIOSMemoryType[i]) == 26:
                        DDR = "DDR4"
                    else:
                        DDR = "Unknown"
            elif MemoryType:
                for i in range(len(MemoryType)):
                    if int(MemoryType[i]) == 20:
                        DDR = "DDR1"
                    elif int(MemoryType[i]) == 21:
                        DDR = "DDR2"
                    elif int(MemoryType[i]) == 22:
                        DDR = "DDR2 FB-DIMM"
                    elif int(MemoryType[i]) == 24:
                        DDR = "DDR3"
                    elif int(MemoryType[i]) == 26:
                        DDR = "DDR4"
                    else:
                        DDR = "Unknown"
            else:
                DDR = "Unknown"
            for i in range(len(Capacity)):
                try:
                    RAM[f"Size[{i}]"] = f"{Capacity[i]}GB"
                    RAM[f"DeviceLocator[{i}]"] = f"{DeviceLocator[i]}"
                    RAM[f"Manufacturer[{i}]"] = f"{Manufacturer[i]}"
                    RAM[f"Type[{i}]"] = f"{DDR}"
                    RAM[f"PartNumber[{i}]"] = f"{PartNumber[i]}"
                    if PositionInRow:
                        RAM[f"PositionInRow[{i}]"] = f"{PositionInRow[i]}"
                    RAM[f"SerialNumber[{i}]"] = f"{SerialNumber[i]}"
                    RAM[f"Speed[{i}]"] = f"{Speed[i]} Mhz"
                    RAM[f"TotalWidth[{i}]"] = f"{TotalWidth[i]}"
                    RAM[f"TypeDetail[{i}]"] = f"{TypeDetail[i]}"
                    if Tag:
                        RAMs[f"{Tag[i]}"] = RAM
                    else:
                        RAMs[f"{Name[i]}"] = RAM
                except:
                    pass
        return RAMs

    def graphic(self):
        g = str(subprocess.check_output(
            'wmic path win32_VideoController get adapterram,name'))
        g = g.replace(r'\r', '')
        g = g.replace(r'\n', '')
        g = g.replace(r"Name", '')
        g = g.replace(r"b'AdapterRAM", '')
        g = g.replace(r"'", '')
        g = g.strip()
        grphics = g.split('  ')
        while '' in grphics:
            grphics.remove('')
        for i in range(0, len(grphics), 2):
            grphics[i] = f"{round(int(grphics[i])/1024**3)}GB"
        return grphics

    def network(self):
        net = str(subprocess.check_output(
            'wmic nic get Name, MACAddress'))
        net = net.replace(r"Name", '')
        net = net.replace(r"b'MACAddress", '')
        net = net.replace(r"'", '')
        net = net.strip()
        nets = net.split('\\r\\r\\n')
        while '' in nets:
            nets.remove('')
        for i, nt in enumerate(nets):
            nets[i] = nt.strip()
        networks = []
        for nt in nets:
            networks.append(nt.split('  '))
        Networks = ""
        z = 0
        for n in networks:
            mac = n[0]
            try:
                nets = n[1]
            except:
                nets = mac
                # mac = "                 "
                mac = ""
            if z > 0:
                Networks += '\n'
            Networks += f"{nets}  [{mac}]"
            z += 1
        return Networks

    def devices(self):
        devs = str(subprocess.check_output(
            'wmic printer get DriverName'))
        devs = devs.replace(r"b'DriverName", '')
        devs = devs.replace(r"'", '')
        devs = devs.strip()
        devss = devs.split('\\r\\r\\n')
        while '' in devss:
            devss.remove('')
        for i, nt in enumerate(devss):
            devss[i] = nt.strip()
        dvs = ""
        z = 0
        for d in devss:
            if z > 0:
                dvs += '\n'
            dvs += d
            z += 1
        return dvs

    def ip_address(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]

    def system_information(self):
        uname = platform.uname()
        # win install date
        key = reg.OpenKey(reg.HKEY_LOCAL_MACHINE,
                          r'SOFTWARE\Microsoft\Windows NT\CurrentVersion')
        secs = reg.QueryValueEx(key, 'InstallDate')[0]
        installDateWin = datetime.fromtimestamp(secs)
        domain = subprocess.run(["powershell.exe", "(Get-CimInstance Win32_ComputerSystem).Domain"],
                                stdout=subprocess.PIPE, text=True).stdout.strip()
        self.infdb["Computer Name"] = uname.node
        self.infdb["WorkGroup"] = domain
        self.infdb["Operation System"] = uname.system
        self.infdb["Release"] = uname.release
        self.infdb["Version"] = uname.version
        self.infdb["System Type"] = platform.architecture()[0]
        self.infdb["User"] = str(os.getlogin())
        self.infdb["Install Date"] = installDateWin
        self.infdb["sysdm"] = self.computersystem()
        self.infdb["Machine"] = uname.machine
        # Network
        if '192.168' in self.ip_address():
            self.infdb["Ip-Address"] = self.ip_address()
        else:
            self.infdb["Ip-Address"] = socket.gethostbyname(
                socket.gethostname())
        # self.infdb["Mac-Address"] = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
        Networks = self.network()
        self.infdb["Network Cards:"] = Networks

        # MainBoard
        self.mainBoard()
        boot_time_timestamp = psutil.boot_time()
        bt = datetime.fromtimestamp(boot_time_timestamp)
        self.infdb["Boot Time"] = f"{bt.year}/{bt.month}/{bt.day} {bt.hour}:{bt.minute}:{bt.second}"

        # ==== CPU ====
        self.infdb["Processor"] = uname.processor
        self.infdb["Processor(cpu)"] = cpuinfo.get_cpu_info()['brand_raw']
        self.infdb["Physical cores"] = psutil.cpu_count(logical=False)
        self.infdb["Total cores"] = psutil.cpu_count(logical=True)
        # CPU frequencies
        cpufreq = psutil.cpu_freq()
        self.infdb["Max Frequency"] = f"{cpufreq.max:.2f}Mhz"
        self.infdb["Min Frequency"] = f"{cpufreq.min:.2f}Mhz"
        self.infdb["Current Frequency"] = f"{cpufreq.current:.2f}Mhz"
        # CPU usage
        cores = ""
        n = 0
        for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
            if n > 0:
                cores += "\n"
            cores += f"Core {i}: {percentage}%"
            n += 1
        self.infdb["Total CPU Usage"] = f"{psutil.cpu_percent()}%"
        self.infdb["CPU Usage Per Core:"] = cores

        # ==== MEMORY ====
        rams = self.ramManufacturer()
        for k, v in rams.items():
            if isinstance(v, dict):
                self.infdb[k] = "-"*10
                for k2, v2 in v.items():
                    self.infdb[f"{k2}"] = v2
            else:
                self.infdb[k] = v

        # SWAP
        # get the swap memory details (if exists)
        swap = psutil.swap_memory()
        self.infdb["SWAP Total"] = f"{self.get_size(swap.total)}"
        self.infdb["SWAP Free"] = f"{self.get_size(swap.free)}"
        self.infdb["SWAP Used"] = f"{self.get_size(swap.used)}"
        self.infdb["SWAP Percentage"] = f"{swap.percent}%"

        # Graphics
        gr = self.graphic()
        g = 0
        for i in range(0, len(gr), 2):
            self.infdb[f"Graphic Card[{g}]"] = gr[i+1].strip()
            self.infdb[f"Graphic Size[{g}]"] = gr[i].strip()
            g += 1

        # === Disk Information ====
        self.diskSpace()
        # get all disk partitions

        # Monitors
        dp = self.monitor()
        for i, m in enumerate(dp):
            self.infdb[f"Monitor[{i}]"] = m

        # DvD Rom
        self.dvdRom()

        # Devices
        self.infdb['Devices:'] = self.devices()


class ShowGUI:
    def __init__(self, lst_inf):
        self.lst_inf = lst_inf
        self.root = Tk()
        self.root.tk.call('tk', 'scaling', 2.0)
        w, h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry("%dx%d+0+0" % (w, h))
        self.root.title('SYSTEM Information')

        self.tableView()
        self.run()

    def run(self):
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        finally:
            self.root.mainloop()

    def tableView(self):
        today = datetime.now()
        dateNow = today.strftime("%Y/%m/%d")
        # text prettytable
        from prettytable import PrettyTable
        t = ExpandoText(self.root, wrap="word")
        t.config(foreground="white", background='black')
        x = PrettyTable()
        x.field_names = ["Title", f"Detail ({dateNow})"]
        for k in self.lst_inf:
            x.add_row([k, self.lst_inf[k]])
        t.insert(INSERT, x)
        t.tag_configure("center", justify='center')
        t.tag_add("center", "1.0", "end")
        t.pack(fill="both", expand=True)
        with open(f"{self.lst_inf['Computer Name']}_{today.strftime('%Y%m%d')}.txt", 'w+') as w:
            w.write(str(x))


class ExpandoText(Text):
    def insert(self, *args, **kwargs):
        result = Text.insert(self, *args, **kwargs)
        self.reset_height()
        return result

    def reset_height(self):
        height = self.tk.call(
            (self._w, "count", "-update", "-displaylines", "1.0", "end"))
        self.configure(height=height)


win_inf = Windows()
win_inf.run()
lst = win_inf.infdb

display = ShowGUI(lst_inf=lst)
