"""PC-only sidecar codec. Not a Digitone project, firmware, or device writer.

The 128 M1 records use the same validated native representation. A sidecar is
bound to the SHA-256 of a specific project file supplied by the caller. Native
project save/load, slot identity and automatic lifecycle adapters are separate.
"""
import hashlib,struct
MAGIC=b'E10SEQ1\n'
RECORD_BYTES=32
PATTERNS=128
BANK_BYTES=RECORD_BYTES*PATTERNS
HEADER_BYTES=80

def validate_record(record):
 if len(record)!=32:raise ValueError('record length')
 if record==bytes(32):return
 if record[:4]!=b'MS10' or record[4]!=1:raise ValueError('record schema')
 if record[5]>1 or not 1<=record[6]<=16 or record[7]>11 or record[8]>35 or record[9]:raise ValueError('record fields')
 if any(not -24<=v<=24 for v in struct.unpack('16b',record[12:28])):raise ValueError('offset range')
 if int.from_bytes(record[28:],'big')!=sum(record[:28]):raise ValueError('record checksum')

def validate_bank(bank):
 if len(bank)!=BANK_BYTES:raise ValueError('bank length')
 for at in range(0,BANK_BYTES,RECORD_BYTES):validate_record(bank[at:at+RECORD_BYTES])

def project_digest(project_sha256):
 if not isinstance(project_sha256,str) or len(project_sha256)!=64:raise ValueError('project SHA-256')
 try:result=bytes.fromhex(project_sha256)
 except ValueError:raise ValueError('project SHA-256') from None
 if len(result)!=32:raise ValueError('project SHA-256')
 return result

def encode(bank,project_sha256):
 bank=bytes(bank);validate_bank(bank)
 return MAGIC+struct.pack('>HHHBB',1,RECORD_BYTES,PATTERNS,0,0)+project_digest(project_sha256)+hashlib.sha256(bank).digest()+bank

def decode(blob,project_sha256):
 # Parse the entire bounded input before handing anything to a state writer.
 if len(blob)!=HEADER_BYTES+BANK_BYTES:raise ValueError('sidecar length')
 if blob[:8]!=MAGIC or blob[8:16]!=struct.pack('>HHHBB',1,RECORD_BYTES,PATTERNS,0,0):raise ValueError('sidecar schema')
 if blob[16:48]!=project_digest(project_sha256):raise ValueError('different project')
 bank=bytes(blob[HEADER_BYTES:])
 if hashlib.sha256(bank).digest()!=blob[48:80]:raise ValueError('bank checksum')
 validate_bank(bank)
 return bank
