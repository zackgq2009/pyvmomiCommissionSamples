#!/usr/bin/env python                                                                                                                                                           

"""                                                                                                                                                                             
Python program that generates various statistics for one or more virtual machines                                                                                               
A list of virtual machines can be provided as a comma separated list.                                                                                                           
"""
# change the RAM of vm with MB
from __future__ import print_function
from pyVim.connect import SmartConnect, Disconnect, SmartConnectNoSSL
from pyVmomi import vmodl, vim
from datetime import timedelta, datetime
from pyVim.task import WaitForTask

import argparse
import atexit
import getpass

import ssl

def get_args():
        parser = argparse.ArgumentParser(description='change vm cpu and memory')
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

        parser.add_argument('--cpu',
                   required=False,
                   action='store',
                   help='vcpu of vm')

        parser.add_argument('--memory',
                   required=False,
                   action='store',
                   help='memory of vm')

        args = parser.parse_args()

        if not args.password:
            args.password = getpass.getpass(prompt='Enter password')
        return args
        
def get_obj(content, vimtype, name):
        obj = None
        container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
        for c in container.view:
                if c.name == name:
                        obj = c
                        break
        return obj

def change_vcpu(vm, si, vcpu_nu):
        vcpu_nu=int(vcpu_nu)
        cspec = vim.vm.ConfigSpec()
        cspec.numCPUs = vcpu_nu
        cspec.numCoresPerSocket = 1
        WaitForTask(vm.Reconfigure(cspec))

def change_memory(vm, si, mem_size):
        mem_size=long(mem_size)
        cspec = vim.vm.ConfigSpec()
        cspec.memoryMB = mem_size # MB of memory                                                                                                                                
        WaitForTask(vm.Reconfigure(cspec))
        
def main():
        args = get_args()
# connect this thing                                                                                                                                                            
        si = SmartConnectNoSSL(host=args.host,
                user=args.user,
                pwd=args.password,
                port=args.port)
# disconnect this thing                                                                                                                                                         
        atexit.register(Disconnect, si)
        if args.uuid:
                search_index = si.content.searchIndex
                vm = search_index.FindByUuid(None, args.uuid, True)
        elif args.vm_name:
                content = si.RetrieveContent()
                vm = get_obj(content, [vim.VirtualMachine], args.vm_name)

        if vm:
                if args.cpu and args.memory:
                        print('changeCPU:',args.cpu)
                        print('changeMEMORY:',args.memory)
                elif args.memory and not args.cpu:
                        print('changeMEMORY:',args.memory)
                        change_memory(vm, si, args.memory)
                elif args.cpu and not args.memory:
                        print('changeCPU:',args.cpu)
                        change_vcpu(vm, si, args.cpu)
                else:
                        print("-h, --help show help messages for you")
        else:
                print("VM not found")

if __name__ == "__main__":
    main()                