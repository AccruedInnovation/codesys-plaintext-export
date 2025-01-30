from __future__ import print_function
from scriptengine import *
import os, shutil
from datetime import datetime

############################################################################
################################# Variables
############################################################################

save_folder = os.path.join(r'C:\Codesys\_TEST_git')

text_extension = '.exp'

save_applications = False
save_pou_tab = True

save_pous = True
save_duts = True
save_gvls = True
save_meth = True
save_acts = True
save_prop = True
save_visu = True

skip_root_folders = True
skipRootFolderNames = ['SkipThisFolder']

debug = True
extendedDebug = False

############################################################################
################################# Timestamps and print statements
############################################################################

start = datetime.now()


old_print = print


def timestamped_print(*args, **kwargs):
    old_print(datetime.now(), *args, **kwargs)


def debug_timestamped_print(*args, **kwargs):
    if debug or extendedDebug:
        old_print(datetime.now(), *args, **kwargs)


def extended_debug_timestamped_print(*args, **kwargs):
    if extendedDebug:
        old_print(datetime.now(), *args, **kwargs)


print = timestamped_print
debugPrint = debug_timestamped_print
eDebugPrint = extended_debug_timestamped_print


print("Start")

############################################################################
################################# CONFIG AND CLASSES
############################################################################

Project_Settings = Guid('8753fe6f-4a22-4320-8103-e553c4fc8e04') # root node?

ApplicationGUID	= Guid('639b491f-5557-464c-af91-1471bac9f549')
folderGUID = Guid('738bea1e-99bb-4f04-90bb-a7a567e74e3a')

GVLGuid = Guid('ffbfa93a-b94d-45fc-a329-229860183b1d')
GVLPersistentGUID = Guid('261bd6e6-249c-4232-bb6f-84c2fbeef430')

POUGuid = Guid("6f9dac99-8de1-4efc-8465-68ac443b7d08")
DUTGuid = Guid("2db5746d-d284-4425-9f7f-2663a34b0ebc")

methodwithoutGUID = Guid("f89f7675-27f1-46b3-8abb-b7da8e774ffd")
methodGUID = Guid("f8a58466-d7f6-439f-bbb8-d4600e41d099")
actionGUID = Guid('8ac092e5-3128-4e26-9e7e-11016c6684f2')

propertyGUID = Guid('5a3b8626-d3e9-4f37-98b5-66420063d91e')
propertyMethodGUID = Guid('792f2eb6-721e-4e64-ba20-bc98351056db')

visuGUID = Guid('f18bec89-9fef-401d-9953-2f11739a6808')

gittable_nodes = {    
    folderGUID : '',
    POUGuid : 'POU',
    DUTGuid : 'DUT',
    GVLGuid : 'GVL',
    GVLPersistentGUID : 'GVLP',
    methodwithoutGUID : 'M',
    methodGUID : 'M',
    actionGUID : 'A',
    propertyGUID : 'P',
    propertyMethodGUID : 'PM',
}

if save_pous:
    gittable_nodes[POUGuid] = 'POU'
    
if save_duts:
    gittable_nodes[DUTGuid] = 'DUT'

if save_gvls:
    gittable_nodes[GVLGuid] = 'GVL'
    gittable_nodes[GVLPersistentGUID] = 'GVLP'

if save_meth:
    gittable_nodes[methodwithoutGUID] = 'M'
    gittable_nodes[methodGUID] = 'M'

if save_acts:
    gittable_nodes[actionGUID] = 'A'

if save_prop:
    gittable_nodes[propertyGUID] = 'P'
    gittable_nodes[propertyMethodGUID] = 'PM'

if save_visu:
    gittable_nodes[visuGUID] = 'VISU'

gittable_guids = gittable_nodes.keys()

application_nodes = set()
root_nodes = set()

############################################################################
################################# Functions
############################################################################

has_repo = False

def GitFolderWipe():
    if GitFolderExists():
        a=os.listdir(save_folder)
        for f in a:
            if not f.startswith("."): # .git
                sub_path = os.path.join(save_folder,f)
                if os.path.isdir(sub_path):
                    shutil.rmtree(sub_path)
                else:
                    os.remove(sub_path)
            #elif f==".git":
                #has_repo=True


def GitFolderExists():
    if not os.path.exists(save_folder):
        os.makedirs(save_folder) 
        return False
    return True
    

def CheckMakeFolder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path) 


def CheckRemoveFile(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)


def FindRootNodes():
    if save_pou_tab:
        first_nodes = proj.get_children()
        for node in first_nodes:
            guid = node.type
            if guid in gittable_guids:
                name = node.get_name()
                if skip_root_folders and guid == folderGUID and name in skipRootFolderNames:
                    continue
                root_nodes.add(node)
            
    if save_applications:
        all_nodes = proj.get_children(True)
        for node in all_nodes:
            if node.type == ApplicationGUID:
                application_nodes.add(node)


def Clear_Text_Object(ScriptTextDocument):
    ScriptTextDocument.remove(length=ScriptTextDocument.length, offset=0)
    return
 

def Clear_All_Texts(pou):
    Clear_Text_Object(pou.textual_implementation)
    Clear_Text_Object(pou.textual_declaration)
    return 


def ParseNodes():
    if save_pou_tab:
        for node in root_nodes:
            name = node.get_name()
            guid = node.type
            if guid == folderGUID:
                folder_children = node.get_children()
                if folder_children:
                    folder_path = os.path.join(save_folder, name)
                    ParseNode(node, folder_path)
            else:
                ext = gittable_nodes[guid]
                folder_path = os.path.join(save_folder, ext + '.' + name)
                SaveNewNode(node, folder_path)
    
    application_number = 0
    folder_path = save_folder
    if save_applications:
        for node in application_nodes: # all application nodes are "folders"
            folder_path = os.path.join(save_folder, 'Application' + str(application_number))
            ParseNode(node, folder_path)
            application_number = application_number + 1


def ParseNode(root, folder_path):
    CheckMakeFolder(folder_path)

    child_nodes = root.get_children()
    
    for node in child_nodes:
        save_path = folder_path
        guid = node.type
        
        if guid in gittable_guids:
            name = node.get_name()
            eDebugPrint("Found node: {}".format(name))
            
            if guid == folderGUID:
                save_path = os.path.join(save_path, name)
                eDebugPrint("Subfolder found: {}".format(save_path))
                ParseNode(node, save_path)
            else:
                pou_children = node.get_children()
                if pou_children:
                    save_path = os.path.join(save_path, name)
                    eDebugPrint("MultiLevel POU found: {}".format(name))
                    #ParseNode(node, save_path)
                    ParseMultiLevelPOU(node, save_path)

                ext = gittable_nodes[guid]
                save_path = os.path.join(save_path, ext + '.' + name)
                eDebugPrint("Saving node: {}".format(name))
                SaveNewNode(node, save_path)


def ParseMultiLevelPOU(node, folder_path):
    # Start somewhere simple
    ParseNode(node, folder_path)

def SaveNewNode(node, save_path):
    has_dec = node.has_textual_declaration
    has_impl = node.has_textual_implementation
    is_pou = ( node.type == POUGuid )
    is_visu = ( node.type == visuGUID )
    
    # Only export as XML if we're a POU with non-ST implementation
    pou_xml_export = (has_dec and is_pou) and (not has_impl)
    visu_xml_export = (is_visu)
    
    xml_export = pou_xml_export or visu_xml_export
    
    if xml_export:
        file_path = os.path.join(save_path + '.xml')
        
        CheckRemoveFile(file_path)
        eDebugPrint("Using native export format for: {}".format(file_path))
        node.export_native(
            destination = os.path.join(file_path),
            recursive = False,
            profile_name = None
        )
    
    # ST POU or other textual object
    else:
        if has_dec:
            file_path = os.path.join(save_path + '.DEC' + text_extension)
            plaintext = node.textual_declaration.text
            
            CheckRemoveFile(file_path)
            eDebugPrint("Using plaintext format for: {}".format(file_path))
            with open(file_path,'w') as f:
                f.write(str(plaintext))
        
            if has_impl:
                file_path = os.path.join(save_path + '.IMP' + text_extension)
                plaintext = node.textual_implementation.text
                
                CheckRemoveFile(file_path)
                eDebugPrint("Using plaintext format for: {}".format(file_path))
                with open(file_path,'w') as f:
                    f.write(str(plaintext))
        
        else: # Implementation onle = Action
            if has_impl:
                file_path = os.path.join(save_path + text_extension)
                plaintext = node.textual_implementation.text
                
                CheckRemoveFile(file_path)
                eDebugPrint("Using plaintext format for: {}".format(file_path))
                with open(file_path,'w') as f:
                    f.write(str(plaintext))
    
    eDebugPrint("Save Successful!")


############################################################################
################################# RUN SCRIPT
############################################################################

# Set target Project to primary
proj = projects.primary

# get script's current directory
ScriptPath = os.path.dirname(os.path.realpath(__file__))

GitFolderWipe()

FindRootNodes()

debugPrint("Root Node Count: {}".format(len(root_nodes)))

if extendedDebug and len(root_nodes) > 0:
    print("Root Nodes")
    for node in root_nodes:
        print("{}".format(node.get_name()))

debugPrint("Application Node Count: {}".format(len(application_nodes)))

if extendedDebug and len(application_nodes) > 0:
    print("Application Nodes:")
    for node in application_nodes:
        print("{}".format(node.get_name()))

print("Parsing nodes")

ParseNodes()

print("DONE! Script runtime: {}".format(datetime.now()-start))