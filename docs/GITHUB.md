# قرار دادن پروژه در GitHub

در پوشهٔ نهایی پروژه اجرا کنید. اگر از قبل مخزن Git دارید، init و تغییر شاخه را تکرار نکنید و ابتدا `git status` را بررسی کنید.

```bash
git init -b main
git add .
git status --short
git diff --cached --stat
```

لیست باید کد، مستندات، PDF و نتایج کوچک را نشان دهد؛ FASTQ، SAM/BAM، JAR و مرجع نباید در آن باشند. برای کنترل قواعد:

```bash
git check-ignore data/demo.fastq data/demo.sam data/demo.sorted.bam reference/grch38/genome.1.ht2
```

اگر Git نام و ایمیل خواست، هویت خودتان را تنظیم کنید؛ از ایمیل noreply حساب GitHub هم می‌توانید استفاده کنید. سپس:

```bash
git commit -m "Add reproducible RNA-seq mini-project and results"
```

در GitHub یک repository خالی به نام `university-cs-topics-rnaseq-project` بسازید؛ گزینهٔ ساخت README، license و gitignore را فعال نکنید. آدرس واقعی HTTPS مخزن را از GitHub بردارید و به‌جای مقدار نمونه بگذارید:

```bash
git remote add origin https://github.com/YOUR_USERNAME/university-cs-topics-rnaseq-project.git
git push -u origin main
```

اگر origin از قبل وجود دارد، ابتدا `git remote -v` را ببینید؛ دوباره آن را اضافه نکنید. انتشار در GitHub در این بسته انجام نشده است.
