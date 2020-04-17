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


def update_file():

    with open("settings.json", "r") as f:
        settings = json.load(f)

    version = [0,0,0,0]
    for idx,num in enumerate(settings["version"].split(".")):
        version[idx] = num
    version_tuple = tuple(version)
    build_name = os.environ.get("BUILD_NAME")

    new_version = template % {"version_tuple": version_tuple,
                              "file_version": settings["version"], "product_version": build_name, "name": settings["name"], "description": settings["description"]}

    with open("file-version.py", "w") as f:
        f.write(new_version)


if __name__ == "__main__":
    update_file()
