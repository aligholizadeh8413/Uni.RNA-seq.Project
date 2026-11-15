#!/usr/bin/env python3
"""Audited single-end RNA-seq project. Standard library only; run in Compose."""
import csv
import gzip
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path('/work')
LOG = ROOT / 'reports/logs'
RAW_SHA = '4e557461b7f65e8cbfa3ce315d16fda98947fc5b52e8d0cf9c9945afa266b297'
REFS = [
 ('reference/grch38_genome.tar.gz', 'https://genome-idx.s3.amazonaws.com/hisat/grch38_genome.tar.gz', '1bbb761c9e1b33eda3f6daf087dec08689b1df48efc4964581f9a3d39b863188'),
 ('reference/Homo_sapiens.GRCh38.106.gtf.gz', 'https://ftp.ensembl.org/pub/release-106/gtf/homo_sapiens/Homo_sapiens.GRCh38.106.gtf.gz', '9f9cc8ea19f03659875a4a3b57220c379f0282b4c361fc7cb637e6f083967871')]
GTF = 'reference/Homo_sapiens.GRCh38.106.gtf'
INDEX = 'reference/grch38/genome'
BAM = 'data/demo.sorted.bam'
COUNTS = 'data/demo_counts.txt'
MODE = sys.argv[1] if len(sys.argv) > 1 else '--verify-existing'
MANIFEST = LOG / 'pipeline_checkpoint.json'
STATE = {}

def require(ok, message):
    if not ok:
        raise RuntimeError(message)

def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(4*1024*1024), b''):
            h.update(block)
    return h.hexdigest()

def write_json(path, value):
    path = Path(path)
    temp = path.with_name(path.name + '.pending')
    temp.write_text(json.dumps(value, indent=2) + '\n')
    temp.replace(path)

def capture(args):
    return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT)

def run(args, logname):
    print('+ ' + ' '.join(args), flush=True)
    with (LOG/logname).open('w') as f:
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in p.stdout:
            print(line, end='', flush=True)
            f.write(line)
        require(p.wait() == 0, f'Command failed; inspect {LOG/logname}')

def space(gib):
    require(shutil.disk_usage(ROOT).free >= gib*1024**3,
            f'Need at least {gib} GiB free before this operation')

def fastq_stats(path):
    lengths = Counter()
    bases = Counter()
    reads_with_n = 0
    qmin, qmax = 127, 0
    with open(path, 'rb') as f:
        while True:
            h = f.readline()
            if not h:
                break
            record = [h, f.readline(), f.readline(), f.readline()]
            require(all(record), f'Truncated FASTQ: {path}')
            h, s, p, q = [x.rstrip(b'\r\n') for x in record]
            require(h.startswith(b'@') and h[1:].strip() and p.startswith(b'+'), 'Invalid FASTQ header')
            require(s and len(s) == len(q), 'Sequence/quality length mismatch')
            require(not (set(s.upper())-set(b'ACGTRYSWKMBDHVN')), 'Unexpected base')
            require(min(q) >= 33 and max(q) <= 126, 'Invalid quality character')
            if p[1:].strip():
                require(p[1:].split()[0] == h[1:].split()[0], 'FASTQ identifier mismatch')
            lengths[len(s)] += 1
            bases.update(s.upper())
            reads_with_n += int(b'N' in s.upper())
            qmin, qmax = min(qmin, min(q)), max(qmax, max(q))
    require(bool(lengths), 'No FASTQ records')
    n = sum(lengths.values())
    return dict(reads=n, lines=4*n, size_bytes=Path(path).stat().st_size,
                length_distribution=dict(sorted(lengths.items())), length_min=min(lengths),
                length_max=max(lengths), length_mean=sum(bases.values())/n,
                bases=sum(bases.values()), N_bases=bases[78], reads_with_N=reads_with_n,
                phred33_Q_min=qmin-33, phred33_Q_max=qmax-33,
                sha256=sha(path), structure_valid=True)

def qc_check(path, expected_reads):
    with zipfile.ZipFile(path) as z:
        require(z.testzip() is None, 'Corrupt FastQC ZIP')
        name = next(n for n in z.namelist() if n.endswith('/fastqc_data.txt'))
        text = z.read(name).decode()
        n = int(re.search(r'^Total Sequences\t(\d+)', text, re.M)[1])
        require(n == expected_reads, 'FastQC count mismatch')

def prepare_references():
    # Downloads and extraction are explicit only under --run.
    for name, url, checksum in REFS:
        p = Path(name)
        if not p.exists():
            require(MODE == '--run', f'Missing reference archive: {name}')
            space(10)
            run(['curl','--fail','--location','--retry','5','--connect-timeout','30',
                 '--continue-at','-','--output',name+'.part',url],p.name+'.download.log')
            require(sha(name+'.part') == checksum, 'Downloaded reference checksum mismatch')
            Path(name+'.part').replace(p)
        require(sha(p) == checksum, f'Reference archive checksum mismatch: {name}')
    inventory = json.loads(Path('tools/reference_inventory.json').read_text())
    missing = []
    for item in inventory['archive_members']:
        if not item['bytes']:
            continue
        p = Path('reference')/item['path']
        if p.exists():
            require(p.stat().st_size == item['bytes'], f'Partial reference: {p}; inspect manually')
        else:
            missing.append(item['path'])
    if missing or not Path(GTF).exists():
        require(MODE == '--run', 'References not extracted; use --run after reviewing disk space')
        space(inventory['total_expanded_GiB'] + 6)
    if missing:
        with tarfile.open(REFS[0][0], 'r|gz') as tar:
            for m in tar:
                require(not Path(m.name).is_absolute() and '..' not in Path(m.name).parts, 'Unsafe archive')
                require(m.isfile() or m.isdir(), 'Unsupported archive entry')
                if m.isfile() and m.name in missing:
                    p = Path('reference')/m.name
                    p.parent.mkdir(parents=True, exist_ok=True)
                    with tar.extractfile(m) as src, p.open('xb') as dst:
                        shutil.copyfileobj(src,dst)
    if not Path(GTF).exists():
        with gzip.open(REFS[1][0],'rb') as src, open(GTF+'.part','wb') as dst:
            shutil.copyfileobj(src,dst)
        Path(GTF+'.part').replace(GTF)
    require(Path(GTF).stat().st_size == inventory['gtf_expanded_bytes'], 'GTF size mismatch')
    for item in inventory['archive_members']:
        if item['bytes']:
            require((Path('reference')/item['path']).stat().st_size == item['bytes'], 'Index size mismatch')
    summary = capture(['hisat2-inspect','-s',INDEX])
    (LOG/'verified_index_summary.txt').write_text(summary)
    # Full content hashes also detect later changes to extracted references.
    return {GTF:sha(GTF), **{f'{INDEX}.{i}.ht2':sha(f'{INDEX}.{i}.ht2') for i in range(1,9)}}

def stage(name, outputs, command, check, inputs):
    signature = hashlib.sha256(json.dumps([command,inputs,STATE['environment']],sort_keys=True).encode()).hexdigest()
    old = STATE['stages'].get(name)
    existing = [Path(p).exists() for p in outputs]
    if old:
        require(old['signature'] == signature, f'{name}: inputs or environment changed; use a separate project copy')
        require(all(existing), f'{name}: checkpoint output missing')
        require(all(sha(p) == old['outputs'][p] for p in outputs), f'{name}: output content changed')
        print(f'REUSE verified checkpoint: {name}',flush=True)
    elif any(existing):
        require(all(existing), f'{name}: incomplete output set; inspect before retrying')
        require(MODE == '--verify-existing', f'{name}: existing outputs lack checkpoint; run --verify-existing first')
        print(f'AUDIT existing output: {name}',flush=True)
    else:
        require(MODE == '--run', f'{name}: output missing')
        space(4)
        if name == 'alignment':
            mem_kb = int(re.search(r'MemTotal:\s+(\d+)',Path('/proc/meminfo').read_text())[1])
            require(mem_kb >= 5*1024**2, 'Docker RAM below 5 GiB')
        run(command, name+'.pipeline.log')
    check()
    entry = dict(signature=signature, outputs={p:sha(p) for p in outputs},command=command)
    STATE['stages'][name] = entry
    write_json(MANIFEST,STATE)
    return entry['outputs']

def verify_alignment():
    require(int(capture(['samtools','view','-c','-F','2304','data/demo.sam']).strip()) == 1249800,'SAM primary count mismatch')
    require(int(capture(['samtools','view','-c','-F','2308','data/demo.sam']).strip()) == 1163237,'SAM mapped primary count mismatch')
    header = capture(['samtools','view','-H','data/demo.sam'])
    require('--rna-strandness R' in header, 'Missing R parameter in SAM program header')

def verify_bam():
    subprocess.run(['samtools','quickcheck','-v',BAM],check=True)
    header = capture(['samtools','view','-H',BAM])
    require('SO:coordinate' in header,'BAM is not coordinate sorted')
    require(int(capture(['samtools','view','-c','-F','2304',BAM]).strip())==1249800,'BAM primary count mismatch')
    require(int(capture(['samtools','view','-c',BAM]).strip())==1430243,'BAM alignment count mismatch')
    (LOG/'verified_bam_flagstat.txt').write_text(capture(['samtools','flagstat',BAM]))

def compatibility():
    refs={}
    for line in capture(['samtools','view','-H',BAM]).splitlines():
        if line.startswith('@SQ\t'):
            d=dict(x.split(':',1) for x in line.split('\t')[1:]);refs[d['SN']]=int(d['LN'])
    chromosomes=set();exons=0
    with open(GTF) as f:
        for line in f:
            if line.startswith('#') or not line.strip(): continue
            fields=line.rstrip('\n').split('\t')
            require(len(fields)==9,'Invalid GTF')
            if fields[2]!='exon':continue
            exons+=1;chromosomes.add(fields[0])
            require('gene_id "' in fields[8],'Missing exon gene_id')
            if fields[0] in refs:require(int(fields[4])<=refs[fields[0]],'GTF coordinate outside reference')
    require(exons==1572538 and chromosomes <= refs.keys(),'GTF/reference mismatch')
    write_json(LOG/'verified_compatibility.json',dict(exon_rows=exons,shared_chromosomes=len(chromosomes)))

def verify_counts():
    with open(COUNTS) as f:
        first=f.readline()
        require('featureCounts v2.0.3' in first and '"-s" "2"' in first or
                'featureCounts v2.0.3' in first and '-s 2' in first,'Count provenance mismatch')
        rows=list(csv.DictReader((l for l in f if not l.startswith('#')),delimiter='\t'))
    key=list(rows[0])[-1];values=[int(r[key]) for r in rows]
    with open(COUNTS+'.summary') as f:
        reader=csv.reader(f,delimiter='\t');next(reader);summary={r[0]:int(r[1]) for r in reader}
    require(len(rows)==61552 and sum(v>0 for v in values)==17875,'Gene count table mismatch')
    require(sum(values)==summary['Assigned']==913764,'Assigned/count sum mismatch')
    require(sum(summary.values())==1430243,'Assignment record total mismatch')
    write_json(LOG/'verified_counts.json',dict(genes=len(rows),nonzero_genes=sum(v>0 for v in values),sum_counts=sum(values),assignment=summary))

def main():
    global STATE
    require(MODE in ['--verify-existing','--run'],'Invalid mode')
    os.chdir(ROOT)
    for directory in ['reports/logs','reports/fastqc_before','reports/fastqc_after','reference','tools','data']:
        Path(directory).mkdir(parents=True,exist_ok=True)
    if not Path('tools/trimmomatic-0.39.jar').exists():
        require(MODE == '--run', 'Missing JAR; copy the original tools JAR or use --run')
        shutil.copyfile('/opt/rnaseq/trimmomatic-0.39.jar','tools/trimmomatic-0.39.jar')
    versions={}
    for name,args,expected in [
        ('FastQC',['fastqc','--version'],'0.11.9'),
        ('Trimmomatic',['java','-jar','tools/trimmomatic-0.39.jar','-version'],'0.39'),
        ('HISAT2',['hisat2','--version'],'2.2.1'),
        ('samtools',['samtools','--version'],'1.16.1'),
        ('featureCounts',['featureCounts','-v'],'2.0.3')]:
        text=capture(args);require(expected in text,f'Unexpected {name} version');versions[name]=text
    environment=dict(versions=versions,image_id=os.environ.get('RNASEQ_IMAGE_ID','unknown'))
    if MANIFEST.exists():
        STATE=json.loads(MANIFEST.read_text())
        require(STATE['environment']==environment,'Image or tool versions changed')
    else:
        STATE=dict(environment=environment,stages={})
    print('Reading and validating full original FASTQ...',flush=True)
    raw=fastq_stats('data/demo.fastq')
    require(raw['sha256']==RAW_SHA,'Original FASTQ differs from the audited project')
    write_json(LOG/'verified_raw_fastq.json',raw)
    refs=prepare_references()
    qc0=stage('fastqc_before',['reports/fastqc_before/demo_fastqc.html','reports/fastqc_before/demo_fastqc.zip'],
       ['fastqc','--threads','1','data/demo.fastq','-o','reports/fastqc_before'],
       lambda:qc_check('reports/fastqc_before/demo_fastqc.zip',1250000),{'raw':RAW_SHA})
    def trimcheck():
        stats=fastq_stats('data/demo_trimmed.fastq')
        require(stats['reads']==1249800 and stats['bases']==118694982,'Trimmed FASTQ does not match audited results')
        write_json(LOG/'verified_trimmed_fastq.json',stats)
    trimmed=stage('trimming',['data/demo_trimmed.fastq'],
       ['java','-jar','tools/trimmomatic-0.39.jar','SE','-threads','4','-phred33','data/demo.fastq','data/demo_trimmed.fastq','TRAILING:10'],
       trimcheck,{'raw':RAW_SHA,'jar':sha('tools/trimmomatic-0.39.jar')})
    stage('fastqc_after',['reports/fastqc_after/demo_trimmed_fastqc.html','reports/fastqc_after/demo_trimmed_fastqc.zip'],
       ['fastqc','--threads','1','data/demo_trimmed.fastq','-o','reports/fastqc_after'],
       lambda:qc_check('reports/fastqc_after/demo_trimmed_fastqc.zip',1249800),trimmed)
    sam=stage('alignment',['data/demo.sam'],
       ['hisat2','-q','--rna-strandness','R','-x',INDEX,'-U','data/demo_trimmed.fastq','-S','data/demo.sam'],
       verify_alignment,{**trimmed,**refs})
    bam=stage('sort',[BAM],['samtools','sort','-o',BAM,'data/demo.sam'],verify_bam,sam)
    def indexcheck():
        # Region lookup explicitly exercises the BAI; idxstats alone can fall back to scanning.
        capture(['samtools','view','-c',BAM,'1:1-100000'])
        (LOG/'verified_bam_idxstats.txt').write_text(capture(['samtools','idxstats',BAM]))
    stage('index',[BAM+'.bai'],['samtools','index',BAM],indexcheck,bam)
    compatibility()
    stage('counts',[COUNTS,COUNTS+'.summary'],
       ['featureCounts','-s','2','-a',GTF,'-o',COUNTS,BAM],verify_counts,{**bam,'gtf':refs[GTF]})
    require(sha('data/demo.fastq')==RAW_SHA,'Original input changed during execution')
    print('PIPELINE_VERIFIED_OK',flush=True)

if __name__=='__main__':
    try: main()
    except Exception as exc:
        print(f'ERROR: {exc}',file=sys.stderr)
        sys.exit(1)
