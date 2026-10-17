#include "aplib.h"
#include "util.h"
int main(int argc,char **argv) {
 size_t n; if(argc!=3)return 1;uint8_t *in=read_file(argv[1],&n);if(!in)return 2;
 size_t cap=n*2+1024;uint8_t *out=malloc(cap),*decoded=malloc(n+1024);
 size_t packed=ap_pack(in,n,out,cap,2);if(packed==(size_t)-1)return 3;
 size_t unpacked=ap_depack(out,packed,decoded,n+1024,0);
 if(unpacked!=n || memcmp(in,decoded,n))return 4;
 FILE *f=fopen(argv[2],"wb");if(!f)return 5;fwrite(out,1,packed,f);fclose(f);
 printf("input=%zu packed=%zu roundtrip=ok\n",n,packed);free(in);free(out);free(decoded);return 0;
}
