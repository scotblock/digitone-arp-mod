#include "firmware.h"
int main(int argc,char **argv) {
 firmware fw;verify_result vr;if(argc!=2 || fw_load(argv[1],&fw))return 1;fw_verify(&fw,&vr);
 printf("packet=%d count=%d content=%d digest=%d all_ok=%d\n",vr.packet_cksum,vr.packet_count,vr.content_cksum,vr.digest,vr.all_ok);
 for(unsigned j=0;j<vr.nsections;j++)printf("section=%u stream_sum=%d decoded=%zu\n",vr.sections[j].id,vr.sections[j].stream_sum,vr.sections[j].decompressed_len);
 int ok=vr.all_ok;fw_free(&fw);return ok?0:2;
}
