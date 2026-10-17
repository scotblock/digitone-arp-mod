"""Independent ZIP/LZ4/project checks, no DNX imports or firmware writes."""
from pathlib import Path
import zipfile,json,zlib,struct,hashlib

p=Path('outputs/Digitone_E08E_ARP_TESTS.dnprj')
with zipfile.ZipFile(p) as archive:
    assert archive.testzip() is None
    entries={n:archive.read(n) for n in archive.namelist()}
manifest=next(json.loads(b) for n,b in entries.items() if n.lower().endswith('.json'))
raw=entries[manifest['Payload']]
assert raw[:4]==bytes.fromhex('ac11d303') and raw[8]==9 and raw[29]==1
assert raw[-4:]==bytes.fromhex('aaa1daaa')
be=lambda a:struct.unpack_from('>I',raw,a)[0]
assert be(len(raw)-12)==zlib.crc32(raw[31:-12],0xffffffff)
assert be(len(raw)-8)==len(raw)-43
image=bytearray();at=31;blocks=0
while True:
    length=be(at);at+=4
    if not length:break
    block=raw[at:at+length];at+=length;i=0;start=len(image)
    def extended(n):
        global i
        if n==15:
            while True:
                b=block[i];i+=1;n+=b
                if b!=255:break
        return n
    while i<len(block):
        token=block[i];i+=1
        n=extended(token>>4);image.extend(block[i:i+n]);i+=n
        if i==len(block):break
        offset=int.from_bytes(block[i:i+2],'little');i+=2
        n=extended(token&15)+4
        assert 0<offset<=len(image)
        for _ in range(n):image.append(image[-offset])
    assert 0<len(image)-start<=32768
    blocks+=1
assert at==len(raw)-12 and len(image)==be(25)==0x2a7404
assert bytes(image)==Path('work/os144/E08E-test-project-image.bin').read_bytes()
seed=Path('work/os144/E08E-project-native-seed.bin').read_bytes()
assert image[:8]==seed[:8] and image[-4:]==bytes.fromhex('bacef00c')
assert image[0x290200:]==seed[0x290200:]
spec=json.loads(Path('work/os144/E08E-test-project-spec.json').read_text())
for slot in range(128):
    pattern=0x200+slot*0x4800;kit=0x240200+slot*0xa00
    assert image[kit+0x1c:kit+0x1c+4*302]==seed[0x240200+127*0xa00+0x1c:0x240200+127*0xa00+0x1c+4*302]
    if slot<16:
        row=spec['rows'][slot]
        assert image[pattern+0x4724:pattern+0x4734].rstrip(b'\0').decode()==row['name']
        assert image[kit+0x54e:kit+0x54e+172]==bytes.fromhex(row['midi_record'])
    for track in range(8):
        base=pattern+4+track*0x3d0
        flags=[int.from_bytes(image[base+s*2:base+s*2+2],'big')&1 for s in range(64)]
        expected={}
        if slot<16:
            kind=spec['rows'][slot]['kind']
            if track==4 and kind in ['chord','both']:expected={0:[60,64,67]}
            if track==4 and kind=='eight':expected={0:[60,62,64,65,67,69,71,72]}
            if track==4 and kind=='wide':expected={0:[48,60,67,72]}
            if track==4 and kind=='retrigger':expected={s:[60,64,67] for s in [0,4,8,12]}
            if track==5 and kind=='m2':expected={s:[60] for s in [0,4,8,12]}
            if track==0 and kind in ['synth','both']:expected=dict(zip([0,4,8,12],[[48],[52],[55],[60]]))
        assert [s for s,f in enumerate(flags) if f]==list(expected),(slot,track)
        for step,notes in expected.items():
            chord=image[base+0x180+step*8:base+0x188+step*8]
            actual=[chord[0]]+[chord[0]+(x if x<128 else x-256) for x in chord[1:] if x]
            assert actual==notes,(slot,track,step,actual,notes)
assert image[0x240200+12*0xa00+0x54e+172:0x240200+12*0xa00+0x54e+344]==bytes.fromhex(spec['M2_record'])
report={'passed':True,'independent_ZIP_CRC_LZ4_check':True,'image_roundtrip_exact':True,
 'all_128_pattern_note_masks_verified':True,'first_16_names_and_native_MIDI_records_verified':True,
 'sounds_and_project_tail_preserved':True,'LZ4_blocks':blocks,'image_bytes':len(image),
 'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'hardware_import_verified':False}
Path('outputs/Digitone-E08E-test-project-independent-check.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
