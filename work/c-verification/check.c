#include "firmware.h"
#include "aplib.h"
#include "util.h"
int main(int argc,char **argv) {
 firmware fw; verify_result vr;
 if(argc!=2 || fw_load(argv[1],&fw)) return 1;
 fw_verify(&fw,&vr);
 printf("packet=%d count=%d content=%d digest=%d key_found=%d\n",vr.packet_cksum,vr.packet_count,vr.content_cksum,vr.digest,fw.bin.have_key);
 for(unsigned i=0;i<fw.bin.nsections;i++) {
  ele3_section *s=&fw.bin.sections[i];
  size_t n=container_section_depack(&fw.bin,s,fw.scratch,fw.scratch_cap);
  printf("section=%u decoded=%zu\n",s->id,n);
  if(n!=(size_t)-1 && n>0) {
   char name[100];snprintf(name,sizeof name,"work/c-section-%u.bin",s->id);
   FILE *f=fopen(name,"wb"); if(!f)return 2;fwrite(fw.scratch,1,n,f);fclose(f);
  }
 }
 fw_free(&fw);return 0;
}
