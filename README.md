# pyvmomiCommissionSamples
### 根据pyvmomi-community-samples项目衍生出来的，根据自己的业务操作进行了相应调整
#### 在使用过程中遇到的一些坑   
1. SSL or NoSSL   
    一些脚本中会根据输入的参数-S来使用不同的连接方式（SmartConnect  or  SmartConnectNoSSL），但有些脚本中则统一采用SmartConnect，这样就会造成连接vcenter的时候报（`ssl.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed`），这个时候请修改脚本，提交-S的参数判断或者默认就采用SmartConnectNoSSL的连接方式
2. decode()
    在deploy_ova.py脚本中，我们需要通过IO获取ova文件并将其部署到vmware vcenter上，默认decode的编码是Unicode，但由于环境的原因会造成相应的编码错误（`UnicodeDecodeError: 'ascii' codec can't decode byte 0xc3 in position 2161`）， 我们需要在decode的时候标注我们需要utf-8编码
3. AttributeError: 'NoneType'   
#### 在使用过程中理解的内容   
1. si = connect.SmartConnectNoSSL()    
2. atexit.register(connect.Disconnect, si)   
3. container = si.content.viewManager.CreateContainerView(si.content.rootFolder, [vim.VirtualMachine], True)   
4. root = si.content.rootFolder   
5. entity_stack = root.childEntity   
6. content = si.RetrieveContent()   
7. views = container.view   
8. summary = view.summary   
#### 
