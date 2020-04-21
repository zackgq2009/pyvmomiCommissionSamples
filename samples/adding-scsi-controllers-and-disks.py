#!/usr/bin/env python
"""
Written by Dann Bohn
Github: https://github.com/whereismyjetpack
Email: dannbohn@gmail.com

Script to add a Hard disk to an existing VM
This is for demonstration purposes only.
I did not do a whole lot of sanity checking, etc.

Known issues:
This will not add more than 15 disks to a VM
To do that the VM needs an additional scsi controller
and I have not yet worked through that
"""
from pyVmomi import vim
from pyVmomi import vmodl
from pyVim.connect import SmartConnect, Disconnect, SmartConnectNoSSL
import atexit
import argparse
import getpass


def get_args():
    parser = argparse.ArgumentParser(
        description='Arguments for talking to vCenter')

    parser.add_argument('-s', '--host',
                        required=True,
                        action='store',
                        help='vSpehre service to connect to')

    parser.add_argument('-o', '--port',
                        type=int,
                        default=443,
                        action='store',
                        help='Port to connect on')

    parser.add_argument('-u', '--user',
                        required=True,
                        action='store',
                        help='User name to use')

    parser.add_argument('-p', '--password',
                        required=False,
                        action='store',
                        help='Password to use')

    parser.add_argument('-v', '--vm-name',
                        required=False,
                        action='store',
                        help='name of the vm')

    parser.add_argument('--uuid',
                        required=False,
                        action='store',
                        help='vmuuid of vm')

    parser.add_argument('--scsi_type',
                        required=False,
                        action='store',
                        choices=['LSI Logic SAS', 'LSI Logic Parallel', 'VMware Paravirtual'],
                        help='three types of scsi controller')

    parser.add_argument('--scsi_sharing',
                        required=False,
                        action='store',
                        choices=['noSharing', 'virtual', 'physical'],
                        help='the type of scsi sharing')

    args = parser.parse_args()

    if not args.password:
        args.password = getpass.getpass(
            prompt='Enter password')

    return args


def get_obj(content, vimtype, name):
    obj = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vimtype, True)
    for c in container.view:
        if c.name == name:
            obj = c
            break
    return obj


def add_scsi_controller(vm, si, scsi_type, scsi_sharing):
    devices = []
    spec = vim.vm.ConfigSpec()
    
    scsi_ctr = vim.vm.device.VirtualDeviceSpec()
    scsi_ctr.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
    scsi_ctr.device = vim.vm.device.ParaVirtualSCSIController()
    scsi_ctr.device.busNumber = 1
    scsi_ctr.device.hotAddRemove = True
    # scsi_ctr.device.controllerKey = 1
    scsi_ctr.device.sharedBus = scsi_sharing #default is noSharing
    scsi_ctr.device.scsiCtlrUnitNumber = 7
    devices.append(scsi_ctr)

    spec.deviceChange = devices
    vm.ReconfigVM_Task(spec=spec)
    print "add scsi controller"


def main():
    args = get_args()

    # connect this thing
    si = SmartConnectNoSSL(
        host=args.host,
        user=args.user,
        pwd=args.password,
        port=args.port)
    # disconnect this thing
    atexit.register(Disconnect, si)

    vm = None
    if args.uuid:
        search_index = si.content.searchIndex
        vm = search_index.FindByUuid(None, args.uuid, True)
    elif args.vm_name:
        content = si.RetrieveContent()
        vm = get_obj(content, [vim.VirtualMachine], args.vm_name)

    if vm:
        add_scsi_controller(vm, si, args.scsi_type, args.scsi_sharing)
    else:
        print "VM not found"


# start this thing
if __name__ == "__main__":
    main()
