# یادداشت‌های اجرای علمی

برای نصب و ساختار مخزن، README ریشه را ملاک قرار دهید؛ متن زیر جزئیات بستهٔ اولیهٔ تحویل است.

# RNAseq-MiniProject — راهنمای اجرای نهایی

این بسته مکمل پروژهٔ اجراشده روی مک است. دادهٔ اصلی، SAM، BAM و مرجع حجیم در بسته نیستند؛ فایل‌های واقعی آن‌ها در پوشهٔ پروژهٔ شما باقی می‌مانند.

## نتیجهٔ تأییدشده

| شاخص | مقدار |
|---|---:|
| خوانش خام | 1,250,000 |
| خوانش پس از Trimming | 1,249,800 |
| خوانش نگاشت‌شده | 1,163,237 (93.07%) |
| کل رکوردهای هم‌ترازی BAM | 1,430,243 |
| رکوردهای secondary | 180,443 |
| ژن‌های جدول | 61,552 |
| ژن‌های دارای Count غیرصفر | 17,875 |
| ژن‌های صفر | 43,677 |
| مجموع Count و Assigned | 913,764 |

Assigned برابر 63.8887% از رکوردهای featureCounts و 73.1128% از خوانش‌های پس از Trimming است. مخرج‌ها را مخلوط نکنید. هیچ نمونهٔ کوچک یا دادهٔ مصنوعی به‌عنوان نتیجه استفاده نشده است.

## قرار دادن فایل‌ها روی مک

مسیر پروژهٔ موجود:

```text
/Users/aligholizadeh/Desktop/RNAseq-MiniProject
```

از بستهٔ بازشده، `run_pipeline.sh`، `README.md` و `Presentation.pdf` را در ریشهٔ پروژه کپی کنید. پوشه‌های `tools`، `figures`، `results` و `evidence` این بسته و فایل `Defense_Guide.md` را هم کنار آن‌ها قرار دهید. پوشهٔ tools را **ادغام** کنید، جایگزین نکنید؛ JAR موجود باید حفظ شود. این بسته هیچ فایل داده یا مرجع اصلی را جایگزین نمی‌کند.

`evidence/reports` نسخهٔ گزارش‌هایی است که برای تهیهٔ ارائه ارسال شده‌اند. مسیر اجرایی واقعی همچنان `reports/` است. جدول‌های داخل `results/` کپی نتایج تأییدشده‌اند؛ خروجی اجرایی واقعی در `data/` قرار دارد.

## اولین اجرا: فقط بررسی خروجی‌های موجود

Docker Desktop باید آماده باشد. در Terminal:

```bash
cd "$HOME/Desktop/RNAseq-MiniProject"
bash run_pipeline.sh --verify-existing
```

این حالت هیچ مرحلهٔ تحلیل یا دانلود مرجع را دوباره اجرا نمی‌کند. فایل‌ها را برای بررسی checksum، ساختار، شمارش‌ها و سازگاری مرجع می‌خواند؛ گزارش‌های `verified_*` و checkpoint تولید می‌کند. خواندن چند گیگابایت مرجع برای هش‌گیری ممکن است چند دقیقه زمان ببرد و با اجرای دوبارهٔ نگاشت متفاوت است. پایان موفق: `PIPELINE_VERIFIED_OK`.

کد نهایی از نظر syntax و کنترل‌های محاسباتی در محیط تهیهٔ بسته بررسی شده است، اما اجرای یکپارچهٔ همین نسخه روی مک شما هنوز انجام نشده؛ برای تأیید نهایی خروجی این فرمان را ارسال کنید. مراحل علمی اصلی قبلاً روی فایل کامل شما اجرا و از گزارش‌های ارسالی بررسی شده‌اند.

## اجرای قابل‌تکرار

```bash
bash run_pipeline.sh --run
```

مراحل دارای checkpoint معتبر و هش‌های یکسان دوباره اجرا نمی‌شوند. تغییر ورودی، Image یا خروجی باعث توقف می‌شود. خروجی موجود بدون checkpoint باید ابتدا با `--verify-existing` بررسی شود. خروجی ناقص را اسکریپت خودکار حذف نمی‌کند. برای اجرای کامل از صفر، از پوشهٔ جداگانه با همان ورودی، Compose، ابزارها و اسکریپت استفاده کنید؛ وجود بخشی از خروجی‌های قبلی در حالت run باعث توقف محافظتی خواهد شد.

اسکریپت برای **همین دادهٔ استاد و همین نسخه‌ها** تنظیم شده است؛ برای دادهٔ دیگر باید checksum و انتظارهای آماری با بررسی علمی تغییر کنند. دانلود مرجع در حالت run قابل ادامه است؛ hash مرجع با نسخهٔ دانلودشده و تأییدشدهٔ این پروژه کنترل می‌شود. این hash ثبت محلی است، نه امضای مستقل ناشر.

نسخه‌ها: FastQC 0.11.9، Trimmomatic 0.39، HISAT2 2.2.1، samtools 1.16.1، featureCounts 2.0.3؛ Java 17 و Python 3.11.2 داخل Linux ARM64. Image موجود: `rnaseq-miniproject:bookworm-arm64-v1`. نمونهٔ تنظیمات برای نصب مجدد در `setup_templates/` است؛ آن‌ها را روی تنظیمات فعلی بازنویسی نکنید.

## دستورهای علمی نهایی داخل کانتینر

```bash
fastqc --threads 1 data/demo.fastq -o reports/fastqc_before
java -jar tools/trimmomatic-0.39.jar SE -threads 4 -phred33 \
  data/demo.fastq data/demo_trimmed.fastq TRAILING:10
fastqc --threads 1 data/demo_trimmed.fastq -o reports/fastqc_after
hisat2 -q --rna-strandness R -x reference/grch38/genome \
  -U data/demo_trimmed.fastq -S data/demo.sam
samtools sort -o data/demo.sorted.bam data/demo.sam
samtools index data/demo.sorted.bam
featureCounts -s 2 -a reference/Homo_sapiens.GRCh38.106.gtf \
  -o data/demo_counts.txt data/demo.sorted.bam
```

با `docker compose run --rm -T bio` این فرمان‌ها در `/work` اجرا می‌شوند. `/work` به پوشهٔ پروژهٔ مک متصل است و `data/demo.fastq` به‌صورت read-only در کانتینر mount می‌شود. داده و مرجع وارد Image نمی‌شوند.

تفاوت با جزوه: مسیر گزارش FastQC به `reports/`، JAR به `tools/` و مرجع به `reference/` منتقل شده؛ لینک GTF با HTTPS استفاده می‌شود. نسخهٔ Annotation و پارامترهای علمی ثابت‌اند. `--threads 1` در FastQC فقط تعداد فایل‌های هم‌زمان را تعیین می‌کند.

## منابع و فضای دیسک

شاخص فشرده 4,210,306,865 بایت و GTF فشرده 51,379,459 بایت است. مجموع حجم بازشده 5.4788 GiB است. برای اجرای از صفر به فضای هم‌زمان آرشیوها، مرجع بازشده، FASTQها، SAM/BAM و حاشیهٔ آزاد نیاز است؛ حدود 20 GiB فضای آزاد اولیه انتخاب محتاطانه‌ای است و اندازهٔ واقعی هنگام اجرا کنترل می‌شود. مقدار فضای مشاهده‌شده از کانتینر را با `df -h .` روی مک هم بررسی کنید.

برای نگاشت، اسکریپت حداقل 5 GiB RAM قابل‌مشاهده در Docker را کنترل می‌کند؛ این حد یک تضمین عملکرد نیست. در اجرای موفق شما Docker مقدار 6.74 GiB گزارش کرد. روی مک 8 GB حین کار برنامه‌های سنگین را ببندید و Memory Pressure را کنترل کنید. هرگز هنگام اجرای کانتینر، Docker را برای تغییر منابع Restart نکنید. همهٔ مراحل پشت سر هم‌اند؛ نگاشت مطابق دستور استاد از thread پیش‌فرض استفاده می‌کند.

## محدودیت‌های علمی

- Reverse-stranded طبق تکلیف اعمال شده است. نرخ Assigned با این فرض سازگار است، ولی آزمون مستقل جهت‌مندی یا مقایسهٔ -s 0/1/2 انجام نشده؛ نتیجهٔ قطعی دربارهٔ پروتکل کتابخانه نمی‌دهیم.
- 1,851 خوانش پس از Trimming کوتاه‌تر از 20 باز است؛ چون استاد MINLEN تعیین نکرده، فیلتر جدید اضافه نشده است.
- FAIL ترکیب بازهای ابتدای خوانش می‌تواند با سوگیری آماده‌سازی کتابخانهٔ RNA-seq سازگار باشد؛ علت در این نمونه قطعی نیست.
- PASS آداپتور نبود کامل آداپتور را ثابت نمی‌کند. TRAILING حذف اختصاصی آداپتور نیست.
- Count خام، بیان نرمال‌شده نیست. یک نمونه و نبود تکرار/گروه کنترل برای تحلیل بیان افتراقی کافی نیست.
- درصد تکرار FastQC را با PCR duplication قطعی یا تکرارهای flagstat یکسان نگیرید؛ در این خط لوله duplicate marking انجام نشده است.
- BAM، FASTQ و مرجع بزرگ در محیط تهیهٔ PDF در دسترس نبودند؛ نتیجهٔ صحت آن‌ها بر اجرای واقعی شما و گزارش‌های ثبت‌شده تکیه دارد.

## فایل‌های ارائه

- `Presentation.pdf`: هشت صفحهٔ فارسی با نمودارهای واقعی و ده سؤال استاد.
- `Defense_Guide.md`: متن تمرین شفاهی، دستورهای مهم و سؤال‌های چالشی.
- `results/analysis_summary.json` و `top10_genes.tsv`: خلاصهٔ عددی قابل بررسی.
- `figures/`: نمودارهای PNG استخراج‌شده از دادهٔ واقعی.
- `tools/build_presentation.py`: کد بازتولید PDF؛ برای محیط Linux تهیه شده و به reportlab، matplotlib، arabic-reshaper، python-bidi و فونت‌های Noto Naskh Arabic و DejaVu نیاز دارد. اجرای تحلیل RNA-seq به این وابستگی‌ها احتیاج ندارد.

## منابع

- جزوهٔ استاد، صفحات 44 تا 51؛ سؤال‌ها در صفحهٔ 51.
- https://www.bioinformatics.babraham.ac.uk/projects/fastqc/
- https://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/3%20Analysis%20Modules/4%20Per%20Base%20Sequence%20Content.html
- https://daehwankimlab.github.io/hisat2/manual/
- https://daehwankimlab.github.io/hisat2/download/
- https://subread.sourceforge.net/featureCounts.html
- https://www.htslib.org/doc/samtools.html
