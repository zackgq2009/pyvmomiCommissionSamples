#!/usr/bin/env python

# Copyright 2016 Abdul Anshad <abdulanshad33@gmail.com>
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""
Written by Abdul Anshad
Github: https://github.com/Abdul-Anshad-A
Email: abdulanshad33@gmail.com

Credits:
Thanks to "reuben.13@gmail.com" for the initial code.

Note: Example code For testing purposes only
vSphere Python SDK program to perform snapshot operations.
"""

import atexit
import argparse
import sys
import time
import ssl

from pyVmomi import vim, vmodl
from pyVim.task import WaitForTask
from pyVim import connect
from pyVim.connect import Disconnect, SmartConnect, GetSi, SmartConnectNoSSL

from tools import cli

def setup_args():
    parser = argparse.ArgumentParser(
        description='Operation of Snapshot in Virtual Machine.')
    parser.add_argument('-s', '--host', required=True, action='store',
                        help='Remote host to connect to')
    parser.add_argument('-o', '--port', type=int, default=443, action='store',
                        help='Port to connect on')
    parser.add_argument('-u', '--user', required=True, action='store',
                        help='User name to use when connecting to host')
    parser.add_argument('-p', '--password', required=True, action='store',
                        help='Password to use when connecting to host')
    parser.add_argument('-vn', '--vm_name', required=True,
                        help="the name of virtual machine.")
    parser.add_argument('-op', '--operation', required=True,
                        help="operation in 'create/remove/'revert/list_all/list_current/remove_all'")
    parser.add_argument('-sn', '--snapshot_name', required=True,
                        help="Name for the Snapshot")
    my_args = parser.parse_args()
    return my_args

# inputs = {'vcenter_ip': '192.168.1.10',
#           'vcenter_password': 'my_password',
#           'vcenter_user': 'root',
#           'vm_name': 'dummy_vm',
#           # operation in 'create/remove/revert/
#           # list_all/list_current/remove_all'
#           'operation': 'create',
#           'snapshot_name': 'snap1',
#           'ignore_ssl': True
#           }


def get_obj(content, vimtype, name):
    """
     Get the vsphere object associated with a given text name
    """
    obj = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vimtype, True)
    for c in container.view:
        if c.name == name:
            obj = c
            break
    return obj


def list_snapshots_recursively(snapshots):
    snapshot_data = []
    snap_text = ""
    for snapshot in snapshots:
        snap_text = "Name: %s; Description: %s; CreateTime: %s; State: %s" % (
                                        snapshot.name, snapshot.description,
                                        snapshot.createTime, snapshot.state)
        snapshot_data.append(snap_text)
        snapshot_data = snapshot_data + list_snapshots_recursively(
                                        snapshot.childSnapshotList)
    return snapshot_data


def get_snapshots_by_name_recursively(snapshots, snapname):
    snap_obj = []
    for snapshot in snapshots:
        if snapshot.name == snapname:
            snap_obj.append(snapshot)
        else:
            snap_obj = snap_obj + get_snapshots_by_name_recursively(
                                    snapshot.childSnapshotList, snapname)
    return snap_obj


def get_current_snap_obj(snapshots, snapob):
    snap_obj = []
    for snapshot in snapshots:
        if snapshot.snapshot == snapob:
            snap_obj.append(snapshot)
        snap_obj = snap_obj + get_current_snap_obj(
                                snapshot.childSnapshotList, snapob)
    return snap_obj


def main():

    args = setup_args()

    # si = None
    #
    # print("Trying to connect to VCENTER SERVER . . .")
    #
    # context = None
    # if inputs['ignore_ssl'] and hasattr(ssl, "_create_unverified_context"):
    #     context = ssl._create_unverified_context()
    #
    # si = connect.Connect(inputs['vcenter_ip'], 443,
    #                      inputs['vcenter_user'], inputs[
    #                          'vcenter_password'],
    #                      sslContext=context)
    #
    # atexit.register(Disconnect, si)

    try:
        si = SmartConnectNoSSL(host=args.host,
                               user=args.user,
                               pwd=args.password,
                               port=int(args.port))
        atexit.register(Disconnect, si)
    except:
        print("Unable to connect to %s" % args.host)
        return 1

    print("Connected to VCENTER SERVER !")

    content = si.RetrieveContent()

    # operation = inputs['operation']
    # vm_name = inputs['vm_name']
    operation = args.operation
    vm_name = args.vm_name

    vm = get_obj(content, [vim.VirtualMachine], vm_name)

    if not vm:
        print("Virtual Machine %s doesn't exists" % vm_name)
        sys.exit()

    if operation != 'create' and vm.snapshot is None:
        print("Virtual Machine %s doesn't have any snapshots" % vm.name)
        sys.exit()

    if operation == 'create':
        # snapshot_name = inputs['snapshot_name']
        snapshot_name = args.snapshot_name
        description = "Test snapshot"
        dumpMemory = False
        quiesce = False

        print("Creating snapshot %s for virtual machine %s" % (
                                        snapshot_name, vm.name))
        WaitForTask(vm.CreateSnapshot(
            snapshot_name, description, dumpMemory, quiesce))

    elif operation in ['remove', 'revert']:
        # snapshot_name = inputs['snapshot_name']
        snapshot_name = args.snapshot_name
        snap_obj = get_snapshots_by_name_recursively(
                            vm.snapshot.rootSnapshotList, snapshot_name)
        # if len(snap_obj) is 0; then no snapshots with specified name
        if len(snap_obj) == 1:
            snap_obj = snap_obj[0].snapshot
            if operation == 'remove':
                print("Removing snapshot %s" % snapshot_name)
                WaitForTask(snap_obj.RemoveSnapshot_Task(True))
            else:
                print("Reverting to snapshot %s" % snapshot_name)
                WaitForTask(snap_obj.RevertToSnapshot_Task())
        else:
            print("No snapshots found with name: %s on VM: %s" % (
                                                snapshot_name, vm.name))

    elif operation == 'list_all':
        print("Display list of snapshots on virtual machine %s" % vm.name)
        snapshot_paths = list_snapshots_recursively(
                            vm.snapshot.rootSnapshotList)
        for snapshot in snapshot_paths:
            print(snapshot)

    elif operation == 'list_current':
        current_snapref = vm.snapshot.currentSnapshot
        current_snap_obj = get_current_snap_obj(
                            vm.snapshot.rootSnapshotList, current_snapref)
        current_snapshot = "Name: %s; Description: %s; " \
                           "CreateTime: %s; State: %s" % (
                                current_snap_obj[0].name,
                                current_snap_obj[0].description,
                                current_snap_obj[0].createTime,
                                current_snap_obj[0].state)
        print("Virtual machine %s current snapshot is:" % vm.name)
        print(current_snapshot)

    elif operation == 'remove_all':
        print("Removing all snapshots for virtual machine %s" % vm.name)
        WaitForTask(vm.RemoveAllSnapshots())

    else:
        print("Specify operation in "
              "create/remove/revert/list_all/list_current/remove_all")

# Start program
if __name__ == "__main__":
    main()
