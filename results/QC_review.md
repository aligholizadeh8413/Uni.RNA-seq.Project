# مرور کیفیت واقعی

| ماژول | قبل | بعد |
|---|---|---|
| Basic Statistics | PASS | PASS |
| Per base sequence quality | PASS | PASS |
| Per tile sequence quality | PASS | PASS |
| Per sequence quality scores | PASS | PASS |
| Per base sequence content | FAIL | FAIL |
| Per sequence GC content | PASS | PASS |
| Per base N content | PASS | PASS |
| Sequence Length Distribution | PASS | WARN |
| Sequence Duplication Levels | PASS | PASS |
| Overrepresented sequences | PASS | PASS |
| Adapter Content | PASS | PASS |

## تفسیر

- Per Base Sequence Quality: افت انتهای خوانش خام در میانگین و صدک دهم مشخص است؛ کیفیت بازهای باقی‌مانده در انتها پس از Trimming بالاتر است. مقایسهٔ موقعیت ۱۰۰ روی جمعیت یکسانی از خوانش‌ها نیست.
- Per Sequence Quality Scores: هر دو PASS؛ این وضعیت وجود خوانش‌های کم‌کیفیت را نفی نمی‌کند.
- Per Base Sequence Content: هر دو FAIL؛ ترکیب ابتدایی نامتوازن است. آماده‌سازی کتابخانه یکی از توضیح‌های احتمالی است، نه علت اثبات‌شده.
- Sequence Length Distribution: قبل همه ۱۰۰ باز؛ بعد ۲ تا ۱۰۰. WARN با طول‌های متفاوت و وجود خوانش‌های بسیار کوتاه سازگار است.
- Per Sequence GC Content: هر دو PASS؛ گزارش نسبت به الگوی مورد انتظار FastQC هشدار نمی‌دهد، ولی آلودگی را قطعی رد نمی‌کند.
- Sequence Duplication Levels: هر دو PASS. درصد deduplicated برآوردی از حدود ۷۹٫۰۱ به ۸۰٫۶۶ رسیده است؛ این معیار به‌تنهایی نرخ PCR duplicate نیست و هیچ deduplication در خط لوله اعمال نشده است.
- Overrepresented Sequences: هر دو PASS؛ توالی پرتکرار گزارش‌شده‌ای در ماژول دیده نمی‌شود. محدودیت تشخیص ابزار برقرار است.
- Adapter Content: هر دو PASS؛ مقدار صفر برای همهٔ آداپتورها فرض نمی‌شود. دستور اجراشده حذف اختصاصی آداپتور نیست.

منبع: فایل‌های fastqc_data.txt و summary.txt داخل ZIPهای FastQC موجود در evidence/reports.
