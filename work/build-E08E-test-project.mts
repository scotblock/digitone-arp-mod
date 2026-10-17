import {readFileSync,writeFileSync} from 'node:fs';
import {randomBytes,createHash} from 'node:crypto';
import {buildContainer,parsePayload} from './upstream/DNX/packages/core/src/project/container.ts';
import {buildProjectFile,parseProject} from './upstream/DNX/src/node/projectfile.ts';
import {decodeProjectImage} from './upstream/DNX/packages/core/src/project/dn2codec.ts';
import {checkDn1Image,readPattern} from './upstream/DNX/packages/core/src/project/dn1.ts';
import {crc32ZeroInit} from './upstream/DNX/packages/core/src/project/checksum.ts';

const seed=new Uint8Array(readFileSync('work/os144/E08E-project-native-seed.bin'));
const spec=JSON.parse(readFileSync('work/os144/E08E-test-project-spec.json','utf8'));
const initial=checkDn1Image(seed);if(!initial.ok)throw new Error(JSON.stringify(initial));
const image=seed.slice();const dv=new DataView(image.buffer);
const ps=0x4800,ks=0xa00,pb=0x200,kb=0x240200,ts=0x3d0;
const template=seed.slice(pb+127*ps,pb+128*ps);
const kit=seed.slice(kb+127*ks,kb+128*ks);
function name(at:number,text:string){image.fill(0,at,at+16);image.set(new TextEncoder().encode(text),at);}
function note(slot:number,track:number,step:number,notes:number[],length:number){
 const at=pb+slot*ps+4+track*ts;
 dv.setUint16(at+step*2,(dv.getUint16(at+step*2,false)&0xfffc)|1,false);
 image[at+0x80+step]=100;image[at+0xc0+step]=length;
 image.fill(0,at+0x180+step*8,at+0x180+(step+1)*8);
 image[at+0x180+step*8]=notes[0];
 notes.slice(1).forEach((n,i)=>image[at+0x180+step*8+i+1]=(n-notes[0])&255);
}
for(let slot=0;slot<128;slot++){
 image.set(template,pb+slot*ps);image.set(kit,kb+slot*ks);
 for(let t=0;t<8;t++){
   const at=pb+slot*ps+4+t*ts;
   for(let s=0;s<64;s++){
     dv.setUint16(at+s*2,(s&1)?0x10:0,false);
     image[at+0x80+s]=255;image[at+0xc0+s]=255;image[at+0x100+s]=0;image[at+0x140+s]=255;image[at+0x380+s]=255;
     image.fill(0,at+0x180+s*8,at+0x180+(s+1)*8);image[at+0x180+s*8]=255;
   }
   image[at+0x3cc]=16;image[at+0x3cd]=2;
 }
 for(let l=0;l<80;l++)image.fill(255,pb+slot*ps+0x1e84+l*130,pb+slot*ps+0x1e84+(l+1)*130);
 name(pb+slot*ps+0x4724,'UNTITLED');dv.setUint16(pb+slot*ps+0x4736,120*120,false);image[pb+slot*ps+0x4741]=slot;
}
name(8,spec.name);image.set(randomBytes(4),0x18);
for(const r of spec.rows){
 const slot=r.slot;name(pb+slot*ps+0x4724,r.name);
 image.set(Buffer.from(r.midi_record,'hex'),kb+slot*ks+0x54e);
 if(['chord','both'].includes(r.kind))note(slot,4,0,[60,64,67],76);
 if(r.kind==='eight')note(slot,4,0,[60,62,64,65,67,69,71,72],76);
 if(r.kind==='wide')note(slot,4,0,[48,60,67,72],76);
 if(r.kind==='retrigger')for(const s of [0,4,8,12])note(slot,4,s,[60,64,67],30);
 if(r.kind==='m2'){
   image.set(Buffer.from(spec.M2_record,'hex'),kb+slot*ks+0x54e+172);
   for(const s of [0,4,8,12])note(slot,5,s,[60],14);
 }
 if(['synth','both'].includes(r.kind))for(const [i,s] of [0,4,8,12].entries())note(slot,0,s,[48+[0,4,7,12][i]],14);
}
const checked=checkDn1Image(image);if(!checked.ok)throw new Error(JSON.stringify(checked));
const raw=buildContainer({body:image,contentKind:1,objectVersion:dv.getUint32(4,false),index:0,device:9,formatVersion:'0107'});
const manifest={FormatVersion:'1.0',ProductType:['24','30'],Payload:'E08E ARP TESTS',FileType:'Project',FirmwareVersion:'1.44'};
const file=buildProjectFile(manifest,raw,image);
const parsed=parseProject(file);const decoded=decodeProjectImage(parsed.payload.raw).image;
if(!Buffer.from(decoded).equals(Buffer.from(image)))throw new Error('Project image did not round-trip');
const body=parsed.payload.raw.subarray(31,-12);const footer=new DataView(parsed.payload.raw.buffer,parsed.payload.raw.byteOffset);
if(footer.getUint32(parsed.payload.raw.length-12,false)!==crc32ZeroInit(body))throw new Error('CRC');
const rows=spec.rows.map((r:any)=>{
 const p=readPattern(decoded,r.slot);return {...r,midi_record:undefined,decoded:p};
});
writeFileSync('work/os144/E08E-test-project-image.bin',image);
writeFileSync('outputs/Digitone_E08E_ARP_TESTS.dnprj',file);
writeFileSync('outputs/Digitone-E08E-test-project-validation.json',JSON.stringify({passed:true,
 hardware_import_verified:false,seed:'Native OS 1.44 saved emulator project, wrapper removed at verified 0x110 offset',
 dn1_structural_check:checked,project_image_bytes:image.length,file_bytes:file.length,
 sha256:createHash('sha256').update(file).digest('hex'),manifest:parsed.manifest,
 native_MIDI_record_encode_decode:true,exact_image_roundtrip:true,CRC_checked:true,
 M1_output_channel:9,M2_output_channel:10,patterns:rows},null,2));
console.log('Created Digitone 1 project:',file.length,'bytes; 16 patterns; DNX structural/codec/CRC checks passed.');
