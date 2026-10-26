"""Compile project C# against installed Unity reference DLLs; does NOT run the editor or physics."""
import os
from pathlib import Path
import subprocess
import tempfile
import json

ROOT=Path(__file__).resolve().parents[1]
UNITY=Path('/workspace/toolchains/unity-6000.6.7f1/Editor/Data')

def main():
    dotnet=UNITY/'DotNetSdk/dotnet'
    compilers=sorted((UNITY/'DotNetSdk/sdk').glob('*/Roslyn/bincore/csc.dll'))
    if not dotnet.exists() or not compilers:raise RuntimeError('Install the official Unity editor first')
    refs={p.name:p for p in (UNITY/'UnityReferenceAssemblies/unity-4.8-api').glob('*.dll')}
    refs.update({p.name:p for p in (UNITY/'UnityReferenceAssemblies/unity-4.8-api/Facades').glob('*.dll')})
    refs.update({p.name:p for p in (UNITY/'Managed/UnityEngine').glob('*.dll')})
    input_dll=UNITY/'Resources/PackageManager/ProjectTemplates/libcache/com.unity.template.urp-blank-17.2.6/ScriptAssemblies/Unity.InputSystem.dll'
    if not input_dll.is_file():raise RuntimeError('Official bundled Input System assembly is missing')
    refs['Unity.InputSystem.dll']=input_dll
    with tempfile.TemporaryDirectory(prefix='machu-csharp-') as directory:
        directory=Path(directory)
        for category,source in [('Runtime','Scripts'),('Editor','Editor')]:
            target=directory/f'MachuPicchu.{category}.dll'
            arguments=['/nologo','/target:library','/nostdlib+','/langversion:9.0',f'/out:"{target}"']
            arguments.extend('/reference:"'+str(p)+'"' for p in refs.values())
            if category=='Editor':arguments.append('/reference:"'+str(directory/'MachuPicchu.Runtime.dll')+'"')
            arguments.extend('"'+str(p)+'"' for p in sorted((ROOT/'Assets/MachuPicchu'/source).glob('*.cs')))
            response=directory/f'{category}.rsp';response.write_text('\n'.join(arguments)+'\n')
            environment=os.environ.copy();environment['DOTNET_CLI_HOME']=str(directory);environment['DOTNET_SKIP_FIRST_TIME_EXPERIENCE']='1'
            result=subprocess.run([str(dotnet),str(compilers[-1]),'@'+str(response)],env=environment,text=True,capture_output=True)
            print(result.stdout,end='');print(result.stderr,end='')
            if result.returncode:raise SystemExit(result.returncode)
            assert target.is_file();print(category+' C# assembly compiled successfully')
    report={'unityReferences':'6000.6.7f1','inputSystem':'1.20.1 (official editor bundle)','runtimeCSharp':'passed','editorCSharp':'passed','editorExecution':'not covered','physicsAndRendering':'not covered'}
    (ROOT/'Artifacts/csharp-validation.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
