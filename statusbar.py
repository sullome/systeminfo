#!/usr/bin/python
from subprocess import PIPE, run
from json import loads
from datetime import datetime
from re import match
from locale import setlocale, LC_ALL, getlocale
from time import sleep

# Set locale to user's default
setlocale(LC_ALL, '')

def get_workspaces():
    workspaces = run('i3-msd -t get_workspaces'.split(), stdout = PIPE).stdout
    workspaces = loads(workspaces.decode())

    for i in range(len(workspaces)):
        workspace = workspaces[i]
        dzen_ws = workspace['name']
        if workspace['focused']:
            pass
        else:
            pass
        if workspace['urgent']:
            pass
        else:
            pass
        command = 'i3-msg workspace num {}'.format(workspace['num'])
        dzen_ws = '^ca(1,{}){}^ca()'.format(command, dzen_ws)
        #TODO: ПКМ по тэгу - показать список окон на нём
        workspaces[i] = dzen_ws
    return ' '.join(workspaces)

def get_time():
    dt = datetime.now()
    month = dt.strftime('%B').lower()
    if month.endswith('т'):
        month += 'а'
    else:
        month = month[:-1] + 'я'
    return dt.strftime('%A, %e {}, %R'.format(month))

SI = (
    (10 ** 12,'Tbit'),
    (10 ** 9, 'Gbit'),
    (10 ** 6, 'Mbit'),
    (10 ** 3, 'kbit')
)
def nice_convert(b):
    '''Inspired by hurry.filesize (https://pypi.python.org/pypi/hurry.filesize/)'''

    global SI
    b *= 8
    for factor, suffix in SI:
        if b >= factor:
            break
    b = b / factor
    return '{:.2f} {}/s'.format(b, suffix)

def read_traffic():
    traffic = dict()
    with open('/proc/net/dev') as netdev:
        lines = netdev.read()
    lines = lines.splitlines()[2:]
    for device in lines:
        device = device.split()
        traffic[device[0][:-1]] = (
            int(device[1]), # Receive (bytes)
            int(device[2]), # Receive (packets)
            int(device[9]), # Transmit (bytes)
            int(device[10]) # Transmit (packets)
            )
    return traffic

def get_traffic():
    traffic = read_traffic()
    full_receive = sum([x[0] for x in traffic.values()])
    full_transmit= sum([x[2] for x in traffic.values()])
    return (full_receive, full_transmit)

def get_cpu():
    cpu = []

    with open('/proc/stat') as stat:
        lines = stat.read()
    lines = lines.splitlines()

    for line in lines:
        if match('cpu\d', line):
            line = line.split()
            for i in range(1,5): line[i] = int(line[i])

            cpu_id = int(line[0][-1:])
            total= sum(line[1:5])
            work = total - line[4]
            cpu.insert(cpu_id, (work, total))
    return cpu

stripname = lambda s, n: int(s.strip(n + ': kB\n'))
def get_ram():
    total = 0
    used = []

    with open('/proc/meminfo') as meminfo:
        lines = meminfo.read()
    lines = lines.splitlines()

    for line in lines:
        if 'MemTotal' in line:
            total = stripname(line, 'MemTotal')
        elif 'MemFree' in line:
            used.append(stripname(line, 'MemFree'))
        elif 'Buffers' in line:
            used.append(stripname(line, 'Buffers'))
        elif 'Cached' in line and 'Swap' not in line:
            used.append(stripname(line, 'Cached'))
    return 1 - sum(used)/total

def get_health_timer():
    pass

def main():
    # Init
    current_time = perf_counter()
    prev_traffic = get_traffic()
    prev_cpu = get_cpu()

    while True:
        # Workspaces
        ws = get_workspaces()

        # Time
        time = get_time()

        # Traffic
        traffic = get_traffic()
        elapsed = perf_counter() - current_time

        receive  = (traffic[0] - prev_traffic[0]) / elapsed
        transmit = (traffic[1] - prev_traffic[1]) / elapsed

        current_time = perf_counter()
        prev_traffic = traffic

        # CPU
        cpu = get_cpu()
        cpu_load = []
        for i in range(len(cpu)):
            work = cpu[i][0] - prev_cpu[i][0]
            total= cpu[i][1] - prev_cpu[i][1]
            load = work / total
            if l > 1: l = 1
            cpu_load[i] = load

        prev_cpu = cpu

        # RAM
        ram = get_ram()

        sleep(1)

if __name__ == '__main__':
    main()
