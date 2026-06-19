Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
appPath = fso.BuildPath(scriptDir, "app.py")
pythonPath = "C:\Users\zjh\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

shell.CurrentDirectory = scriptDir
cmd = """" & pythonPath & """ -m streamlit run """ & appPath & """ --server.address 127.0.0.1 --server.port 8501 --server.headless true"
shell.Run cmd, 2, False
