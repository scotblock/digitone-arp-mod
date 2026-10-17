"""Build pinned upstream CPU fixes with explicit, installed compiler/SDK paths."""
import pathlib,subprocess,os,sys,json,hashlib,shutil
vs=pathlib.Path('LOCAL_FILES/Microsoft Visual Studio/18/BuildTools')
vc=vs/'VC/Tools/MSVC/14.51.36231';sdk=pathlib.Path('LOCAL_FILES/Windows Kits/10');ver='10.0.26100.0'
cmake=vs/'Common7/IDE/CommonExtensions/Microsoft/CMake/CMake/bin/cmake.exe'
ninja=vs/'Common7/IDE/CommonExtensions/Microsoft/CMake/Ninja/ninja.exe'
env=os.environ.copy();env['PATH']=os.pathsep.join([str(vc/'bin/Hostx64/x64'),str(sdk/f'bin/{ver}/x64'),str(pathlib.Path(sys.executable).parent),env['PATH']])
env['INCLUDE']=';'.join(str(p) for p in [vc/'include',sdk/f'Include/{ver}/ucrt',sdk/f'Include/{ver}/shared',sdk/f'Include/{ver}/um',sdk/f'Include/{ver}/winrt'])
env['LIB']=';'.join(str(p) for p in [vc/'lib/x64',sdk/f'Lib/{ver}/ucrt/x64',sdk/f'Lib/{ver}/um/x64'])
src=pathlib.Path('work/upstream/unicorn-source').resolve();build=pathlib.Path('work/unicorn-ninja-build-2').resolve()
subprocess.run([str(cmake),'-S',str(src),'-B',str(build),'-G','Ninja',f'-DCMAKE_MAKE_PROGRAM={ninja.as_posix()}',f'-DCMAKE_C_COMPILER={vc.as_posix()}/bin/Hostx64/x64/cl.exe',f'-DCMAKE_RC_COMPILER={sdk.as_posix()}/bin/{ver}/x64/rc.exe',f'-DCMAKE_MT={sdk.as_posix()}/bin/{ver}/x64/mt.exe','-DCMAKE_BUILD_TYPE=Release','-DUNICORN_ARCH=m68k','-DUNICORN_BUILD_TESTS=OFF'],env=env,check=True)
subprocess.run([str(cmake),'--build',str(build),'--target','unicorn','--parallel','4'],env=env,check=True)
dll=build/'unicorn.dll';assert dll.is_file()
target=pathlib.Path('work/emulator-deps/unicorn/lib/unicorn.dll')
if not target.with_suffix('.stock.dll').exists():shutil.copyfile(target,target.with_suffix('.stock.dll'))
shutil.copyfile(dll,target)
r={'unicorn_commit':'8028ec436f2d9376525352dd38ed9ed6b9f6be10','digiemu_commit':'24a1dcfbb53de52c42b0d3f2f2a2f5029873f0d2','compiler':str(vc),'sdk':ver,'built_dll_sha256':hashlib.sha256(dll.read_bytes()).hexdigest(),'patch_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in pathlib.Path('work/upstream/digiemu/patches').glob('*.patch')},'installation':'workspace-only work/emulator-deps; system Python unchanged'}
pathlib.Path('work/local-cpu-engine-build.json').write_text(json.dumps(r,indent=2));print('Built local CPU engine',r['built_dll_sha256'],flush=True)
