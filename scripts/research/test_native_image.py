import hashlib,sqlite3,struct,tempfile,unittest
from contextlib import closing
from pathlib import Path
from native_image import Image,build


def fixture():
    b=bytearray(0x800);b[:2]=b'MZ';struct.pack_into('<I',b,0x3c,0x80);b[0x80:0x84]=b'PE\0\0'
    struct.pack_into('<HHIIIHH',b,0x84,0x8664,3,0,0,0,240,0x22)
    opt=0x98;struct.pack_into('<H',b,opt,0x20b);struct.pack_into('<Q',b,opt+24,0x140000000)
    struct.pack_into('<II',b,opt+56,0x4000,0x200);struct.pack_into('<I',b,opt+108,16)
    struct.pack_into('<II',b,opt+112+24,0x2000,12)
    for i,(name,rva,offset,flags) in enumerate([(b'.text',0x1000,0x200,0x60000020),
                                               (b'.pdata',0x2000,0x400,0x40000040),(b'.rdata',0x3000,0x600,0x40000040)]):
        at=opt+240+40*i;b[at:at+len(name)]=name
        struct.pack_into('<IIII',b,at+8,0x200,rva,0x200,offset);struct.pack_into('<I',b,at+36,flags)
    struct.pack_into('<III',b,0x400,0x1000,0x1020,0x2020)
    b[0x200:0x207]=b'\x48\x8d\x05'+struct.pack('<i',0x3000-0x1007)
    b[0x207]=0xc3;signature=b'() ctor (vec3)\0';b[0x600:0x600+len(signature)]=signature
    return b


class NativeImageTests(unittest.TestCase):
    def test_mapping_and_runtime_range(self):
        image=Image(fixture());self.assertEqual(image.file_offset(0x1007),0x207)
        self.assertEqual(image.rva_for_offset(0x600),0x3000)
        self.assertEqual(image.containing_runtime_ranges(0x1010)[0]['file_offset'],0x200)
        self.assertEqual(image.containing_runtime_ranges(0x1020),[])

    def test_signature_leads_are_not_promoted_to_decoded_bindings(self):
        image=Image(fixture());s=image.signatures();self.assertEqual(len(s),1)
        leads=image.relative_signature_leads(s);self.assertEqual(leads[0]['target_rva'],0x3000)
        self.assertEqual(leads[0]['containing_runtime_begin_rvas'],[0x1000])
        self.assertIn('not_decoded_or_bound',leads[0]['status'])

    def test_all_truncations_reject(self):
        b=fixture()
        for length in range(len(b)):
            with self.assertRaises(ValueError):Image(b[:length])

    def test_unbacked_tail_and_cross_section_rejected(self):
        b=fixture();struct.pack_into('<I',b,0x188+8,0x300)
        image=Image(b)
        for rva,width in [(0x1200,1),(0x11ff,2),(0x1ff,2),(-1,1),(0x1000,0)]:
            with self.assertRaises(ValueError):image.file_offset(rva,width)
        with self.assertRaises(ValueError):image.rva_for_offset(0x3ff,2)

    def test_bad_headers_directories_and_ranges(self):
        variants=[]
        for at,fmt,value in [(0x84,'<H',0x14c),(0x98,'<H',0x10b),(0x98+108,'<I',17),
                             (0x98+112+28,'<I',13),(0x404,'<I',0x1000),(0x400,'<I',0x3000)]:
            b=fixture();struct.pack_into(fmt,b,at,value);variants.append(b)
        for b in variants:
            with self.assertRaises(ValueError):Image(b)

    def test_overlap_rejection_and_duplicate_runtime_retention(self):
        b=fixture();struct.pack_into('<I',b,0x1b0+12,0x1000)
        with self.assertRaises(ValueError):Image(b)
        b=fixture();struct.pack_into('<I',b,0x98+112+28,24);b[0x40c:0x418]=b[0x400:0x40c]
        image=Image(b);self.assertEqual(len(image.containing_runtime_ranges(0x1001)),2)

    def test_build_identity_and_overwrite_rejection(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            root=Path(directory);source=root/'fixture.bin';source.write_bytes(fixture());output=root/'out'
            report=build(source,output);self.assertEqual(report['source_sha256'],hashlib.sha256(source.read_bytes()).hexdigest())
            with closing(sqlite3.connect(output/'native.sqlite')) as db:self.assertEqual(db.execute('select count(*) from leads').fetchone()[0],1)
            with self.assertRaises(FileExistsError):build(source,output)


if __name__=='__main__':unittest.main()
