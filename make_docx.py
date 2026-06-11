from docx import Document
from docx.shared import Pt, Cm, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

doc = Document()

# ─── Page margins ───
for section in doc.sections:
    section.page_width  = Cm(21)
    section.page_height = Cm(29.7)
    section.top_margin    = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin   = Cm(3)
    section.right_margin  = Cm(2.5)

# ─── Colors and Styling ───
DARK_BLUE = RGBColor(0x1F, 0x38, 0x64)
MID_BLUE  = RGBColor(0x2E, 0x74, 0xB5)
WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
GREEN     = RGBColor(0x2E, 0x7D, 0x32)
GRAY      = RGBColor(0x40, 0x40, 0x40)

def set_cell_bg(cell, hex_color):
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd  = OxmlElement('w:shd')
    shd.set(qn('w:val'),   'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'),  hex_color)
    tcPr.append(shd)

def set_cell_border(cell):
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    for edge in ('top','left','bottom','right','insideH','insideV'):
        tag = OxmlElement(f'w:{edge}')
        tag.set(qn('w:val'),  'single')
        tag.set(qn('w:sz'),   '4')
        tag.set(qn('w:color'),'BFBFBF')
        tcBorders.append(tag)
    tcPr.append(tcBorders)

def heading1(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after  = Pt(6)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.bold      = True
    run.font.size = Pt(14)
    run.font.color.rgb = DARK_BLUE
    
    # bottom border line under H1
    pPr  = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'),   'single')
    bottom.set(qn('w:sz'),    '6')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), '1F3864')
    pBdr.append(bottom)
    pPr.append(pBdr)
    return p

def heading2(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after  = Pt(4)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.bold      = True
    run.font.size = Pt(12)
    run.font.color.rgb = MID_BLUE
    return p

def heading3(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after  = Pt(2)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.bold      = True
    run.underline = True
    run.font.size = Pt(11)
    run.font.color.rgb = GRAY
    return p

def body(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.alignment   = WD_ALIGN_PARAGRAPH.JUSTIFY
    run = p.add_run(text)
    run.font.size = Pt(11)
    return p

def bullet(text):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(3)
    run = p.add_run(text)
    run.font.size = Pt(11)
    return p

def add_table(headers, rows, header_bg='1F3864'):
    tbl = doc.add_table(rows=1+len(rows), cols=len(headers))
    tbl.style = 'Table Grid'
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Header row
    hdr_row = tbl.rows[0]
    for i, h in enumerate(headers):
        cell = hdr_row.cells[i]
        cell.text = h
        run = cell.paragraphs[0].runs[0]
        run.bold = True
        run.font.color.rgb = WHITE
        run.font.size = Pt(10.5)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_bg(cell, header_bg)

    # Data rows
    for r_idx, row_data in enumerate(rows):
        row = tbl.rows[r_idx+1]
        for c_idx, val in enumerate(row_data):
            cell = row.cells[c_idx]
            cell.text = val
            if cell.paragraphs[0].runs:
                cell.paragraphs[0].runs[0].font.size = Pt(10.5)
            set_cell_border(cell)
            if r_idx % 2 == 1:
                set_cell_bg(cell, 'F5F8FF')

    doc.add_paragraph()
    return tbl

def add_info_box(title, content, bg='EEF3FF', border_color='1F3864'):
    """Info card box with left thick border"""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.style = 'Table Grid'
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.rows[0].cells[0]
    set_cell_bg(cell, bg)
    
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    
    for edge in ('top', 'bottom', 'right'):
        tag = OxmlElement(f'w:{edge}')
        tag.set(qn('w:val'), 'none')
        tcBorders.append(tag)
        
    left = OxmlElement('w:left')
    left.set(qn('w:val'), 'single')
    left.set(qn('w:sz'), '24') # 3pt
    left.set(qn('w:color'), border_color)
    tcBorders.append(left)
    tcPr.append(tcBorders)
    
    p = cell.paragraphs[0]
    if title:
        r = p.add_run(f"📌 {title}\n")
        r.bold = True
        r.font.size = Pt(11)
        r.font.color.rgb = DARK_BLUE
        
    for i, line in enumerate(content):
        if i > 0 or title:
            p = cell.add_paragraph()
        p.paragraph_format.left_indent = Cm(0.3)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(line)
        r.font.size = Pt(10.5)
        
    doc.add_paragraph()

def add_code_block(code_text):
    """Monospaced block with shading and left border"""
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.5)
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    
    run = p.add_run(code_text)
    run.font.name = 'Courier New'
    run.font.size = Pt(9.5)
    run.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), 'F4F4F4')
    pPr.append(shd)
    
    pBdr = OxmlElement('w:pBdr')
    left = OxmlElement('w:left')
    left.set(qn('w:val'), 'single')
    left.set(qn('w:sz'), '24')
    left.set(qn('w:color'), '1F3864')
    pBdr.append(left)
    pPr.append(pBdr)
    return p

def page_break():
    doc.add_page_break()

# ═══════════════════════════════════════════════════
#  KAPAK SAYFASI
# ═══════════════════════════════════════════════════
doc.add_paragraph()
doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("🕌")
r.font.size = Pt(48)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("BİLGİSAYAR MÜHENDİSLİĞİ BÖLÜMÜ")
r.bold = True; r.font.size = Pt(14); r.font.color.rgb = DARK_BLUE

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Web Programlama Dersi\nFinal Dönemi Proje Çalışması")
r.font.size = Pt(11); r.font.color.rgb = GRAY

doc.add_paragraph()
doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("FİNAL PROJE RAPORU DOKÜMANI")
r.bold = True; r.font.size = Pt(12); r.font.color.rgb = MID_BLUE

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("KUR'AN KERİM HATİM TAKİP\nWEB UYGULAMASI")
r.bold = True; r.font.size = Pt(22); r.font.color.rgb = DARK_BLUE

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Full-Stack Web Geliştirme — React.js + Node.js + SQLite")
r.font.size = Pt(12); r.font.color.rgb = GRAY

doc.add_paragraph()
doc.add_paragraph()

info_tbl = doc.add_table(rows=5, cols=2)
info_tbl.style = 'Table Grid'
info_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
labels = ["Öğrenci Adı", "Öğrenci No", "Ders Adı", "Danışman Hoca", "Teslim Tarihi"]
values = ["Mohamed Ayman", "MOHAMEDAYMEN12", "Web Programlama", "", "7 Haziran 2026"]
for i, (lbl, val) in enumerate(zip(labels, values)):
    row = info_tbl.rows[i]
    row.cells[0].text = lbl
    row.cells[0].paragraphs[0].runs[0].bold = True
    row.cells[0].paragraphs[0].runs[0].font.size = Pt(11)
    set_cell_bg(row.cells[0], 'DBE5F1')
    row.cells[1].text = val
    if row.cells[1].paragraphs[0].runs:
        row.cells[1].paragraphs[0].runs[0].font.size = Pt(11)
    set_cell_border(row.cells[0])
    set_cell_border(row.cells[1])

doc.add_paragraph()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Ankara, Türkiye — Haziran 2026")
r.font.size = Pt(11); r.font.color.rgb = GRAY

page_break()

# ═══════════════════════════════════════════════════
#  İÇİNDEKİLER
# ═══════════════════════════════════════════════════
heading1("İÇİNDEKİLER")
toc_items = [
    ("1.", "Proje Özeti ve Amacı"),
    ("2.", "Proje Hedefleri ve Gereksinimler"),
    ("3.", "Geliştirme Zaman Çizelgesi (Timeline)"),
    ("4.", "Kullanılan Teknolojiler"),
    ("5.", "Sistem Mimarisi"),
    ("6.", "Veritabanı Tasarımı"),
    ("7.", "Backend Geliştirme (Node.js & Express)"),
    ("8.", "Frontend Geliştirme (React.js)"),
    ("9.", "Karşılaşılan Sorunlar ve Çözümleri"),
    ("10.", "Uygulama Ekran Görüntüleri Açıklaması"),
    ("11.", "Sonuç ve Değerlendirme"),
    ("12.", "Kaynakça"),
]
for num, title in toc_items:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(f"{num}  {title}")
    r.font.size = Pt(11.5)
    r.bold = True
    r.font.color.rgb = DARK_BLUE

page_break()

# ═══════════════════════════════════════════════════
#  BÖLÜM 1: ÖZET VE AMAÇ
# ═══════════════════════════════════════════════════
heading1("1. Proje Özeti ve Amacı")
body("Bu proje, Müslümanların Kur'an-ı Kerim okuma ve hatim süreçlerini dijitalleştirmek ve kolaylaştırmak amacıyla geliştirilmiştir. Kullanıcılar sisteme üye olarak kendi bireysel hatimlerini takip edebildikleri gibi, modern bir işbirlikçi araç olan Grup Hatmi (Collective/Group Khatma) özelliğini kullanarak diğer insanlarla ortak hatimler tamamlayabilirler.")

body("Projenin Temel Amacı: Bireysel okuma alışkanlıklarını düzenli hale getirmek, cüzlerin kimler tarafından okunduğunu şeffaf bir şekilde yönetmek ve fiziksel olarak koordine edilmesi zor olan toplu Kur'an hatimlerini tamamen web üzerinden yönetilebilir hale getirmektir. Ayrıca, kullanıcıların gizliliğini korumak adına 'Grup Hatmi' katılımlarında gerçek adını gizleyerek 'Anonymous' (Gizli Katılımcı) olarak cüz rezerve edebilmesini sağlar.")

add_info_box(
    "Proje Özellikleri",
    [
        "• Kullanıcı kaydı ve oturum yönetimi (JWT tabanlı kimlik doğrulama)",
        "• Bireysel hatim takibi (sure ve ayet bazlı ilerleme, 6236 ayet üzerinden)",
        "• Grup Hatmi başlatma (Ramazan Hatmi, Aile Hatmi vb. başlıklarla)",
        "• 30 Cüzün farklı kullanıcılar tarafından kilitlenerek rezerve edilmesi",
        "• Gizli Katılımcı (Anonymous) modu ile kimlik korumalı cüz tamamlama",
        "• Her katılımcı için sadece kendi rezerve ettiği cüzler üzerinden ilerleme hesabı",
        "• Tüm cüzler bittiğinde grup hatmi durumunun otomatik 'Tamamlandı' olarak güncellenmesi",
        "• Özel Cüz Okuyucu (JuzReader) ile doğrudan hedeflenen cüze geçiş"
    ],
    'EEF3FF',
    '1F3864'
)

# ═══════════════════════════════════════════════════
#  BÖLÜM 2: HEDEFLER VE GEREKSİNİMLER
# ═══════════════════════════════════════════════════
heading1("2. Proje Hedefleri ve Gereksinimler")

heading2("2.1 Fonksiyonel Gereksinimler")
add_table(
    ["No", "Gereksinim", "Öncelik", "Durum"],
    [
        ["F-01", "Kullanıcı kaydı (Ad, E-posta, Şifre)", "Yüksek", "✓ Tamamlandı"],
        ["F-02", "Kullanıcı girişi ve JWT token yönetimi", "Yüksek", "✓ Tamamlandı"],
        ["F-03", "Kişisel hatim başlatma", "Yüksek", "✓ Tamamlandı"],
        ["F-04", "Başkası adına hatim açma", "Orta", "✓ Tamamlandı"],
        ["F-05", "Sure/Ayet seçimi ile ilerleme güncelleme", "Yüksek", "✓ Tamamlandı"],
        ["F-06", "Bireysel Kur'an okuma sayfası", "Yüksek", "✓ Tamamlandı"],
        ["F-07", "Ayete tıklayarak ilerleme kaydetme", "Yüksek", "✓ Tamamlandı"],
        ["F-08", "Türkçe / Arapça dil değiştirme ve RTL desteği", "Orta", "✓ Tamamlandı"],
        ["F-09", "Grup Hatmi oluşturma ve listeleme", "Yüksek", "✓ Tamamlandı"],
        ["F-10", "Cüz rezervasyon kilitleme ve çakışma önleme", "Yüksek", "✓ Tamamlandı"],
        ["F-11", "Gizli Katılım (Anonim rezervasyon) desteği", "Orta", "✓ Tamamlandı"],
        ["F-12", "Cüz okuma (JuzReader) ve cüz bazlı tamamlama", "Yüksek", "✓ Tamamlandı"]
    ]
)

heading2("2.2 Teknik Gereksinimler")
bullet("Ayrı bir frontend ve backend sunucu mimarisi (Ayrık katmanlı mimari)")
bullet("REST API ile frontend-backend iletişimi")
bullet("Güvenli şifreleme ve token tabanlı kimlik doğrulama")
bullet("Harici API entegrasyonu (api.alquran.cloud) Kur'an verileri için")
bullet("Kalıcı veri depolama (SQLite veritabanı)")
bullet("Duyarlı (Responsive) tasarım")

page_break()

# ═══════════════════════════════════════════════════
#  BÖLÜM 3: GELİŞTİRME ZAMAN ÇİZGELGESİ
# ═══════════════════════════════════════════════════
heading1("3. Geliştirme Zaman Çizelgesi (Timeline)")
body("Projenin planlanması, veritabanının tasarlanması, kodlanması ve test edilmesine ilişkin haftalık süreç çizelgesi aşağıda belirtilmiştir:")

add_table(
    ["Tarih / Hafta", "Yapılan Çalışmalar", "Kullanılan Araçlar"],
    [
        ["1-2. Hafta\n(15-28 Şubat 2026)", "• Gereksinim analizi yapıldı.\n• Figma üzerinde arayüz taslakları oluşturuldu.\n• Proje dizini yapılandırıldı, Git başlatıldı.", "Figma, Git, VS Code"],
        ["3-4. Hafta\n(1-15 Mart 2026)", "• Node.js + Express sunucusu yapılandırıldı.\n• SQLite veritabanı kuruldu, users ve khatms tabloları oluşturuldu.\n• bcrypt ve JWT ile kimlik doğrulama API'leri yazıldı.", "Express, SQLite, JWT, bcrypt"],
        ["5-6. Hafta\n(16-31 Mart 2026)", "• React.js arayüzü kuruldu, Context API ile global Auth Context yazıldı.\n• react-i18next entegre edilerek Türkçe-Arapça anlık geçiş ve RTL yönlendirmeleri eklendi.", "React, i18next, CSS"],
        ["7-8. Hafta\n(1-19 Nisan 2026)", "• QuranReader geliştirildi ve api.alquran.cloud entegre edildi.\n• Ayet tıklama durak kaydı ve onay penceresi yazıldı.\n• Vize Proje Raporu hazırlandı ve teslim edildi.", "Axios, REST API, Word/HTML"],
        ["9-10. Hafta\n(20 Nis - 10 May 2026)", "• Grup Hatmi (Collective Khatma) tasarım planı çizildi.\n• Veritabanı şeması genişletilerek group_khatms ve group_khatm_reservations tabloları eklendi.\n• Grup oluşturma ve cüz kilitleme/rezervasyon API'leri backend tarafında geliştirildi.", "SQLite, REST APIs, Postman"],
        ["11-12. Hafta\n(11-25 Mayıs 2026)", "• Frontend tarafında GroupDashboard ve GroupKhatmaDetails arayüzleri tasarlandı.\n• 30 Cüz için etkileşimli cüz seçim paneli ve anonim seçeneği yerleştirildi.\n• JuzReader.jsx yazıldı; cüze özel okuma ve bismillah/sure gruplama mantığı entegre edildi.", "React, Axios, Amiri Font"],
        ["13. Hafta (Son)\n(26 May - 7 Haz 2026)", "• Güvenlik güncellemesi yapıldı: Token süresi dolduğunda (401/403) otomatik güvenli çıkış (interceptor) yazıldı.\n• Proje son kez test edildi ve GitHub'a yüklendi.\n• Final Proje Raporu ve sunum belgelemesi tamamlandı.", "GitHub, Git, Node.js"]
    ]
)

page_break()

# ═══════════════════════════════════════════════════
#  BÖLÜM 4: TEKNOLOJİLER
# ═══════════════════════════════════════════════════
heading1("4. Kullanılan Teknolojiler")

heading2("4.1 Frontend Teknolojileri")
add_table(
    ["Teknoloji", "Versiyon", "Kullanım Amacı"],
    [
        ["React.js", "^19.x", "Kullanıcı arayüzü bileşenleri"],
        ["Vite", "^8.x", "Hızlı geliştirme sunucusu ve paketleme"],
        ["React Router DOM", "^7.x", "Sayfa yönlendirme (SPA routing)"],
        ["Axios", "^1.x", "HTTP istekleri (API çağrıları)"],
        ["i18next + react-i18next", "^24.x", "Çok dilli destek (TR / AR)"],
        ["Vanilla CSS", "-", "Özel stil tasarımı (karanlık tema)"],
        ["Google Fonts (Amiri)", "-", "Arap hattı yazı tipi"],
        ["Alquran Cloud API", "v1", "Kur'an metni verisi (Osmanlı hattı)"]
    ]
)

heading2("4.2 Backend Teknolojileri")
add_table(
    ["Teknoloji", "Versiyon", "Kullanım Amacı"],
    [
        ["Node.js", "^22.x", "Sunucu taraflı JavaScript çalışma ortamı"],
        ["Express.js", "^5.x", "HTTP sunucusu ve API routing"],
        ["SQLite3", "^6.x", "Hafif ilişkisel veritabanı"],
        ["bcrypt", "^6.x", "Güvenli şifre şifreleme (hashing)"],
        ["jsonwebtoken (JWT)", "^9.x", "Kimlik doğrulama token'ları"],
        ["cors", "^2.x", "Cross-Origin kaynak paylaşımı"],
        ["dotenv", "^17.x", "Ortam değişkenleri yönetimi"],
        ["nodemon", "^3.x", "Otomatik sunucu yeniden başlatma"]
    ]
)

heading2("4.3 Geliştirme Araçları")
bullet("Visual Studio Code (Kod editörü)")
bullet("npm (Paket yönetimi)")
bullet("Git (Versiyon kontrolü)")
bullet("Windows PowerShell (Terminal komutları)")

page_break()

# ═══════════════════════════════════════════════════
#  BÖLÜM 5: MİMARİ
# ═══════════════════════════════════════════════════
heading1("5. Sistem Mimarisi")

heading2("5.1 Genel Mimari")
body("Uygulama, İstemci-Sunucu (Client-Server) mimarisi üzerine inşa edilmiştir. Frontend ve Backend birbirinden tamamen bağımsız olup aralarındaki iletişim REST API aracılığıyla gerçekleşmektedir.")

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("React (Port 5173)   ⇄   REST API   ⇄   Express.js (Port 5000)   ⇄   SQLite DB")
r.bold = True; r.font.color.rgb = DARK_BLUE; r.font.size = Pt(11)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("api.alquran.cloud API   →   Kur'an Okuyucu (React)")
r.bold = True; r.font.color.rgb = GREEN; r.font.size = Pt(11)

doc.add_paragraph()

heading2("5.2 Proje Dizin Yapısı")
file_tree_text = """uyglama22/
├── backend/
│   ├── server.js          → Ana Express sunucusu & API endpoint'leri
│   ├── db.js              → SQLite bağlantısı & tablo oluşturma
│   ├── .env               → Ortam değişkenleri (PORT, JWT_SECRET)
│   ├── database.sqlite    → Veritabanı dosyası
│   └── package.json       → Node.js bağımlılıkları
│
└── frontend/
    ├── src/
    │   ├── App.jsx         → Ana uygulama (Auth, Dashboard, GroupDashboard, GroupKhatmaDetails)
    │   ├── QuranReader.jsx → Bireysel Kur'an okuyucu sayfası
    │   ├── JuzReader.jsx   → Grup cüz okuyucu sayfası
    │   ├── surahData.js    → 114 sure verisi & ayet indeks yardımcıları
    │   ├── i18n.js         → Türkçe/Arapça çeviri dosyası
    │   ├── index.css       → Global stiller (karanlık tema)
    │   └── main.jsx        → React giriş noktası
    └── package.json        → React bağımlılıkları"""
add_code_block(file_tree_text)

heading2("5.3 Kimlik Doğrulama Akışı")
bullet("Kullanıcı Kaydı: Ad + E-posta + Şifre → bcrypt ile şifrelenir → SQLite veritabanına kaydedilir.")
bullet("Giriş Yapma: E-posta + Şifre → bcrypt.compare karşılaştırması → JWT token oluşturulur ve istemciye gönderilir.")
bullet("API İstekleri: İsteklerin başlığında (Header) 'Authorization: Bearer <token>' gönderilir → Backend doğrular → Sonuç döner.")
bullet("Çıkış Yapma: LocalStorage temizlenir → Token silinir → İstemci otomatik çıkış yaparak ana sayfaya yönlendirilir.")

page_break()

# ═══════════════════════════════════════════════════
#  BÖLÜM 6: VERİTABANI
# ═══════════════════════════════════════════════════
heading1("6. Veritabanı Tasarımı")
body("Veritabanı olarak kurulum gerektirmeyen, dosya tabanlı SQLite veritabanı kullanılmıştır. Projede ilişkisel yapıda çalışan 4 ana tablo yer almaktadır.")

heading2("6.1 users Tablosu")
add_table(
    ["Sütun", "Tür", "Açıklama"],
    [
        ["id", "INTEGER (PK, AUTO)", "Kullanıcı benzersiz numarası"],
        ["name", "TEXT NOT NULL", "Kullanıcının adı ve soyadı"],
        ["email", "TEXT UNIQUE NOT NULL", "E-posta adresi (giriş için, benzersiz)"],
        ["password", "TEXT NOT NULL", "bcrypt ile hashlenmiş şifre"]
    ]
)

heading2("6.2 khatms Tablosu (Bireysel)")
add_table(
    ["Sütun", "Tür", "Açıklama"],
    [
        ["id", "INTEGER (PK, AUTO)", "Hatim benzersiz numarası"],
        ["title", "TEXT NOT NULL", "Hatim başlığı"],
        ["owner_id", "INTEGER (FK → users.id)", "Hatimi oluşturan kullanıcı kimliği"],
        ["target_person", "TEXT", "Hatim adanan kişi (opsiyonel)"],
        ["last_ayah", "INTEGER DEFAULT 0", "Son okunan ayetin global numarası (1 - 6236)"],
        ["total_ayahs", "INTEGER DEFAULT 6236", "Toplam ayet sayısı (6236)"],
        ["type", "TEXT DEFAULT 'self'", "Bireysel ('self') veya Başkası Adına ('other')"]
    ]
)

heading2("6.3 group_khatms Tablosu (Ortak Hatim)")
add_table(
    ["Sütun", "Tür", "Açıklama"],
    [
        ["id", "INTEGER (PK, AUTO)", "Grup hatmi benzersiz kimliği"],
        ["title", "TEXT NOT NULL", "Grup hatmi başlığı (Örn: Ramazan Hatmi)"],
        ["creator_id", "INTEGER (FK → users.id)", "Grubu oluşturan kullanıcı kimliği"],
        ["status", "TEXT DEFAULT 'open'", "Durum: 'open' (açık), 'fully_reserved' (dolu), 'completed' (bitti)"],
        ["created_at", "DATETIME", "Oluşturulma zamanı"],
        ["updated_at", "DATETIME", "Son güncellenme zamanı"]
    ]
)

heading2("6.4 group_khatm_reservations Tablosu (Cüz Rezervasyon)")
add_table(
    ["Sütun", "Tür", "Açıklama"],
    [
        ["id", "INTEGER (PK, AUTO)", "Rezervasyon benzersiz kimliği"],
        ["group_khatma_id", "INTEGER (FK)", "Grup hatmi referansı"],
        ["juz_number", "INTEGER NOT NULL", "Rezerve edilen cüz numarası (1-30)"],
        ["user_id", "INTEGER (FK → users.id)", "Rezerve eden kullanıcı referansı"],
        ["display_name", "TEXT NOT NULL", "Kullanıcı adı veya 'Anonymous'"],
        ["is_anonymous", "INTEGER DEFAULT 0", "Gizli katılımcı bayrağı (0 veya 1)"],
        ["status", "TEXT DEFAULT 'reserved'", "Cüz durumu: 'reserved' (okunuyor), 'completed' (okundu)"],
        ["completed_at", "DATETIME", "Cüzün bittiği tarih/saat"],
        ["created_at", "DATETIME", "Rezervasyon tarih/saat"]
    ]
)

add_info_box(
    "Veritabanı Benzersizlik Kısıtı (UNIQUE Constraint)",
    [
        "Aynı grup hatminde aynı cüzün iki farklı kişi tarafından aynı anda kilitlenip okunmasını önlemek amacıyla group_khatm_reservations tablosuna UNIQUE (group_khatma_id, juz_number) kısıtı eklenmiştir. Bu kısıt, çakışmaları veritabanı düzeyinde mutlak suretle engeller."
    ],
    'FFF8E1',
    'FFE082'
)

page_break()

# ═══════════════════════════════════════════════════
#  BÖLÜM 7: BACKEND
# ═══════════════════════════════════════════════════
heading1("7. Backend Geliştirme (Node.js & Express)")

heading2("7.1 API Endpoint'leri")
add_table(
    ["Method", "Endpoint", "Açıklama", "Kimlik Doğrulama"],
    [
        ["POST", "/api/auth/register", "Yeni kullanıcı kaydı", "Hayır"],
        ["POST", "/api/auth/login", "Kullanıcı girişi → JWT Token", "Hayır"],
        ["GET", "/api/khatms", "Kullanıcının tüm bireysel hatimleri", "✓ JWT"],
        ["POST", "/api/khatms", "Yeni bireysel hatim oluşturma", "✓ JWT"],
        ["PUT", "/api/khatms/:id", "Bireysel hatim ilerlemesini güncelleme", "✓ JWT"],
        ["POST", "/api/group-khatms", "Yeni ortak grup hatmi oluşturma", "✓ JWT"],
        ["GET", "/api/group-khatms", "Tüm grup hatimlerini listeleme", "✓ JWT"],
        ["GET", "/api/group-khatms/:id", "Grup hatmi detayları (30 cüzün durumları)", "✓ JWT"],
        ["POST", "/api/group-khatms/:id/reserve", "Seçili cüzleri rezerve etme (kilitleme)", "✓ JWT"],
        ["PUT", "/api/group-khatms/:id/complete", "Rezerve edilmiş cüzü okundu olarak işaretleme", "✓ JWT"]
    ]
)

heading2("7.2 Kimlik Doğrulama Middleware (authenticate)")
body("Yetki gerektiren her API çağrısı, istemcinin gönderdiği Authorization başlığındaki Bearer token'ı doğrulayan bir middleware kontrolünden geçer:")
auth_code = """const authenticate = (req, res, next) => {
  const token = req.headers['authorization'];
  if (!token) return res.status(401).json({ error: 'Unauthorized' });

  jwt.verify(token.split(' ')[1], SECRET, (err, decoded) => {
    if (err) return res.status(403).json({ error: 'Forbidden' });
    req.userId = decoded.id;
    next();
  });
};"""
add_code_block(auth_code)

heading2("7.3 Cüz Rezervasyonunda İş Mantığı (Business Logic)")
body("Cüz rezervasyonu yapılırken seçilen cüzlerin başka bir kullanıcı tarafından rezerve edilip edilmediği backend seviyesinde denetlenir ve 30 cüzün tamamı kilitlendiğinde grup hatmi durumu 'fully_reserved' yapılır:")
reserve_code = """// Cüz Rezervasyon Endpoint (POST /api/group-khatms/:id/reserve)
app.post('/api/group-khatms/:id/reserve', authenticate, (req, res) => {
  const khatmaId = req.params.id;
  const { juzNumbers, isAnonymous } = req.body;

  // Çakışan rezervasyonları kontrol et
  const placeholders = juzNumbers.map(() => '?').join(',');
  const checkSql = `SELECT juz_number FROM group_khatm_reservations 
                    WHERE group_khatma_id = ? AND juz_number IN (${placeholders})`;
  
  db.all(checkSql, [khatmaId, ...juzNumbers], (err, rows) => {
    if (rows.length > 0) {
      const alreadyReserved = rows.map(r => r.juz_number).join(', ');
      return res.status(400).json({ error: `Cüz ${alreadyReserved} zaten rezerve edilmiş.` });
    }

    db.get(`SELECT name FROM users WHERE id = ?`, [req.userId], (err, user) => {
      const displayName = isAnonymous ? 'Anonymous' : user.name;
      db.serialize(() => {
        const insertSql = `INSERT INTO group_khatm_reservations 
                           (group_khatma_id, juz_number, user_id, display_name, is_anonymous) 
                           VALUES (?, ?, ?, ?, ?)`;
        const stmt = db.prepare(insertSql);
        juzNumbers.forEach(juz => {
          stmt.run([khatmaId, juz, req.userId, displayName, isAnonymous ? 1 : 0]);
        });
        stmt.finalize(() => {
          // 30 cüzün tamamı doldu mu kontrolü
          db.get(`SELECT COUNT(*) as count FROM group_khatm_reservations 
                  WHERE group_khatma_id = ?`, [khatmaId], (err, row) => {
            if (row && row.count === 30) {
              db.run(`UPDATE group_khatms SET status = 'fully_reserved', updated_at = CURRENT_TIMESTAMP WHERE id = ?`, [khatmaId]);
            }
            res.json({ message: 'Rezervasyon başarılı!' });
          });
        });
      });
    });
  });
});"""
add_code_block(reserve_code)

page_break()

# ═══════════════════════════════════════════════════
#  BÖLÜM 8: FRONTEND
# ═══════════════════════════════════════════════════
heading1("8. Frontend Geliştirme (React.js)")

heading2("8.1 Bileşen (Component) Yapısı")
add_table(
    ["Bileşen", "Dosya", "Görev"],
    [
        ["Dashboard", "App.jsx", "Bireysel hatimlerin listesi ve hatim oluşturma arayüzü"],
        ["GroupDashboard", "App.jsx", "Ortak hatimlerin listesi ve yeni grup hatmi oluşturma formu"],
        ["GroupKhatmaDetails", "App.jsx", "30 cüzün durum paneli, katılımcı istatistikleri ve cüz rezervasyon alanı"],
        ["JuzReader", "JuzReader.jsx", "Seçili cüzün (1-30) ayetlerini api.alquran.cloud'dan çeken ve sunan özel arayüz"],
        ["QuranReader", "QuranReader.jsx", "Bireysel hatim için sure-ayet bazlı Kur'an okuma ekranı"],
        ["Navbar", "App.jsx", "Kullanıcı bilgisi, Çıkış butonu ve TR/AR dil değiştirme menüsü"]
    ]
)

heading2("8.2 Sayfa Yönlendirme (Routing)")
add_table(
    ["Rota (Route)", "Bileşen", "Açıklama"],
    [
        ["/", "Dashboard", "Bireysel hatim yönetim paneli (Giriş zorunlu)"],
        ["/group-khatms", "GroupDashboard", "Grup hatimleri listesi paneli (Giriş zorunlu)"],
        ["/group-khatms/:id", "GroupKhatmaDetails", "Grup hatmi detay ve cüz yönetim ekranı"],
        ["/read/:khatmId", "QuranReader", "Bireysel hatim okuma ve ayet işaretleme ekranı"],
        ["/read-juz/:juzNum", "JuzReader", "Grup hatminden rezerve edilen cüzü okuma ekranı"],
        ["/login", "Login", "Kullanıcı giriş sayfası"],
        ["/register", "Register", "Yeni kayıt sayfası"]
    ]
)

heading2("8.3 Axios Oturum İstek Interceptor'ı")
body("İstemci tarafında JWT token'ın süresi dolduğunda (24 saat sonra) API isteklerinden dönecek olan 401/403 yetkisiz hatası durumunda kullanıcının arayüzde kilitlenmesini engellemek için Axios interceptor mekanizması geliştirilmiştir:")
interceptor_code = """useEffect(() => {
  const interceptor = axios.interceptors.response.use(
    (response) => response,
    (error) => {
      // Yetkisiz istekte otomatik çıkış yap ve local storage'ı temizle
      if (error.response && (error.response.status === 401 || error.response.status === 403)) {
        logout();
      }
      return Promise.reject(error);
    }
  );
  return () => {
    axios.interceptors.response.eject(interceptor);
  };
}, []);"""
add_code_block(interceptor_code)

page_break()

# ═══════════════════════════════════════════════════
#  BÖLÜM 9: SORUNLAR VE ÇÖZÜMLER
# ═══════════════════════════════════════════════════
heading1("9. Karşılaşılan Sorunlar ve Çözümleri")

heading2("Sorun 1: Frontend-Backend CORS Engeli")
body("React uygulaması (localhost:5173) Node.js sunucusuna (localhost:5000) istek gönderdiğinde tarayıcı CORS politikası hatası veriyordu. Çözüm olarak backend sunucusuna cors npm paketi entegre edilerek tüm kaynaklardan gelen isteklere izin verildi.")

heading2("Sorun 2: SQLite Modülü Windows Kurulum Hatası")
body("Windows üzerinde sqlite3 paketi kurulurken Native C++ binding derleme hatası oluştu. Çözüm olarak Node.js'in LTS sürümüne geçildi ve sqlite3 paketinin önceden derlenmiş (prebuilt binary) sürümlerinin indirilmesi sağlandı.")

heading2("Sorun 3: React useNavigate import Sırası Hatası")
body("App.jsx dosyasında useNavigate hook'u dosyanın ortalarında, JSX kodlarının hemen üstünde import edilmeye çalışıldığında Vite derleme hatası verdi. Çözüm olarak tüm import kodları dosyanın en üst satırlarına taşındı.")

heading2("Sorun 4: Giriş Başarısız - 'Invalid credentials'")
body("Yeni oluşturulan veritabanı dosyasında hiçbir kayıt bulunmadığı için kullanıcılar giriş yapamıyordu. Çözüm olarak giriş formuna 'Kaydol' bağlantısı eklendi ve veritabanına veri yazma başarılı olduktan sonra giriş mekanizması çalıştırıldı.")

heading2("Sorun 5: Kur'an API Entegrasyonu ve Performans")
body("Tüm 6236 ayetin arayüze gömülmesi bundle boyutunu 5MB'ın üzerine çıkarıyordu. Çözüm olarak harici Alquran Cloud API entegre edilerek lazy loading (seçilen sureye göre anlık veri çekme) yapısı kurgulandı.")

heading2("Sorun 6: Grup Hatimlerinde Eşzamanlı Cüz Rezervasyon Çakışmaları")
body("Birden fazla kullanıcının aynı anda aynı cüzü rezerve etmek için butona basması halinde SQLite dosyasında çakışmalar oluyordu. Çözüm olarak group_khatm_reservations tablosuna UNIQUE (group_khatma_id, juz_number) kısıtı eklendi ve backend'de rezervasyon öncesi SELECT denetimleri entegre edildi.")

page_break()

# ═══════════════════════════════════════════════════
#  BÖLÜM 10: EKRAN GÖRÜNTÜLERİ
# ═══════════════════════════════════════════════════
heading1("10. Uygulama Ekran Görüntüleri Açıklaması")

heading2("10.1 Kullanıcı Akış Şeması")
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Kayıt Ol  →  Giriş Yap  →  Ana Panel  →  Grup Hatmi  →  Cüz Rezerve Et  →  JuzReader Oku  →  Cüzü Tamamla")
r.bold = True; r.font.color.rgb = DARK_BLUE; r.font.size = Pt(10)

heading2("10.2 Arayüz Görselleri ve Tasarım Detayları")

body("Uygulama, modern koyu renk şemasına (dark mode) sahip bir kullanıcı arayüzü sunar. Aşağıda, kullanıcıları karşılayan giriş ekranı yer almaktadır:")

# Insert Hero Screenshot
base_path = os.path.dirname(os.path.abspath(__file__))
hero_path = os.path.join(base_path, "frontend", "src", "assets", "hero.png")
if os.path.exists(hero_path):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run()
    r.add_picture(hero_path, width=Cm(14))
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(8)
    r = p.add_run("Şekil 1: Kur'an Hatim Takip Uygulaması - Karşılama Ekranı")
    r.font.size = Pt(10)
    r.font.color.rgb = GRAY
else:
    body("[Giriş Ekranı Görseli: frontend/src/assets/hero.png bulunamadı]")

body("Giriş yapıldıktan sonra erişilen Ana Panel (Dashboard) ise bireysel hatimlerin ve genel uygulama kontrollerinin bulunduğu ana merkezdir. Aşağıda, projenin en önemli görsel çıktısı olan aktif ana panel arayüzü sunulmuştur:")

# Insert Dashboard Screenshot
dashboard_path = os.path.join(base_path, "frontend", "src", "assets", "dashboard.png")
if os.path.exists(dashboard_path):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run()
    r.add_picture(dashboard_path, width=Cm(15.5))
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(8)
    r = p.add_run("Şekil 2: Kur'an Hatim Takip Uygulaması - Ana Kontrol Paneli (Dashboard)")
    r.font.size = Pt(10)
    r.font.color.rgb = GRAY
else:
    body("[Ana Panel Görseli: frontend/src/assets/dashboard.png bulunamadı]")

heading3("Görsel Analiz ve Bileşen Yapıları:")
bullet("Bireysel Hatim Takip Kartları: Dahil olunan hatimlerin (Kişisel Hatim, Aile Hatmi vb.) tamamlanma durumları mavi ve yeşil renkli ilerleme çubukları ile görselleştirilir.")
bullet("Son Okunan Durak Noktası: Kartların üzerinde kullanıcının en son okuduğu sure ve ayet numarası (Örn: Al-Baqara 100) yer alır.")
bullet("Hızlı İlerleme Menüleri: Kullanıcı okuma ekranına gitmeden de doğrudan kart üzerindeki açılır sure/ayet kutularından kaldığı yeri güncelleyebilir.")
bullet("Çok Dilli Entegrasyon: Navbar üzerinde Türkçe ve Arapça dil değişim butonu bulunur. Arapça seçildiğinde sayfa düzeni otomatik olarak sağdan sola (RTL) geçer.")

heading2("10.2.3 Ortaklaşa Hatim Takip Paneli (Group Khatma Dashboard)")
body("Kullanıcının üst menüden 'Ortak Hatimler' sekmesine tıklayarak eriştiği bu panel, işbirlikçi Kur'an hatimlerinin yönetildiği alandır. Aşağıda, yeni bir grup hatmi oluşturma formu ve mevcut hatimlerin durum kartları sunulmuştur:")

# Insert Group Dashboard Screenshot
group_dash_path = os.path.join(base_path, "frontend", "src", "assets", "group_khatma_dashboard.png")
if os.path.exists(group_dash_path):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run()
    r.add_picture(group_dash_path, width=Cm(15.5))
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(8)
    r = p.add_run("Şekil 3: Kur'an Hatim Takip Uygulaması - Ortak Hatim Kontrol Paneli")
    r.font.size = Pt(10)
    r.font.color.rgb = GRAY
else:
    body("[Ortak Hatim Paneli Görseli: frontend/src/assets/group_khatma_dashboard.png bulunamadı]")

heading2("10.2.4 Ortak Hatim Cüz Rezervasyon ve Yönetim Ekranı")
body("Bu ekran, grup hatminin en dinamik ve işbirlikçi kısmıdır. 30 cüzün tamamı interaktif bir ızgara (grid) şeklinde listelenir. Aşağıda cüz dağılımları ve katılımcı listesinin ekran görüntüsü sunulmuştur:")

# Insert Group Juz Detail Screenshot
group_juz_path = os.path.join(base_path, "frontend", "src", "assets", "group_juz_detail.png")
if os.path.exists(group_juz_path):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run()
    r.add_picture(group_juz_path, width=Cm(15.5))
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(8)
    r = p.add_run("Şekil 4: Kur'an Hatim Takip Uygulaması - Grup Hatmi Cüz Yönetim Ekranı")
    r.font.size = Pt(10)
    r.font.color.rgb = GRAY
else:
    body("[Cüz Detay Görseli: frontend/src/assets/group_juz_detail.png bulunamadı]")

heading3("Özellik ve Fonksiyon Analizi:")
bullet("30 Cüz Izgarası: Her cüz kutusu kendi durumuna göre (Seçilebilir, Kilitli veya Okundu) renk alır. Boş cüzler seçilip tek tıkla rezerve edilebilir.")
bullet("Gizli Katılım (Anonymous Mode): Kullanıcı cüz seçerken 'Gizli Katıl' kutusunu işaretlerse, cüz kartında adı gizlenerek 'Anonymous' olarak kilitlenir.")
bullet("Oku ve Tamamla Butonları: Cüz rezerve eden kullanıcı kartın üstünde beliren yeşil 'Oku' butonuyla doğrudan JuzReader'a geçiş yapabilir.")
bullet("Katılımcı İlerlemeleri: Sağdaki yan panelde, hatme katılan her kişinin cüz rezerve etme ve okuma oranları dinamik olarak hesaplanarak listelenir.")

page_break()

# ═══════════════════════════════════════════════════
#  BÖLÜM 11: SONUÇ VE DEĞERLENDİRME
# ═══════════════════════════════════════════════════
heading1("11. Sonuç ve Değerlendirme")

heading2("11.1 Proje Çıktıları ve Başarı Durumu")
add_info_box(
    "Final Dönemi İtibariyle Çalışan Özellikler",
    [
        "• Kullanıcı kaydı, girişi ve JWT tabanlı oturum yönetimi",
        "• Bireysel hatim takibi ve 6236 ayet üzerinden ilerleme hesaplama",
        "• Sure ve ayet seçimi ile ilerleme güncelleme",
        "• Kur'an okuyucu ekranı (api.alquran.cloud entegrasyonu)",
        "• Grup Hatmi oluşturma, 30 cüzün paylaşılarak kilitlenmesi ve rezervasyonu",
        "• Gizli Katılımcı (Anonymous) cüz tamamlama modu",
        "• Cüz okuma (JuzReader) bileşeni ve cüz bazlı okuma tamamlama",
        "• Türkçe/Arapça çok dilli destek ve otomatik RTL düzeni"
    ],
    'E2EFDA',
    '2E7D32'
)

body("Geliştirilen sistem, başlangıçta hedeflenen tüm isterleri başarıyla yerine getirmektedir. Ayrık katmanlı (React + Node.js + SQLite) mimarisi sayesinde projenin performansı ve bakımı son derece kolaydır.")

heading2("11.2 Edinilen Teknik Kazanımlar")
bullet("React.js bileşen mimarisi ve Context API ile global durum yönetimi.")
bullet("Express.js ile RESTful API standartlarına uygun endpoint tasarımı.")
bullet("SQLite ilişkisel şemalarında UNIQUE kısıtları ve transaction yönetimi.")
bullet("Axios interceptor'ları ile istemci tarafında kimlik doğrulama hatalarını yönetme.")
bullet("i18next kütüphanesi ile çok dilli ve RTL/LTR yönelimli arayüzler geliştirme.")

page_break()

# ═══════════════════════════════════════════════════
#  BÖLÜM 12: KAYNAKÇA
# ═══════════════════════════════════════════════════
heading1("12. Kaynakça")
references = [
    "1. React Resmi Dokümantasyonu. (2024). React – A JavaScript library for building user interfaces. Meta Open Source. https://react.dev",
    "2. Node.js Foundation. (2024). Node.js v22 Documentation. OpenJS Foundation. https://nodejs.org/docs",
    "3. Express.js Team. (2024). Express – Fast, unopinionated, minimalist web framework for Node.js. https://expressjs.com",
    "4. Vite Team. (2024). Vite – Next Generation Frontend Tooling. https://vitejs.dev",
    "5. i18next Team. (2024). i18next – Internationalization-framework. https://www.i18next.com",
    "6. AlQuran Cloud. (2024). AlQuran Cloud API – Open source Quran RESTful API. https://alquran.cloud/api",
    "7. SQLite Consortium. (2024). SQLite – A C-language library that implements a small, fast, self-contained SQL database engine. https://www.sqlite.org",
    "8. Auth0. (2024). JSON Web Tokens – Introduction to JWT. https://jwt.io/introduction",
    "9. Google Fonts. (2024). Amiri – A Classical Arabic Typeface. https://fonts.google.com/specimen/Amiri",
    "10. MDN Web Docs. (2024). Cross-Origin Resource Sharing (CORS). Mozilla Developer Network. https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS"
]
for ref in references:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r = p.add_run(ref)
    r.font.size = Pt(10)

doc.add_paragraph()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Kur'an Hatim Takip Web Uygulaması  |  Haziran 2026")
r.font.size = Pt(9); r.font.color.rgb = GRAY

# ═══════════════════════════════════════════════════
#  KAYDET
# ═══════════════════════════════════════════════════
out = os.path.join(base_path, "Proje_Raporu.docx")
doc.save(out)
print(f"Word dosyasi basariyla olusturuldu: {out}")
