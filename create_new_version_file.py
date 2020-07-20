import json
import os
template = """
# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
    ffi=FixedFileInfo(
        # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
        # Set not needed items to zero 0.
        filevers=%(version_tuple)s,
        prodvers=%(version_tuple)s,
        # Contains a bitmask that specifies the valid bits 'flags'r
        mask=0x3f,
        # Contains a bitmask that specifies the Boolean attributes of the file.
        flags=0x0,
        # The operating system for which this file was designed.
        # 0x4 - NT and there is no need to change it.
        OS=0x4,
        # The general type of file.
        # 0x1 - the file is an application.
        fileType=0x1,
        # The function of the file.
        # 0x0 - the function is not defined for this fileType
        subtype=0x0,
        # Creation date and time stamp.
        date=(0, 0)
    ),
    kids=[
        StringFileInfo(
            [
                StringTable(
                    u'040904B0',
                    [StringStruct(u'CompanyName', u'Qualisys'),
                     StringStruct(u'FileDescription',
                                  u'%(description)s'),
                     StringStruct(u'FileVersion', u'%(file_version)s'),
                     StringStruct(u'InternalName', u'%(name)s'),
                     StringStruct(u'LegalCopyright', u''),
                     StringStruct(u'OriginalFilename', u'%(name)s.exe'),
                     StringStruct(u'ProductName', u'%(name)s'),
                     StringStruct(u'ProductVersion', u'%(product_version)s')])
            ]),
        VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
    ]
)

"""

def load_pyCGM2_version(requrements_file):
    with open(requrements_file,"r") as f:
        for line in f.readlines():
            if "git+https://github.com" in line and "pyCGM2" in line:
                version = line.split("git+")[-1]
                version = version.replace("\n","")
                break
    return version

def update_file(full_name):

    name = "_".join(full_name.split("_")[:-1])

    with open("settings.json","w") as f:
        json.dump({"name":full_name},f) # used in main.spec

    version_number = full_name.split("_")[-1].split("+")[0]
    version = [0,0,0,0]
    for idx,num in enumerate(version_number.split(".")):
        version[idx] = int(num)
    version_tuple = tuple(version)

    final_description = "Qualisys implementation for CGM2. pyCGM2 version: " + load_pyCGM2_version("requirements-dev.txt")

    new_version = template % {"version_tuple": version_tuple,
                              "file_version": version_number, "product_version": full_name, "name": name, "description": final_description}

    with open("file-version.py", "w") as f:
        f.write(new_version)


if __name__ == "__main__":
    import argparse

    argparser = argparse.ArgumentParser()
    argparser.add_argument("--build-name",type=str,required=True,help="format needs to be as follows: name-you-desire_x.x.x+num ")
    args = argparser.parse_args()

    update_file(args.build_name)

