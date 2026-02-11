\# Image Quality Checker (Batch) / 图片质量检测工具（批量）



A tiny open-source Python tool to \*\*batch check image assets\*\* and export a report.



一个开源的 Python 小工具，用于\*\*批量检查图片素材\*\*并导出报告。



---



\## What it checks / 检测内容



\- \*\*Real file format\*\* by reading file signatures (magic bytes), not file extensions  

&nbsp; \*\*真实文件格式\*\*：读取文件头（魔数），不依赖扩展名

\- \*\*Resolution\*\* (width × height)  

&nbsp; \*\*分辨率\*\*（宽 × 高）

\- \*\*JPEG quality estimate\*\* (heuristic; derived from quantization tables)  

&nbsp; \*\*JPEG 压缩质量估算\*\*（经验值；基于量化表）

\- \*\*File size\*\*  

&nbsp; \*\*文件大小\*\*

\- \*\*Extension mismatch\*\* detection (e.g. `.png` that is actually JPEG)  

&nbsp; \*\*扩展名与真实格式不符\*\*检测（例如“假 PNG”）

\- Exports `quality\_report.txt` into the scanned folder  

&nbsp; 在扫描目录输出 `quality\_report.txt`



---



\## Supported formats / 支持格式



JPEG, PNG, WEBP, BMP, TIFF



---



\## Requirements / 环境要求



\- Python 3.8+

\- Dependency: Pillow



Install / 安装：

```bash

pip install -r requirements.txt

```



---



\## Usage / 使用方法



\### Option A: Run by double-click (Windows) / 双击运行（Windows）

1\. Copy `check\_image\_quality.py` into your image folder  

&nbsp;  把脚本复制到素材图片文件夹中

2\. Double-click to run  

&nbsp;  双击运行

3\. It will scan that folder and write `quality\_report.txt`  

&nbsp;  会扫描该文件夹并生成 `quality\_report.txt`



\### Option B: Command line (recommended) / 命令行（推荐）



Scan a folder / 扫描文件夹：

```bash

python check\_image\_quality.py /path/to/images

```



Scan a single file / 扫描单文件：

```bash

python check\_image\_quality.py /path/to/image.jpg

```



---



\## Output / 输出说明



\- Console output prints details per image (resolution, size, mode, extension, real format, etc.)  

&nbsp; 控制台逐张输出：分辨率、大小、颜色模式、扩展名、真实格式等

\- A summary section lists warnings (low resolution, low JPEG quality, format mismatch, etc.)  

&nbsp; 最后汇总警告：分辨率偏低、JPEG 质量偏低、格式不匹配等

\- Report file: `quality\_report.txt` (saved in the scanned folder)  

&nbsp; 报告文件：`quality\_report.txt`（保存在扫描目录）



---



\## Notes / 说明



\- JPEG “quality” is an estimate derived from quantization tables. It is \*\*not an exact encoder quality setting\*\*.  

&nbsp; JPEG“量”是根据量化表推断的区间值，\*\*不是编码器的精确 quality 参数\*\*。

\- Intended for quick screening of asset packs / stock images / mixed-format folders.  

&nbsp; 适合用于快速筛查素材包、图库图片、混合格式文件夹。



---



\## License



MIT

