#!/usr/bin/env python                                                                                                                                                           
"""                                                                                                                                                                             
Github : https://github.com/blacksponge                                                                                                                                         
                                                                                                                                                                                
This code is released under the terms of the Apache 2                                                                                                                           
http://www.apache.org/licenses/LICENSE-2.0.html                                                                                                                                 
                                                                                                                                                                                
Example code for using the task scheduler.                                                                                                                                      
"""
# poweroff the vm machine
import atexit
import argparse
import getpass
from datetime import datetime
from pyVmomi import vim
from pyVim import connect

from tools import cli
from tools import tasks

def get_args():
    parser = argparse.ArgumentParser(
        description='Arguments for scheduling a poweroff of a virtual machine')
    parser.add_argument('-s', '--host', required=True, action='store',
                        help='Remote host to connect to')
    parser.add_argument('-o', '--port', type=int, default=443, action='store',
                        help='Port to connect on')
    parser.add_argument('-u', '--user', required=True, action='store',
                        help='User name to use when connecting to host')
    parser.add_argument('-p', '--password', required=False, action='store',
                        help='Password to use when connecting to host')
    parser.add_argument('-d', '--date', required=False, action='store',
                        help='Date and time used to create the scheduled task '
                        'with the format d/m/Y H:M')
    parser.add_argument('-n', '--vmname', required=True, action='store',
                        help='VM name on which the action will be performed')
    args = parser.parse_args()
    return args


def main():
    args = get_args()
    if args.date:
        try:
                dt = datetime.strptime(args.date, '%d/%m/%Y %H:%M')
        except ValueError:
                print('Unrecognized date format')
                raise
                return -1

    if args.password:
        password = args.password
    else:
        password = getpass.getpass(prompt='Enter password for host %s and '
                                   'user %s: ' % (args.host, args.user))

    try:
        si = connect.SmartConnectNoSSL(host=args.host,
                                       user=args.user,
                                       pwd=password,
                                       port=int(args.port))
    except vim.fault.InvalidLogin:
        print("Could not connect to the specified host using specified "
              "username and password")
        return -1

    atexit.register(connect.Disconnect, si)
    # vm = None                                                                                                                                                                 
    # 
    view = si.content.viewManager.CreateContainerView(si.content.rootFolder,
                                                      [vim.VirtualMachine],
                                                      True)
    vms = [vm for vm in view.view if vm.name == args.vmname]

    if not vms:
        print('VM not found')
        connect.Disconnect(si)
        return -1
    vm = vms[0]

    # vm = si.content.searchIndex.FindByDnsName(None, args.vmname,                                                                                                              
    #                                           True)                                                                                                                           

    # spec = vim.scheduler.ScheduledTaskSpec()                                                                                                                                  
    # spec.name = 'PowerOff vm %s' % args.vmname                                                                                                                                
    # spec.description = 'poweroff vm machine'                                                                                                                                  
    # spec.scheduler = vim.scheduler.OnceTaskScheduler()                                                                                                                        
    # spec.scheduler.runAt = dt                                                                                                                                                 
    # spec.action = vim.action.MethodAction()                                                                                                                                   
    # spec.action.name = vim.VirtualMachine.PowerOff                                                                                                                            
    # spec.enabled = True                                                                                                                                                       

    # si.content.scheduledTaskManager.CreateScheduledTask(vm, spec)                                                                                                             

    TASK = vm.PowerOff()
    tasks.wait_for_tasks(si, [TASK])


if __name__ == "__main__":
    main()
