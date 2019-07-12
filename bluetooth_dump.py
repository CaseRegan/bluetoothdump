import subprocess
import pexpect
import datetime

# logs
log_fname = 'bluetooth_dump'
activity_log = open('%s.log' % log_fname, 'r+')

# background scanning
subprocess.Popen(['bluetoothctl', 'scan', 'on'], stdout=subprocess.PIPE)
print('Started scan subprocess')
btctl = pexpect.spawn('bluetoothctl')
print('Started bluetoothctl')

help_message = 'Hold the desync button until the four lights start oscilating \
and you will be completely disconnected from the last Switch you were \
connected to!'
print(help_message)

# ensures that no non-specified devices are already registered
device_queue = subprocess.check_output(['bluetoothctl', 'devices']). \
    decode().splitlines()
for device in device_queue:
    arr = device.split(' ')
    mac = arr[1]
    name = ' '.join(arr[2:])

    btctl.sendline('remove %s' % mac)
    btctl.expect('Device has been removed')
    print('removed %s %s' % (name, mac))

    activity_log.write('removed pre-detected %s %s at %s\n' % \
        (name, mac, datetime.datetime.now()))

device_queue = []
no_repeat_timer = 0

# main loop
while 1:
    devices = subprocess.check_output(['bluetoothctl', 'devices']).decode()
    device_queue += devices.splitlines()

    while device_queue:
        device = device_queue.pop(0)
        arr = device.split(' ')
        mac = arr[1]
        name = ' '.join(arr[2:])

        if not name == 'Pro Controller':
            continue

        activity_log.write('attemping %s %s at %s\n' % \
            (name, mac, datetime.datetime.now()))

        try:
            btctl.sendline('pair %s' % mac)
            btctl.expect('Pairing successful')
            print('paired with %s %s' % (name, mac))

            btctl.sendline('connect %s' % mac)
            btctl.expect('Connection successful')
            print('connected to %s %s' % (name, mac))

            btctl.sendline('remove %s' % mac)
            btctl.expect('Device has been removed')
            print('removed %s %s' % (name, mac))

            activity_log.write('completed %s %s at %s\n' % \
                (name, mac, datetime.datetime.now()))

            print(help_message)
        except pexpect.TIMEOUT:
            print('timeout occured with %s %s at %s' % \
                (name, mac, datetime.datetime.now()))
            activity_log.write('timeout with %s %s at %s\n' % \
                (name, mac, datetime.datetime.now()))

activity_log.close()
