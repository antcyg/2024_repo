# read pdf table of content => title, page range (inclusive), image list

import pymupdf
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 2000)

def get_toc_pno(doc):
    return 0

def check_if_toc_title(span):
    font, size, color = span["font"], round(span["size"], 2), span["color"]
    return font == "Arial-BoldMT" and size == 11.04 and color == 0

#
# 1. Get Table of Content (TOC) from the pdf
#
doc = pymupdf.open("test_pdf1.pdf")
toc_pno = get_toc_pno(doc)
toc_page = doc.load_page(toc_pno)
blocks = toc_page.get_text("dict", flags=11)["blocks"]

title_list = []

for b in blocks:
    for l in b["lines"]:
        for s in l["spans"]:
            if check_if_toc_title(s):
                title_list.append(s["text"].strip())

title_list += ["MARKET CLOSINGS"]
start_page_list = []

title_list_idx = 0
for page in doc:
    if page.number <= 1:
        continue
    text_page = page.get_textpage()
    res_list = text_page.search(title_list[title_list_idx])
    if len(res_list) > 0:
        # print(f"Found {title_list[title_list_idx]} on page {page.number}")
        start_page_list.append(page.number)
        title_list_idx += 1
        if title_list_idx == len(title_list):
            break

df_toc = pd.DataFrame({
    "index": range(1, len(title_list)),
    "title": title_list[:-1],
    "start_page": start_page_list[:-1],
    "end_page": start_page_list[1:]})

print(df_toc)


#
# 2. Get Images for each article, save to disk
#

dict_images = {}

# get images for each article
for idx, row in df_toc.iterrows():
    start_page, end_page = row["start_page"], row["end_page"]
    article_index, article_title = row["index"], row["title"]

    for i in range(start_page, end_page):
        page = doc.load_page(i)
        img_list = page.get_image_info(xrefs=True)
        dict_images[article_index] = []
        for img_result in img_list:
            xref = img_result["xref"]
            bbox = img_result["bbox"]
            digest = img_result["digest"]
            img_obj = page.get_pixmap(clip=bbox)
            img_obj.save(f"img_{page}_{xref}.png")
            dict_images[article_index].append({
                "page": i,
                "xref": xref,
                "hash": digest,
            })

print(dict_images)